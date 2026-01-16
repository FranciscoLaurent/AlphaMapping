"""Test configuration loading"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.config import settings, ENV_FILE
from pathlib import Path

print("=" * 60)
print("Configuration Loading Test")
print("=" * 60)

print(f"\nENV_FILE path: {ENV_FILE}")
print(f"ENV_FILE exists: {Path(ENV_FILE).exists()}")

print("\n--- Loaded Settings ---")
print(f"FOFA_EMAIL: {settings.FOFA_EMAIL}")
print(f"FOFA_KEY: {settings.FOFA_KEY}")
print(f"OPENAI_API_KEY: {settings.OPENAI_API_KEY[:20] if settings.OPENAI_API_KEY else 'NOT SET'}...")
print(f"DATABASE_URL: {settings.DATABASE_URL}")

if Path(ENV_FILE).exists():
    print("\n--- .env File Content ---")
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        # Show only first 500 chars for security
        print(content[:500])
else:
    print("\n❌ .env file not found!")

print("\n" + "=" * 60)
