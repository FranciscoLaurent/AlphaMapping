"""
Cleanup script to remove corrupted/null assets from database
"""
import sqlite3
import os

DB_PATH = "data/alpha_mapping.db"

def cleanup_database():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Cleaning up database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Count null assets
        cursor.execute("SELECT COUNT(*) FROM assets WHERE ip IS NULL OR ip = ''")
        null_count = cursor.fetchone()[0]
        
        print(f"Found {null_count} corrupted assets (NULL IP)")
        
        if null_count > 0:
            # Delete null assets
            cursor.execute("DELETE FROM assets WHERE ip IS NULL OR ip = ''")
            conn.commit()
            print(f"✓ Deleted {null_count} corrupted assets")
        
        # Count remaining
        cursor.execute("SELECT COUNT(*) FROM assets")
        remaining = cursor.fetchone()[0]
        print(f"Remaining assets: {remaining}")
        
    except Exception as e:
        print(f"Cleanup failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_database()
