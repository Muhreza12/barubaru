# app_db_fixed.py - Railway PostgreSQL Connection
import psycopg2
from psycopg2 import pool
from typing import Dict, Optional
import secrets
import hashlib

# ========== RAILWAY DATABASE CONNECTION ==========
DATABASE_URL = "postgresql://postgres:WuZnoaOPPcCPpsPQcpJZdiswoenTjoXE@yamabiko.proxy.rlwy.net:28518/railway?sslmode=require"

# Connection pool
connection_pool = None


# ========== CONNECTION POOL MANAGEMENT ==========

def create_connection_pool():
    """Create database connection pool"""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,
            DATABASE_URL
        )
        print("✅ Connected to Railway PostgreSQL")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def get_connection():
    """Get connection from pool"""
    if connection_pool is None:
        create_connection_pool()
    return connection_pool.getconn()


def release_connection(conn):
    """Release connection back to pool"""
    if connection_pool and conn:
        connection_pool.putconn(conn)


# ========== AUTHENTICATION FUNCTIONS ==========

def verify_user(username: str, password: str):
    """Verify user credentials"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Hash password
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        cur.execute("""
            SELECT role FROM users 
            WHERE username = %s AND password = %s AND is_banned = FALSE
        """, (username, hashed_pw))
        
        result = cur.fetchone()
        if result:
            return result[0]
        return None
        
    except Exception as e:
        print(f"❌ Verify user error: {e}")
        return None
    finally:
        if conn:
            release_connection(conn)


def create_user(username: str, password: str, role: str = 'user'):
    """Create new user"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        cur.execute("""
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, %s)
        """, (username, hashed_pw, role))
        
        conn.commit()
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Create user error: {e}")
        return False
    finally:
        if conn:
            release_connection(conn)


def user_exists(username: str):
    """Check if user exists"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        
        return result is not None
        
    except Exception as e:
        print(f"❌ User exists check error: {e}")
        return False
    finally:
        if conn:
            release_connection(conn)


def start_session(username: str):
    """Start user session"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Get user ID
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        if not user:
            return None
        
        user_id = user[0]
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        
        cur.execute("""
            INSERT INTO user_sessions (user_id, session_token, is_active)
            VALUES (%s, %s, TRUE)
            RETURNING id
        """, (user_id, session_token))
        
        conn.commit()
        return session_token
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Start session error: {e}")
        return None
    finally:
        if conn:
            release_connection(conn)


def end_session(session_token: str):
    """End user session (logout)"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE user_sessions
            SET is_active = FALSE, ended_at = CURRENT_TIMESTAMP
            WHERE session_token = %s AND is_active = TRUE
        """, (session_token,))
        
        conn.commit()
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ End session error: {e}")
        return False
    finally:
        if conn:
            release_connection(conn)


def validate_session(session_token: str):
    """Validate if session is active"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT user_id FROM user_sessions
            WHERE session_token = %s AND is_active = TRUE
        """, (session_token,))
        
        result = cur.fetchone()
        if result:
            return result[0]
        return None
        
    except Exception as e:
        print(f"❌ Validate session error: {e}")
        return None
    finally:
        if conn:
            release_connection(conn)


def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user details by username"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, username, role, created_at, is_banned
            FROM users
            WHERE username = %s
        """, (username,))
        
        user = cur.fetchone()
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'role': user[2],
                'created_at': user[3],
                'is_banned': user[4]
            }
        return None
        
    except Exception as e:
        print(f"❌ Get user error: {e}")
        return None
    finally:
        if conn:
            release_connection(conn)


def get_all_users():
    """Get all users (admin function)"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, username, role, created_at, is_banned
            FROM users
            ORDER BY created_at DESC
        """)
        
        users = []
        for row in cur.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'role': row[2],
                'created_at': row[3],
                'is_banned': row[4]
            })
        
        return users
        
    except Exception as e:
        print(f"❌ Get all users error: {e}")
        return []
    finally:
        if conn:
            release_connection(conn)


def ban_user(username: str):
    """Ban a user (admin function)"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE users
            SET is_banned = TRUE
            WHERE username = %s
        """, (username,))
        
        conn.commit()
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Ban user error: {e}")
        return False
    finally:
        if conn:
            release_connection(conn)


def unban_user(username: str):
    """Unban a user (admin function)"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE users
            SET is_banned = FALSE
            WHERE username = %s
        """, (username,))
        
        conn.commit()
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Unban user error: {e}")
        return False
    finally:
        if conn:
            release_connection(conn)


def health_check():
    """Check database connection health"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        return True
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    finally:
        if conn:
            release_connection(conn)


def setup_database():
    """Setup database (placeholder)"""
    pass


# ========== INITIALIZE CONNECTION POOL ==========
create_connection_pool()


# ========== TEST SCRIPT ==========
if __name__ == "__main__":
    print("=" * 70)
    print("🚀 RAILWAY POSTGRESQL CONNECTION TEST")
    print("=" * 70)
    
    # Test connection
    if health_check():
        print("✅ Database connection successful!")
        print("✅ SSL connection to Railway established")
        
        # Count users
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        print(f"\n📊 Total users in database: {count}")
        
        # List all users
        cur.execute("SELECT id, username, role, is_banned FROM users ORDER BY id")
        users = cur.fetchall()
        
        print("\n📋 Users List:")
        print("-" * 70)
        print(f"{'ID':<5} {'Username':<20} {'Role':<15} {'Status':<10}")
        print("-" * 70)
        
        for user_id, username, role, banned in users:
            status = "BANNED" if banned else "ACTIVE"
            print(f"{user_id:<5} {username:<20} {role:<15} {status:<10}")
        
        print("-" * 70)
        
        # Count active sessions
        cur.execute("SELECT COUNT(*) FROM user_sessions WHERE is_active = TRUE")
        sessions = cur.fetchone()[0]
        print(f"\n🔐 Active sessions: {sessions}")
        
        release_connection(conn)
        
    else:
        print("❌ Database connection FAILED!")
        print("📝 Check your DATABASE_URL")
    
    print("=" * 70)
    print("✅ All functions ready!")
    print("=" * 70)
