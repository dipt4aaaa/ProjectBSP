"""
Database configuration
"""
import os

class DesktopDatabaseConfig:
    
    @classmethod
    def get_connection(cls):
        """
        Get database connection, now only PostgreSQL
        """
        try:
            # Coba PostgreSQL jika tersedia
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'absensi_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
                port=os.getenv('DB_PORT', '5432')
            )
            print("✅ Connected to PostgreSQL")
            return conn, 'postgresql'
            
        except Exception as e:
            raise RuntimeError(f"PostgreSQL connection failed: {e}")

    @classmethod
    def init_tables(cls, conn, db_type):
        """Initialize database tables (PostgreSQL only)"""
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS karyawan (
                id SERIAL PRIMARY KEY,
                nama VARCHAR(100) NOT NULL,
                departemen VARCHAR(100) NOT NULL,
                posisi VARCHAR(100) NOT NULL,
                face_encoding_path TEXT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS log_absensi (
                id SERIAL PRIMARY KEY,
                nama VARCHAR(100) NOT NULL,
                departemen VARCHAR(100),
                posisi VARCHAR(100),
                tanggal DATE NOT NULL,
                jam TIME NOT NULL,
                path_gambar TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        return cursor
