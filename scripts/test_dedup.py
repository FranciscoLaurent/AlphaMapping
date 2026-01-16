"""
Test script to verify upsert functionality
Creates duplicate test data and verifies only one record is kept
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import get_db
from app.models.models import Asset
import datetime

def test_upsert():
    print("="*60)
    print("Testing IP:Port Deduplication")
    print("="*60)
    
    db = next(get_db())
    
    # Test data
    test_ip = "192.168.1.100"
    test_port = 8080
    
    try:
        # Clean up any existing test data
        db.query(Asset).filter(
            Asset.ip == test_ip,
            Asset.port == test_port
        ).delete()
        db.commit()
        
        print(f"\n1. Creating first asset: {test_ip}:{test_port}")
        asset1 = Asset(
            ip=test_ip,
            port=test_port,
            protocol="http",
            title="First Entry",
            country="CN",
            platform="test"
        )
        db.add(asset1)
        db.commit()
        db.refresh(asset1)
        print(f"   Created with ID: {asset1.id}, Title: '{asset1.title}'")
        
        # Try to insert duplicate
        print(f"\n2. Attempting to insert duplicate {test_ip}:{test_port}")
        try:
            asset2 = Asset(
                ip=test_ip,
                port=test_port,
                protocol="https",
                title="Duplicate Entry",
                country="US",
                platform="test"
            )
            db.add(asset2)
            db.commit()
            print("   ❌ FAILED: Duplicate was inserted (constraint not working)")
        except Exception as e:
            db.rollback()
            print(f"   ✓ PASSED: Duplicate rejected by unique constraint")
            print(f"   Error: {str(e)[:100]}")
        
        # Test update scenario
        print(f"\n3. Testing update of existing asset")
        existing = db.query(Asset).filter(
            Asset.ip == test_ip,
            Asset.port == test_port
        ).first()
        
        if existing:
            old_title = existing.title
            existing.title = "Updated Entry"
            existing.last_seen = datetime.datetime.utcnow()
            db.commit()
            print(f"   ✓ PASSED: Asset updated")
            print(f"   Old title: '{old_title}' -> New title: '{existing.title}'")
        
        # Verify only one record exists
        print(f"\n4. Verifying only one record exists for {test_ip}:{test_port}")
        count = db.query(Asset).filter(
            Asset.ip == test_ip,
            Asset.port == test_port
        ).count()
        
        if count == 1:
            print(f"   ✓ PASSED: Exactly 1 record found")
        else:
            print(f"   ❌ FAILED: Found {count} records (expected 1)")
        
        # Cleanup
        print(f"\n5. Cleaning up test data...")
        db.query(Asset).filter(
            Asset.ip == test_ip,
            Asset.port == test_port
        ).delete()
        db.commit()
        print("   ✓ Test data removed")
        
        print("\n" + "="*60)
        print("✓ All tests completed")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_upsert()
