# migrate_add_ban.py - Add ban column to users table
"""
Migration untuk menambahkan kolom is_banned ke tabel users
"""

from app_db_fixed import connect

def migrate_add_ban():
    """Add is_banned column to users table"""
    print("🔧 Starting migration: Add ban functionality...")
    
    conn, _ = connect()
    if not conn:
        print("❌ Cannot connect to database!")
        return False
    
    try:
        cur = conn.cursor()
        
        # Add is_banned column if not exists
        print("📊 Adding is_banned column to users table...")
        cur.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'is_banned'
                ) THEN
                    ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT FALSE;
                END IF;
            END $$;
        """)
        
        conn.commit()
        print("✅ Ban functionality migration completed successfully!")
        print()
        print("📋 Changes made:")
        print("   - users.is_banned column added (default: FALSE)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.close()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION: Add Ban Functionality")
    print("=" * 60)
    print()
    
    success = migrate_add_ban()
    
    print()
    if success:
        print("🎉 Migration successful! Ban feature ready.")
    else:
        print("💥 Migration failed! Check the error messages above.")
    print()
