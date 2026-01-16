import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.geolocation import GeoLocationService
from app.services.report_generator import ReportGenerator

async def test_geolocation():
    print("\nTesting Geolocation Service...")
    service = GeoLocationService()
    
    # Test Google DNS IP
    ip = "8.8.8.8"
    print(f"getting coordinates for {ip}...")
    lat, lon = await service.get_coordinates(ip)
    print(f"IP: {ip}, Lat: {lat}, Lon: {lon}")
    
    if lat and lon:
        print("✅ Geolocation test passed")
    else:
        print("❌ Geolocation test failed (might be network issue)")

def test_report_generation():
    print("\nTesting Report Generation...")
    generator = ReportGenerator()
    
    content = "# Test Report\n\nThis is a test report.\n\n## Section 1\nContent."
    report_id = 999
    summary = "Test Report Summary"
    
    # Test Markdown
    try:
        md_path = generator.save_as_markdown(content, report_id)
        print(f"Saved Markdown to: {md_path}")
        if os.path.exists(md_path):
            print("✅ Markdown generation passed")
        else:
            print("❌ Markdown file not found")
            
        # Cleanup
        if os.path.exists(md_path):
            os.remove(md_path)
            
    except Exception as e:
        print(f"❌ Markdown generation failed: {e}")

    # Test PDF
    try:
        pdf_path = generator.save_as_pdf(content, report_id, summary)
        print(f"Saved PDF to: {pdf_path}")
        if os.path.exists(pdf_path):
            print("✅ PDF generation passed")
        else:
            print("❌ PDF file not found")
            
        # Cleanup
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")

async def main():
    await test_geolocation()
    test_report_generation()

if __name__ == "__main__":
    asyncio.run(main())
