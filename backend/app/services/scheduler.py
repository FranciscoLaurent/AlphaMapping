"""
APScheduler-based task scheduler for AlphaMapping.
Handles scheduled data pulling from FOFA/ZoomEye.
"""
import logging
from datetime import datetime
from typing import Optional, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class SchedulerService:
    """Manages scheduled tasks for data pulling."""
    
    _instance: Optional['SchedulerService'] = None
    _scheduler: Optional[AsyncIOScheduler] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._scheduler is None:
            self._scheduler = AsyncIOScheduler(
                jobstores={'default': MemoryJobStore()},
                timezone='Asia/Shanghai'
            )
    
    @property
    def scheduler(self) -> AsyncIOScheduler:
        return self._scheduler
    
    def start(self):
        """Start the scheduler."""
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        if self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("Scheduler stopped")
    
    def add_task(
        self,
        task_id: int,
        cron_expression: str,
        job_func: Callable,
        **kwargs
    ) -> bool:
        """
        Add a scheduled task.
        
        Args:
            task_id: Database task ID
            cron_expression: Cron expression (e.g., "0 2 * * *")
            job_func: Async function to execute
            **kwargs: Arguments to pass to job_func
            
        Returns:
            True if successful, False otherwise
        """
        job_id = f"task_{task_id}"
        
        try:
            # Parse cron expression
            trigger = CronTrigger.from_crontab(cron_expression)
            
            # Remove existing job if any
            if self._scheduler.get_job(job_id):
                self._scheduler.remove_job(job_id)
            
            # Add new job
            self._scheduler.add_job(
                job_func,
                trigger=trigger,
                id=job_id,
                kwargs=kwargs,
                replace_existing=True
            )
            
            logger.info(f"Added scheduled task {job_id} with cron: {cron_expression}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add task {job_id}: {e}")
            return False
    
    def remove_task(self, task_id: int) -> bool:
        """Remove a scheduled task."""
        job_id = f"task_{task_id}"
        try:
            if self._scheduler.get_job(job_id):
                self._scheduler.remove_job(job_id)
                logger.info(f"Removed scheduled task {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove task {job_id}: {e}")
            return False
    
    def pause_task(self, task_id: int) -> bool:
        """Pause a scheduled task."""
        job_id = f"task_{task_id}"
        try:
            self._scheduler.pause_job(job_id)
            logger.info(f"Paused scheduled task {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pause task {job_id}: {e}")
            return False
    
    def resume_task(self, task_id: int) -> bool:
        """Resume a paused task."""
        job_id = f"task_{task_id}"
        try:
            self._scheduler.resume_job(job_id)
            logger.info(f"Resumed scheduled task {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resume task {job_id}: {e}")
            return False
    
    def get_next_run_time(self, task_id: int) -> Optional[datetime]:
        """Get next scheduled run time for a task."""
        job_id = f"task_{task_id}"
        job = self._scheduler.get_job(job_id)
        if job:
            return job.next_run_time
        return None
    
    def get_all_jobs(self) -> list:
        """Get all scheduled jobs."""
        return self._scheduler.get_jobs()


# Global scheduler instance
scheduler_service = SchedulerService()


async def execute_scheduled_query(task_id: int, db_session_factory):
    """
    Execute a scheduled query task.
    
    This function is called by APScheduler when a task is due.
    """
    from .agent import AgentService
    from .fofa import FofaPlatform
    from .zoomeye import ZoomEyePlatform
    from .geolocation import GeoLocationService
    from ..models.scheduled_task import ScheduledTask
    from ..models.models import PlatformQuery, Asset
    
    logger.info(f"Executing scheduled task {task_id}")
    
    db = db_session_factory()
    try:
        # Get task details
        task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        # Translate NL to CSEQL
        agent = AgentService()
        query_string = agent.translate_nl_to_cseql(task.nl_query, task.platform)
        
        # Execute query
        platform_svc = FofaPlatform() if task.platform == 'fofa' else ZoomEyePlatform()
        results = await platform_svc.query(query_string)
        
        # Get geolocation
        geo_service = GeoLocationService()
        ips = [item.get('ip') for item in results if item.get('ip')]
        coords = await geo_service.batch_get_coordinates(ips)
        
        # Save results
        new_query = PlatformQuery(
            platform=task.platform,
            query_string=query_string,
            nl_query=task.nl_query,
            results_count=len(results)
        )
        db.add(new_query)
        db.commit()
        
        # Save assets (upsert logic)
        created = 0
        updated = 0
        for item in results:
            ip = item.get('ip')
            port = item.get('port')
            if not ip or not port:
                continue
            
            lat, lon = coords.get(ip, (None, None)) if ip else (None, None)
            
            existing = db.query(Asset).filter(
                Asset.ip == ip,
                Asset.port == port
            ).first()
            
            if existing:
                for key, value in item.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)
                existing.last_seen = datetime.utcnow()
                updated += 1
            else:
                asset = Asset(
                    **item,
                    platform=task.platform,
                    query_id=new_query.id,
                    raw_data=item,
                    latitude=lat,
                    longitude=lon
                )
                db.add(asset)
                created += 1
        
        db.commit()
        
        # Update task statistics
        task.last_run = datetime.utcnow()
        task.run_count += 1
        task.success_count += 1
        task.last_result = f"Success: {len(results)} results, {created} new, {updated} updated"
        task.next_run = scheduler_service.get_next_run_time(task_id)
        db.commit()
        
        logger.info(f"Task {task_id} completed: {task.last_result}")
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        # Update task with error
        task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
        if task:
            task.last_run = datetime.utcnow()
            task.run_count += 1
            task.last_result = f"Error: {str(e)}"
            db.commit()
    finally:
        db.close()
