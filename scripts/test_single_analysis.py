"""
Test script for single asset AI analysis API
"""
import sys
import os
import requests
import json
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import get_db
from app.models.models import Asset

def test_analysis():
    print("="*60)
    print("Testing Single Asset AI Analysis")
    print("="*60)
    
    # 1. Get an existing valid asset
    db = next(get_db())
    # Filter for assets with valid IP to ensure analysis works
    asset = db.query(Asset).filter(Asset.ip.isnot(None)).first()
    db.close()
    
    if not asset:
        print("❌ No valid assets found in database to test")
        return

    print(f"Testing with Asset ID: {asset.id}")
    print(f"Asset: {asset.ip}:{asset.port} ({asset.protocol})")
    
    # 2. Call API
    url = f"http://localhost:8000/analyze-asset/{asset.id}"
    print(f"\nCalling API: {url}")
    
    try:
        response = requests.post(url)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ Analysis Successful!")
            print("-" * 30)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("-" * 30)
            
            # Verify fields
            required_fields = ['risk_level', 'summary', 'vulnerabilities', 'recommendations']
            missing = [f for f in required_fields if f not in result]
            
            if not missing:
                print("✓ All required fields present")
            else:
                print(f"❌ Missing fields: {missing}")
                
        else:
            print(f"❌ API Request Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error calling API: {e}")

if __name__ == "__main__":
    test_analysis()
