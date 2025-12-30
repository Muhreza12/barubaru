# migrate_add_comments.py — Add comments table with nested reply support
"""
Migration untuk menambahkan tabel comments dengan dukungan nested replies
"""

from app_db_fixed import connect

def migrate_add_comments():
    """Create comments table with parent_id for nested replies"""
    print("🔧 Starting migration: Add comments table...")
    
    conn, _ = connect()
    if not conn:
        print("❌ Cannot connect to database!")
        return False
    
    try:
        cur = conn.cursor()
        
        # Create comments table
        print("📊 Creating comments table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                article_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
                username VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ,
                is_deleted BOOLEAN DEFAULT FALSE
            );
        """)
        
        # Create indexes for performance
        print("📊 Creating indexes...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_comments_article_id 
            ON comments(article_id);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_comments_parent_id 
            ON comments(parent_id);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_comments_username 
            ON comments(username);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_comments_created_at 
            ON comments(created_at DESC);
        """)
        
        conn.commit()
        print("✅ Comments table created successfully!")
        print("✅ Indexes created for performance!")
        print()
        print("📋 Table structure:")
        print("   - id (SERIAL PRIMARY KEY)")
        print("   - article_id (INTEGER, references news)")
        print("   - username (VARCHAR)")
        print("   - content (TEXT)")
        print("   - parent_id (INTEGER, NULL for root comments)")
        print("   - created_at (TIMESTAMPTZ)")
        print("   - updated_at (TIMESTAMPTZ, NULL initially)")
        print("   - is_deleted (BOOLEAN, for soft delete)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.close()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION: Add Comments with Nested Replies")
    print("=" * 60)
    print()
    
    success = migrate_add_comments()
    
    print()
    if success:
        print("🎉 Migration successful! Comments system is ready.")
        print("👉 Now update app_db_fixed.py with comment functions.")
    else:
        print("💥 Migration failed! Check the error messages above.")
    print()
