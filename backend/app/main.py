from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from .core.config import settings
from .models.models import Base, PlatformQuery, Asset, SecurityReport
from .models.scheduled_task import ScheduledTask
from .core.database import engine, get_db, SessionLocal
from .services.fofa import FofaPlatform
from .services.zoomeye import ZoomEyePlatform
from .services.agent import AgentService
from .services.geolocation import GeoLocationService
from .services.report_generator import ReportGenerator
from .services.scheduler import scheduler_service, execute_scheduled_query
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
import datetime
import logging
from pathlib import Path
from functools import partial

logger = logging.getLogger(__name__)

# Create tables (include ScheduledTask)
Base.metadata.create_all(bind=engine)
ScheduledTask.__table__.create(bind=engine, checkfirst=True)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # True + origins=["*"] = 任意网站可携带凭证发请求（会话劫持）
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    nl_query: str
    platform: Literal['fofa', 'zoomeye'] = Field(..., description="查询平台")
    use_cache: bool = True

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.APP_NAME} API"}

@app.post("/query")
async def query_assets(request: QueryRequest, db: Session = Depends(get_db)):
    agent = AgentService()
    
    # 1. Check Cache
    if request.use_cache:
        cached_query = db.query(PlatformQuery).filter(
            PlatformQuery.nl_query == request.nl_query,
            PlatformQuery.platform == request.platform
        ).first()
        if cached_query:
            return {
                "source": "cache",
                "query_id": cached_query.id,
                "query": cached_query.query_string,
                "results": [
                    {
                        "ip": a.ip, "port": a.port, "protocol": a.protocol,
                        "domain": a.domain, "host": a.host, "title": a.title,
                        "server": a.server, "country": a.country, "city": a.city,
                        "org": a.org
                    } for a in cached_query.assets
                ]
            }

    # 2. Translate NL to CSEQL
    try:
        query_string = agent.translate_nl_to_cseql(request.nl_query, request.platform)
    except Exception as e:
        logger.error("LLM translation failed: %s", e)
        raise HTTPException(status_code=500, detail="查询翻译失败，请稍后重试")

    # 2. Check Cache
    cached_query = db.query(PlatformQuery).filter(
        PlatformQuery.platform == request.platform,
        PlatformQuery.query_string == query_string
    ).order_by(PlatformQuery.created_at.desc()).first()

    if cached_query:
        logger.info(f"Cache hit for query: {query_string}")
        # Return cached results
        # Assuming asset data structure in DB matches what frontend expects
        cached_assets = []
        for asset in cached_query.assets:
             cached_assets.append({
                "ip": asset.ip,
                "port": asset.port,
                "protocol": asset.protocol,
                "domain": asset.domain,
                "host": asset.host,
                "title": asset.title,
                "server": asset.server,
                "country": asset.country,
                "city": asset.city,
                "org": asset.org,
                "raw_data": asset.raw_data
             })
             
        # Refresh last seen for these assets? Optional. 
        # For now just return
        return {
            "source": "cache",
            "query_id": cached_query.id,
            "query": query_string,
            "results": cached_assets
        }

    # 3. Pull from Platform (Cache Miss)
    platform_svc = FofaPlatform() if request.platform == 'fofa' else ZoomEyePlatform()
    try:
        results = await platform_svc.query(query_string)
    except Exception as e:
        logger.error("Platform query failed: %s", e)
        raise HTTPException(status_code=502, detail="平台查询失败，请检查查询条件或稍后重试")

    # 4. Get geolocation for new assets
    geo_service = GeoLocationService()
    ips = [item.get('ip') for item in results if item.get('ip')]
    coords = await geo_service.batch_get_coordinates(ips)
    
    # 5. Save to Database with Upsert Logic
    new_query = PlatformQuery(
        platform=request.platform,
        query_string=query_string,
        nl_query=request.nl_query,
        results_count=len(results)
    )
    db.add(new_query)
    db.commit()
    db.refresh(new_query)

    updated_count = 0
    created_count = 0
    
    for item in results:
        ip = item.get('ip')
        port = item.get('port')
        
        if not ip or not port:
            continue  # Skip invalid entries
        
        lat, lon = coords.get(ip, (None, None)) if ip else (None, None)
        
        # Check if asset already exists
        existing_asset = db.query(Asset).filter(
            Asset.ip == ip,
            Asset.port == port
        ).first()
        
        if existing_asset:
            # Update existing asset with new data
            for key, value in item.items():
                if hasattr(existing_asset, key) and value is not None:
                    setattr(existing_asset, key, value)
            
            existing_asset.last_seen = datetime.datetime.utcnow()
            existing_asset.platform = request.platform
            existing_asset.raw_data = item
            
            # Update geolocation if we have new coordinates
            if lat and lon:
                existing_asset.latitude = lat
                existing_asset.longitude = lon
                
            updated_count += 1
        else:
            # Create new asset
            asset = Asset(
                **item,
                platform=request.platform,
                query_id=new_query.id,
                raw_data=item,
                latitude=lat,
                longitude=lon
            )
            db.add(asset)
            created_count += 1
    
    db.commit()
    
    logger.info(f"Created {created_count} new assets, updated {updated_count} existing assets")

    return {
        "source": "api",
        "query_id": new_query.id,
        "query": query_string,
        "results": results
    }

