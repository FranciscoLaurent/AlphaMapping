"""
Apply unique constraint to existing database
This recreates the assets table with the unique constraint
"""
import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = "data/alpha_mapping.db"
BACKUP_PATH = f"data/alpha_mapping_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def migrate_database():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    # Create backup
    print(f"Creating backup at {BACKUP_PATH}...")
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print("✓ Backup created")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("\nApplying unique constraint migration...")
        
        # Create new table with unique constraint
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets_new (
                id INTEGER PRIMARY KEY,
                ip VARCHAR,
                port INTEGER,
                protocol VARCHAR,
                domain VARCHAR,
                host VARCHAR,
                title VARCHAR,
                server VARCHAR,
                country VARCHAR,
                city VARCHAR,
                org VARCHAR,
                last_seen DATETIME,
                platform VARCHAR,
                raw_data JSON,
                query_id INTEGER,
                latitude VARCHAR,
                longitude VARCHAR,
                UNIQUE(ip, port),
                FOREIGN KEY(query_id) REFERENCES platform_queries(id)
            )
        """)
        
        # Copy data from old table
        cursor.execute("""
            INSERT INTO assets_new
            SELECT * FROM assets
        """)
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE assets")
        cursor.execute("ALTER TABLE assets_new RENAME TO assets")
        
        # Recreate indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_assets_ip ON assets (ip)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_assets_domain ON assets (domain)")
        
        conn.commit()
        print("✓ Migration completed successfully")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM assets")
        count = cursor.fetchone()[0]
        print(f"  Total assets: {count}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print(f"Restoring from backup...")
        conn.close()
        shutil.copy2(BACKUP_PATH, DB_PATH)
        print("✓ Database restored from backup")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
