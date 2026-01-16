"""
Script to deduplicate assets based on ip:port unique key
Keeps the most recent record for each ip:port combination
"""
import sqlite3
import os

DB_PATH = "data/alpha_mapping.db"

def deduplicate_assets():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Deduplicating assets in {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Find duplicate ip:port combinations
        cursor.execute("""
            SELECT ip, port, COUNT(*) as count
            FROM assets
            WHERE ip IS NOT NULL AND port IS NOT NULL
            GROUP BY ip, port
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        
        duplicates = cursor.fetchall()
        print(f"\nFound {len(duplicates)} duplicate ip:port combinations")
        
        total_deleted = 0
        
        for ip, port, count in duplicates:
            print(f"\nProcessing {ip}:{port} ({count} records)")
            
            # Get all records for this ip:port, ordered by last_seen DESC
            cursor.execute("""
                SELECT id, last_seen, latitude, longitude, raw_data
                FROM assets
                WHERE ip = ? AND port = ?
                ORDER BY last_seen DESC
            """, (ip, port))
            
            records = cursor.fetchall()
            
            if len(records) <= 1:
                continue
                
            # Keep the first one (most recent)
            keep_id = records[0][0]
            print(f"  Keeping record ID {keep_id} (most recent)")
            
            # Merge data from older records if needed
            keep_lat, keep_lon = records[0][2], records[0][3]
            
            # If the kept record doesn't have coordinates, try to get from others
            if not keep_lat or not keep_lon:
                for record in records[1:]:
                    if record[2] and record[3]:  # has lat and lon
                        cursor.execute("""
                            UPDATE assets
                            SET latitude = ?, longitude = ?
                            WHERE id = ?
                        """, (record[2], record[3], keep_id))
                        print(f"  Updated coordinates from older record")
                        break
            
            # Delete older records
            delete_ids = [r[0] for r in records[1:]]
            cursor.execute(f"""
                DELETE FROM assets
                WHERE id IN ({','.join('?' * len(delete_ids))})
            """, delete_ids)
            
            deleted_count = len(delete_ids)
            total_deleted += deleted_count
            print(f"  Deleted {deleted_count} duplicate(s)")
        
        conn.commit()
        print(f"\n✓ Deduplication complete!")
        print(f"  Total duplicates removed: {total_deleted}")
        
        # Show final stats
        cursor.execute("SELECT COUNT(*) FROM assets")
        final_count = cursor.fetchone()[0]
        print(f"  Remaining assets: {final_count}")
        
    except Exception as e:
        print(f"❌ Deduplication failed: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    deduplicate_assets()
