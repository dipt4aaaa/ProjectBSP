"""
Database configuration khusus untuk desktop app dengan error handling yang lebih baik
"""
import os
import sqlite3

class DesktopDatabaseConfig:
    """Database config khusus untuk desktop app dengan fallback yang aman"""
    
    # SQLite configuration (primary untuk desktop)
    SQLITE_DB = os.path.join(os.path.dirname(__file__), '..', 'absensi.db')
    
    @classmethod
    def get_connection(cls):
        """
        Get database connection dengan prioritas SQLite untuk desktop app
        Returns: (connection, db_type)
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
            
        except (ImportError, Exception) as e:
            # Fallback ke SQLite (default untuk desktop)
            print(f"PostgreSQL not available: {e}")
            print("🔄 Using SQLite database...")
            
            conn = sqlite3.connect(cls.SQLITE_DB, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn, 'sqlite'
    
    @classmethod
    def init_tables(cls, conn, db_type):
        """Initialize database tables"""
        cursor = conn.cursor()
        
        if db_type == 'postgresql':
            # PostgreSQL table creation
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS karyawan (
                    id SERIAL PRIMARY KEY,
                    nama VARCHAR(100) NOT NULL,
                    departemen VARCHAR(100) NOT NULL,
                    posisi VARCHAR(100) NOT NULL,
                    face_encoding_path TEXT,
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
        else:
            # SQLite table creation
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS karyawan (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT NOT NULL,
                    departemen TEXT NOT NULL,
                    posisi TEXT NOT NULL,
                    face_encoding_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS log_absensi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT NOT NULL,
                    departemen TEXT,
                    posisi TEXT,
                    tanggal TEXT NOT NULL,
                    jam TEXT NOT NULL,
                    path_gambar TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        conn.commit()
        return cursor