@app.post("/analyze")
async def analyze_assets(query_id: int, db: Session = Depends(get_db)):
    query = db.query(PlatformQuery).filter(PlatformQuery.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    assets = [
        {
            "ip": a.ip, "port": a.port, "protocol": a.protocol,
            "domain": a.domain, "host": a.host, "title": a.title,
            "server": a.server, "country": a.country, "city": a.city,
            "org": a.org
        } for a in query.assets
    ]
    
    agent = AgentService()
    report_data = agent.generate_security_report(assets)
    
    # Generate and save report files
    report_gen = ReportGenerator()
    
    report = SecurityReport(
        query_id=query.id,
        content=report_data['content'],
        summary=report_data['summary'],
        risk_level=report_data['risk_level']
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Save report files
    try:
        md_path = report_gen.save_as_markdown(report_data['content'], report.id)
        pdf_path = report_gen.save_as_pdf(report_data['content'], report.id, report_data['summary'])
        report.file_path = md_path  # Store markdown path as primary
        db.commit()
        logger.info(f"Saved report files: {md_path}, {pdf_path}")
    except Exception as e:
        logger.error(f"Failed to save report files: {e}")
    
    return report

@app.get("/queries")
def get_queries(db: Session = Depends(get_db)):
    return db.query(PlatformQuery).order_by(PlatformQuery.id.desc()).all()

@app.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    return db.query(SecurityReport).order_by(SecurityReport.id.desc()).all()

@app.delete("/clear-history")
def clear_history(db: Session = Depends(get_db)):
    """Clear all query history and reports, but keep assets."""
    try:
        # Delete all reports
        reports_count = db.query(SecurityReport).count()
        db.query(SecurityReport).delete()
        
        # Delete all queries
        queries_count = db.query(PlatformQuery).count()
        db.query(PlatformQuery).delete()
        
        db.commit()
        
        logger.info(f"Cleared {queries_count} queries and {reports_count} reports")
        
        return {
            "success": True,
            "message": f"已清除 {queries_count} 条查询历史和 {reports_count} 份报告",
            "queries_deleted": queries_count,
            "reports_deleted": reports_count
        }
    except Exception as e:
        db.rollback()
        logger.error("Failed to clear history: %s", e)
        raise HTTPException(status_code=500, detail="清除历史记录失败")

@app.get("/assets/recent")
def get_recent_assets(limit: int = 100, db: Session = Depends(get_db)):
    """Get the most recent assets added to the database."""
    assets = db.query(Asset).order_by(Asset.id.desc()).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "ip": a.ip, "port": a.port, "protocol": a.protocol,
            "domain": a.domain, "host": a.host, "title": a.title,
            "server": a.server, "country": a.country, "city": a.city,
            "org": a.org, "raw_data": a.raw_data
        } for a in assets
    ]

