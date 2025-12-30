# create_full_database.py
"""
Database Setup Script - Create Full Database
"""

import psycopg2
from psycopg2 import sql
import sys

def create_database():
    """Create crypto_insight database if not exists"""
    try:
        # Connect to postgres database
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="123"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'crypto_insight';")
        exists = cur.fetchone()
        
        if not exists:
            cur.execute("CREATE DATABASE crypto_insight;")
            print("✅ Database 'crypto_insight' created!")
        else:
            print("ℹ️  Database 'crypto_insight' already exists")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False


def create_tables():
    """Create all tables"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="crypto_insight",
            user="postgres",
            password="123"
        )
        cur = conn.cursor()
        
        print("\n🔧 Creating tables...")
        
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                is_banned BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Table 'users' created")
        
        # Crypto data table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS crypto_data (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                name VARCHAR(100),
                price DECIMAL(20, 8),
                market_cap DECIMAL(30, 2),
                volume_24h DECIMAL(30, 2),
                change_24h DECIMAL(10, 2),
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Table 'crypto_data' created")
        
        # Portfolios table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Table 'portfolios' created")
        
        # Portfolio holdings table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_holdings (
                id SERIAL PRIMARY KEY,
                portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
                crypto_symbol VARCHAR(20) NOT NULL,
                amount DECIMAL(20, 8) NOT NULL,
                purchase_price DECIMAL(20, 8),
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Table 'portfolio_holdings' created")
        
        # Transactions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                crypto_symbol VARCHAR(20) NOT NULL,
                transaction_type VARCHAR(10) NOT NULL,
                amount DECIMAL(20, 8) NOT NULL,
                price DECIMAL(20, 8) NOT NULL,
                total DECIMAL(30, 2) NOT NULL,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Table 'transactions' created")
        
        # User sessions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            );
        """)
        print("✅ Table 'user_sessions' created")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("\n🎉 All tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def insert_sample_data():
    """Insert sample data"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="crypto_insight",
            user="postgres",
            password="123"
        )
        cur = conn.cursor()
        
        print("\n📊 Inserting sample data...")
        
        # Insert sample users
        cur.execute("""
            INSERT INTO users (username, password, role) 
            VALUES 
                ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin'),
                ('user1', '0a041b9462caa4a31bac3567e0b6e6fd9100787db2ab433d96f6d178cabfce90', 'user')
            ON CONFLICT (username) DO NOTHING;
        """)
        print("✅ Sample users inserted (admin/admin, user1/123456)")
        
        # Insert sample crypto data
        cur.execute("""
            INSERT INTO crypto_data (symbol, name, price, market_cap, volume_24h, change_24h)
            VALUES
                ('BTC', 'Bitcoin', 45000.00, 850000000000, 30000000000, 2.5),
                ('ETH', 'Ethereum', 3000.00, 360000000000, 15000000000, 1.8),
                ('BNB', 'Binance Coin', 400.00, 65000000000, 2000000000, -0.5),
                ('XRP', 'Ripple', 0.75, 40000000000, 1500000000, 3.2),
                ('ADA', 'Cardano', 0.50, 17000000000, 800000000, 1.1)
            ON CONFLICT DO NOTHING;
        """)
        print("✅ Sample crypto data inserted")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("\n🎉 Sample data inserted successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        return False


def drop_all_tables():
    """Drop all tables"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="crypto_insight",
            user="postgres",
            password="123"
        )
        cur = conn.cursor()
        
        print("\n🗑️  Dropping all tables...")
        
        cur.execute("""
            DROP TABLE IF EXISTS user_sessions CASCADE;
            DROP TABLE IF EXISTS transactions CASCADE;
            DROP TABLE IF EXISTS portfolio_holdings CASCADE;
            DROP TABLE IF EXISTS portfolios CASCADE;
            DROP TABLE IF EXISTS crypto_data CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ All tables dropped!")
        return True
        
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return False


def main():
    """Main menu"""
    print("=" * 60)
    print("DATABASE SETUP - CRYPTO INSIGHT")
    print("=" * 60)
    print("\nOptions:")
    print("1. Create full database (recommended)")
    print("2. Drop and recreate all tables")
    print("3. Add sample data only")
    print("4. Exit")
    print()
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == "1":
        print("\n🚀 Creating full database...\n")
        if create_database():
            if create_tables():
                insert_sample_data()
                print("\n✅ DONE! Database is ready!")
    
    elif choice == "2":
        confirm = input("\n⚠️  This will DELETE ALL DATA! Continue? (yes/no): ").strip().lower()
        if confirm == "yes":
            if drop_all_tables():
                if create_tables():
                    insert_sample_data()
                    print("\n✅ DONE! Database recreated!")
        else:
            print("❌ Cancelled")
    
    elif choice == "3":
        insert_sample_data()
    
    elif choice == "4":
        print("👋 Bye!")
        sys.exit(0)
    
    else:
        print("❌ Invalid option!")


if __name__ == "__main__":
    main()
