"""
Diagnostic script to test the entire data pipeline from FOFA API to database
Run this to check if data is flowing correctly through the system.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.fofa import FofaPlatform
from app.models.models import Asset, PlatformQuery
from app.core.database import get_db, engine
from app.models.models import Base

async def test_fofa_api():
    print("\n=== Testing FOFA API ===")
    fofa = FofaPlatform()
    
    if not fofa.email or not fofa.key:
        print("❌ FOFA credentials not configured in .env")
        return None
    
    print(f"✓ FOFA Email: {fofa.email}")
    print(f"✓ FOFA Key: {'*' * 20}")
    
    # Test with a simple query
    test_query = "title=\"Apache\""
    print(f"\nTesting query: {test_query}")
    
    try:
        results = await fofa.query(test_query, size=3)
        print(f"✓ Received {len(results)} results from FOFA")
        
        if len(results) > 0:
            print("\n--- Sample Result (Full Dict) ---")
            import json
            first_result = results[0]
            print(json.dumps(first_result, indent=2, ensure_ascii=False))
            
            print("\n--- Field-by-Field Analysis ---")
            for key, value in first_result.items():
                print(f"  {key:15} = {repr(value):50} (type: {type(value).__name__})")
            
            # Check field presence
            required_fields = ['ip', 'port', 'protocol', 'domain', 'host', 'title', 'server', 'country', 'city', 'org']
            missing_fields = [f for f in required_fields if f not in first_result]
            if missing_fields:
                print(f"\n⚠️ Missing fields: {missing_fields}")
            else:
                print("\n✓ All required fields present")
        
        return results
    except Exception as e:
        print(f"❌ FOFA API Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_database_write(test_data):
    print("\n=== Testing Database Write ===")
    
    if not test_data or len(test_data) == 0:
        print("⚠️ Skipping DB test (no FOFA data)")
        return
    
    from sqlalchemy.orm import Session
    db = next(get_db())
    
    try:
        # Create a test query record
        test_query_record = PlatformQuery(
            platform="fofa",
            query_string="title=\"Apache\"",
            nl_query="Test Diagnostic Query",
            results_count=len(test_data)
        )
        db.add(test_query_record)
        db.commit()
        db.refresh(test_query_record)
        print(f"✓ Created PlatformQuery record (ID: {test_query_record.id})")
        
        # Save first result as asset
        item = test_data[0]
        asset = Asset(
            **item,
            platform="fofa",
            query_id=test_query_record.id,
            raw_data=item
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        
        print(f"✓ Saved Asset (ID: {asset.id})")
        print(f"  IP: {asset.ip}, Port: {asset.port}")
        print(f"  Title: {asset.title}")
        print(f"  Country: {asset.country}")
        
        # Verify we can read it back
        retrieved = db.query(Asset).filter(Asset.id == asset.id).first()
        if retrieved:
            print("✓ Successfully retrieved asset from DB")
            print(f"  Raw Data Type: {type(retrieved.raw_data)}")
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def test_database_read():
    print("\n=== Testing Database Read ===")
    db = next(get_db())
    
    try:
        total_assets = db.query(Asset).count()
        total_queries = db.query(PlatformQuery).count()
        
        print(f"Total Assets in DB: {total_assets}")
        print(f"Total Queries in DB: {total_queries}")
        
        if total_assets > 0:
            sample = db.query(Asset).first()
            print(f"\n--- Sample Asset from DB ---")
            print(f"IP: {sample.ip}")
            print(f"Port: {sample.port}")
            print(f"Title: {sample.title}")
            print(f"Server: {sample.server}")
            print(f"Country: {sample.country}")
            print(f"Has raw_data: {sample.raw_data is not None}")
        
    except Exception as e:
        print(f"❌ Read Error: {e}")
    finally:
        db.close()

async def main():
    print("=" * 60)
    print("AlphaMapping Data Pipeline Diagnostic Tool")
    print("=" * 60)
    
    # Step 1: Test FOFA API
    fofa_results = await test_fofa_api()
    
    # Step 2: Test Database Write
    if fofa_results:
        test_database_write(fofa_results)
    
    # Step 3: Test Database Read
    test_database_read()
    
    print("\n" + "=" * 60)
    print("Diagnostic Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