@app.get("/assets")
def get_assets(
    port: Optional[int] = None,
    protocol: Optional[str] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get assets with filtering and pagination.
    
    - **port**: Filter by port number
    - **protocol**: Filter by protocol (http, https, ssh, etc.)
    - **country**: Filter by country
    - **city**: Filter by city
    - **keyword**: Search in IP, title, domain, host
    - **page**: Page number (1-indexed)
    - **page_size**: Items per page (max 200)
    """
    query = db.query(Asset)
    
    # Apply filters
    if port:
        query = query.filter(Asset.port == port)
    if protocol:
        query = query.filter(Asset.protocol.ilike(f"%{protocol}%"))
    if country:
        query = query.filter(Asset.country.ilike(f"%{country}%"))
    if city:
        query = query.filter(Asset.city.ilike(f"%{city}%"))
    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            (Asset.ip.ilike(keyword_filter)) |
            (Asset.title.ilike(keyword_filter)) |
            (Asset.domain.ilike(keyword_filter)) |
            (Asset.host.ilike(keyword_filter))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    page_size = min(page_size, 200)  # Max 200 per page
    offset = (page - 1) * page_size
    assets = query.order_by(Asset.id.desc()).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "data": [
            {
                "id": a.id,
                "ip": a.ip, "port": a.port, "protocol": a.protocol,
                "domain": a.domain, "host": a.host, "title": a.title,
                "server": a.server, "country": a.country, "city": a.city,
                "org": a.org, "last_seen": a.last_seen.isoformat() if a.last_seen else None
            } for a in assets
        ]
    }

@app.get("/assets/export")
def export_assets(
    format: str = "csv",
    port: Optional[int] = None,
    protocol: Optional[str] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Export assets to file.
    
    - **format**: Export format (csv, excel, json)
    - Other parameters: Same filters as /assets
    """
    from fastapi.responses import Response
    from .services.exporter import AssetExporter
    
    query = db.query(Asset)
    
    # Apply same filters
    if port:
        query = query.filter(Asset.port == port)
    if protocol:
        query = query.filter(Asset.protocol.ilike(f"%{protocol}%"))
    if country:
        query = query.filter(Asset.country.ilike(f"%{country}%"))
    if city:
        query = query.filter(Asset.city.ilike(f"%{city}%"))
    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            (Asset.ip.ilike(keyword_filter)) |
            (Asset.title.ilike(keyword_filter)) |
            (Asset.domain.ilike(keyword_filter)) |
            (Asset.host.ilike(keyword_filter))
        )
    
    assets = query.order_by(Asset.id.desc()).limit(10000).all()  # Max 10k for export
    filename = AssetExporter.get_filename(format)
    
    if format == "csv":
        content = AssetExporter.to_csv(assets)
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    elif format == "excel":
        content = AssetExporter.to_excel(assets)
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    elif format == "json":
        content = AssetExporter.to_json(assets)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

