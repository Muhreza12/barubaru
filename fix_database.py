# fix_database.py - Railway Database Fix Tool
import psycopg2
import hashlib

DATABASE_URL = "postgresql://postgres:WuZnoaOPPcCPpsPQcpJZdiswoenTjoXE@yamabiko.proxy.rlwy.net:28518/railway?sslmode=require"

def fix_database():
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Database connected!")
        print("-" * 60)
        
        # 1. Backup users
        print("Step 1: Creating backup...")
        try:
            cur.execute("CREATE TEMP TABLE users_backup AS SELECT * FROM users WHERE TRUE")
            print("OK - Backup created")
        except Exception as e:
            print(f"SKIP - No existing users: {e}")
        
        # 2. Drop tables
        print("\nStep 2: Dropping old tables...")
        cur.execute("DROP TABLE IF EXISTS user_sessions CASCADE")
        cur.execute("DROP TABLE IF EXISTS users CASCADE")
        print("OK - Old tables dropped")
        
        # 3. Create users table
        print("\nStep 3: Creating users table...")
        cur.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_banned BOOLEAN DEFAULT FALSE
            )
        """)
        print("OK - Users table created")
        
        # 4. Create sessions table
        print("\nStep 4: Creating user_sessions table...")
        cur.execute("""
            CREATE TABLE user_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("OK - User_sessions table created")
        
        # 5. Restore users
        print("\nStep 5: Restoring users from backup...")
        try:
            cur.execute("""
                INSERT INTO users (username, password, role, created_at, is_banned)
                SELECT username, password, role, created_at, is_banned 
                FROM users_backup
            """)
            cur.execute("SELECT COUNT(*) FROM users")
            count = cur.fetchone()[0]
            print(f"OK - Restored {count} users")
        except Exception as e:
            print(f"SKIP - No users to restore: {e}")
        
        # 6. Create admin
        print("\nStep 6: Creating admin user...")
        admin_pw = hashlib.sha256('admin'.encode()).hexdigest()
        try:
            cur.execute("""
                INSERT INTO users (username, password, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            """, ('admin', admin_pw, 'admin'))
            print("OK - Admin user ready")
        except:
            print("SKIP - Admin already exists")
        
        # 7. Verify
        print("\n" + "=" * 60)
        print("VERIFICATION:")
        print("=" * 60)
        
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        print(f"Total users: {user_count}")
        
        if user_count > 0:
            cur.execute("SELECT id, username, role FROM users")
            print("\nUsers list:")
            for uid, uname, urole in cur.fetchall():
                print(f"  - ID {uid}: {uname} ({urole})")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("SUCCESS! Database fixed!")
        print("=" * 60)
        print("\nYou can now run: python auth_ui_cyberpunk.py")
        print("Login: admin / admin")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("Railway Database Fix Tool")
    print("=" * 60)
    print("\nWARNING: This will recreate tables!")
    print("Existing users will be backed up and restored.")
    print()
    
    confirm = input("Continue? (yes/no): ").lower()
    
    if confirm in ['yes', 'y']:
        print()
        fix_database()
    else:
        print("Cancelled.")
