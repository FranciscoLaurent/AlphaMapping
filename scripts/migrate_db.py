import sqlite3
import os

DB_PATH = "data/alpha_mapping.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. It will be created on first run.")
        return

    print(f"Migrating database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(assets)")
    asset_columns = [info[1] for info in cursor.fetchall()]
    
    cursor.execute("PRAGMA table_info(security_reports)")
    report_columns = [info[1] for info in cursor.fetchall()]

    try:
        # Add latitude to assets
        if "latitude" not in asset_columns:
            print("Adding 'latitude' column to assets table...")
            cursor.execute("ALTER TABLE assets ADD COLUMN latitude VARCHAR")
        
        # Add longitude to assets
        if "longitude" not in asset_columns:
            print("Adding 'longitude' column to assets table...")
            cursor.execute("ALTER TABLE assets ADD COLUMN longitude VARCHAR")
            
        # Add file_path to security_reports
        if "file_path" not in report_columns:
            print("Adding 'file_path' column to security_reports table...")
            cursor.execute("ALTER TABLE security_reports ADD COLUMN file_path VARCHAR")

        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