@app.get("/asset/{asset_id}")
def get_asset_detail(asset_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a single asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return {
        "id": asset.id,
        "ip": asset.ip,
        "port": asset.port,
        "protocol": asset.protocol,
        "domain": asset.domain,
        "host": asset.host,
        "title": asset.title,
        "server": asset.server,
        "country": asset.country,
        "city": asset.city,
        "org": asset.org,
        "latitude": asset.latitude,
        "longitude": asset.longitude,
        "platform": asset.platform,
        "last_seen": asset.last_seen,
        "raw_data": asset.raw_data
    }

@app.post("/analyze-asset/{asset_id}")
async def analyze_asset(asset_id: int, db: Session = Depends(get_db)):
    """Analyze a single asset using AI."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Prepare asset data
    asset_data = {
        "ip": asset.ip,
        "port": asset.port,
        "protocol": asset.protocol,
        "domain": asset.domain,
        "host": asset.host,
        "title": asset.title,
        "server": asset.server,
        "country": asset.country,
        "city": asset.city,
        "org": asset.org
    }
    
    # Analyze with AI
    agent = AgentService()
    try:
        analysis = agent.analyze_single_asset(asset_data)
        logger.info(f"Analyzed asset {asset_id}: {analysis.get('risk_level', 'Unknown')}")
        return analysis
    except Exception as e:
        logger.error("Failed to analyze asset %s: %s", asset_id, e)
        raise HTTPException(status_code=500, detail="资产分析失败，请稍后重试")

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get aggregated statistics for visualization."""

    total_assets = db.query(func.count(Asset.id)).scalar() or 0

    if total_assets == 0:
        return {
            "total_assets": 0,
            "geo_distribution": [],
            "port_distribution": {},
            "protocol_distribution": {},
            "country_distribution": {}
        }

    # Geographic distribution — 用 SQL 过滤，避免全表加载到内存
    geo_rows = db.query(
        Asset.country, Asset.city, Asset.ip,
        Asset.longitude, Asset.latitude
    ).filter(
        Asset.latitude.isnot(None), Asset.longitude.isnot(None)
    ).all()

    geo_data = [
        {
            "name": r.country or "Unknown",
            "value": [float(r.longitude), float(r.latitude), 1],
            "ip": r.ip,
            "city": r.city
        }
        for r in geo_rows
    ]

    # Port distribution
    port_stats = db.query(
        Asset.port, func.count(Asset.id)
    ).group_by(Asset.port).order_by(func.count(Asset.id).desc()).limit(10).all()
    port_distribution = {str(port): count for port, count in port_stats if port}

    # Protocol distribution
    protocol_stats = db.query(
        Asset.protocol, func.count(Asset.id)
    ).group_by(Asset.protocol).all()
    protocol_distribution = {proto or "unknown": count for proto, count in protocol_stats}

    # Country distribution
    country_stats = db.query(
        Asset.country, func.count(Asset.id)
    ).group_by(Asset.country).order_by(func.count(Asset.id).desc()).limit(10).all()
    country_distribution = {country or "Unknown": count for country, count in country_stats}

    return {
        "total_assets": total_assets,
        "geo_distribution": geo_data,
        "port_distribution": port_distribution,
        "protocol_distribution": protocol_distribution,
        "country_distribution": country_distribution
    }

@app.get("/download/report/{report_id}")
def download_report(report_id: int, format: str = "markdown", db: Session = Depends(get_db)):
    """Download a security report in specified format."""
    report = db.query(SecurityReport).filter(SecurityReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report_gen = ReportGenerator()
    
    try:
        if format.lower() == "pdf":
            # Generate PDF if not exists or regenerate
            pdf_path = report_gen.save_as_pdf(report.content, report.id, report.summary)
            if not Path(pdf_path).exists():
                raise HTTPException(status_code=404, detail="PDF file not found")
            return FileResponse(
                path=pdf_path,
                filename=Path(pdf_path).name,
                media_type="application/pdf"
            )
        else:
            # Default to Markdown
            if report.file_path and Path(report.file_path).exists():
                md_path = report.file_path
            else:
                md_path = report_gen.save_as_markdown(report.content, report.id)
            
            return FileResponse(
                path=md_path,
                filename=Path(md_path).name,
                media_type="text/markdown"
            )
    except Exception as e:
        logger.error("Error downloading report: %s", e)
        raise HTTPException(status_code=500, detail="报告文件生成失败")

# ============ Scheduled Tasks API ============

class ScheduledTaskCreate(BaseModel):
    name: str
    nl_query: str
    platform: Literal['fofa', 'zoomeye']
    cron_expression: str  # e.g., "0 2 * * *" for 2am daily

class ScheduledTaskUpdate(BaseModel):
    name: Optional[str] = None
    nl_query: Optional[str] = None
    platform: Optional[Literal['fofa', 'zoomeye']] = None
    cron_expression: Optional[str] = None
    is_active: Optional[bool] = None

@app.get("/scheduled-tasks")
def get_scheduled_tasks(db: Session = Depends(get_db)):
    """Get all scheduled tasks."""
    tasks = db.query(ScheduledTask).order_by(ScheduledTask.id.desc()).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "nl_query": t.nl_query,
            "platform": t.platform,
            "cron_expression": t.cron_expression,
            "is_active": t.is_active,
            "last_run": t.last_run.isoformat() if t.last_run else None,
            "next_run": t.next_run.isoformat() if t.next_run else None,
            "run_count": t.run_count,
            "success_count": t.success_count,
            "last_result": t.last_result,
            "created_at": t.created_at.isoformat() if t.created_at else None
        } for t in tasks
    ]

