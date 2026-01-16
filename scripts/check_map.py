"""Check if geolocation data exists and stats endpoint works"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import get_db
from app.models.models import Asset
import requests

print("=" * 60)
print("Map Display Diagnostic")
print("=" * 60)

# 1. Check database for lat/lon
db = next(get_db())
assets_with_coords = db.query(Asset).filter(
    Asset.latitude.isnot(None),
    Asset.longitude.isnot(None)
).all()

print(f"\n1. Assets with coordinates in DB: {len(assets_with_coords)}")
if assets_with_coords:
    sample = assets_with_coords[0]
    print(f"   Sample: IP={sample.ip}, Lat={sample.latitude}, Lon={sample.longitude}")

# 2. Check total assets
total = db.query(Asset).count()
print(f"   Total assets: {total}")

# 3. Check stats endpoint
print("\n2. Testing /stats endpoint...")
try:
    response = requests.get("http://localhost:8000/stats", timeout=5)
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✓ Stats endpoint accessible")
        print(f"   Total assets: {stats.get('total_assets')}")
        print(f"   Geo distribution points: {len(stats.get('geo_distribution', []))}")
        
        if stats.get('geo_distribution'):
            print("\n   Sample geo point:")
            print(f"   {stats['geo_distribution'][0]}")
    else:
        print(f"   ❌ Stats endpoint returned {response.status_code}")
except Exception as e:
    print(f"   ❌ Failed to call stats endpoint: {e}")

db.close()
print("\n" + "=" * 60)