@app.post("/scheduled-tasks")
def create_scheduled_task(task: ScheduledTaskCreate, db: Session = Depends(get_db)):
    """Create a new scheduled task."""
    new_task = ScheduledTask(
        name=task.name,
        nl_query=task.nl_query,
        platform=task.platform,
        cron_expression=task.cron_expression
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # Register with scheduler
    scheduler_service.add_task(
        task_id=new_task.id,
        cron_expression=task.cron_expression,
        job_func=partial(execute_scheduled_query, task_id=new_task.id, db_session_factory=SessionLocal)
    )
    
    # Update next run time
    new_task.next_run = scheduler_service.get_next_run_time(new_task.id)
    db.commit()
    
    return {"id": new_task.id, "message": "Task created successfully"}

@app.put("/scheduled-tasks/{task_id}")
def update_scheduled_task(task_id: int, task: ScheduledTaskUpdate, db: Session = Depends(get_db)):
    """Update a scheduled task."""
    db_task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update fields
    if task.name is not None:
        db_task.name = task.name
    if task.nl_query is not None:
        db_task.nl_query = task.nl_query
    if task.platform is not None:
        db_task.platform = task.platform
    if task.cron_expression is not None:
        db_task.cron_expression = task.cron_expression
        # Re-register with new cron
        scheduler_service.add_task(
            task_id=task_id,
            cron_expression=task.cron_expression,
            job_func=partial(execute_scheduled_query, task_id=task_id, db_session_factory=SessionLocal)
        )
    if task.is_active is not None:
        db_task.is_active = task.is_active
        if task.is_active:
            scheduler_service.resume_task(task_id)
        else:
            scheduler_service.pause_task(task_id)
    
    db_task.next_run = scheduler_service.get_next_run_time(task_id)
    db.commit()
    
    return {"message": "Task updated successfully"}

@app.delete("/scheduled-tasks/{task_id}")
def delete_scheduled_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a scheduled task."""
    db_task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    scheduler_service.remove_task(task_id)
    db.delete(db_task)
    db.commit()
    
    return {"message": "Task deleted successfully"}

@app.post("/scheduled-tasks/{task_id}/run")
async def run_scheduled_task(task_id: int, db: Session = Depends(get_db)):
    """Manually trigger a scheduled task."""
    db_task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Run the task immediately
    await execute_scheduled_query(task_id=task_id, db_session_factory=SessionLocal)
    
    return {"message": f"Task '{db_task.name}' executed"}

# ============ Scheduler Lifecycle ============

@app.on_event("startup")
async def startup_event():
    """Start scheduler and load existing tasks."""
    logger.info("Starting scheduler...")
    scheduler_service.start()
    
    # Load existing active tasks
    db = SessionLocal()
    try:
        tasks = db.query(ScheduledTask).filter(ScheduledTask.is_active == True).all()
        for task in tasks:
            scheduler_service.add_task(
                task_id=task.id,
                cron_expression=task.cron_expression,
                job_func=partial(execute_scheduled_query, task_id=task.id, db_session_factory=SessionLocal)
            )
            task.next_run = scheduler_service.get_next_run_time(task.id)
        db.commit()
        logger.info(f"Loaded {len(tasks)} scheduled tasks")
    finally:
        db.close()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop scheduler on shutdown."""
    logger.info("Stopping scheduler...")
    scheduler_service.stop()
