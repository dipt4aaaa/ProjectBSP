from flask import Flask, render_template, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from datetime import datetime, timedelta
import calendar
import os

app = Flask(__name__)

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.init_connection()
    
    def init_connection(self):
        """Inisialisasi koneksi database"""
        try:
            # Coba PostgreSQL dulu
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'absensi_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
                port=os.getenv('DB_PORT', '5432')
            )
            self.db_type = 'postgresql'
            print("Connected to PostgreSQL")
        except Exception as e:
            # Fallback ke SQLite
            print(f"PostgreSQL connection failed: {e}")
            print("Falling back to SQLite")
            self.conn = sqlite3.connect('absensi.db', check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.db_type = 'sqlite'
    
    def get_cursor(self):
        if self.db_type == 'postgresql':
            return self.conn.cursor(cursor_factory=RealDictCursor)
        else:
            return self.conn.cursor()
    
    def execute_query(self, query, params=None):
        cursor = self.get_cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
            if self.db_type == 'sqlite':
                # Convert sqlite3.Row to dict
                result = [dict(row) for row in result]
            return result
        else:
            self.conn.commit()
            return cursor.rowcount

db = DatabaseManager()

@app.route('/')
def dashboard():
    """Halaman dashboard utama"""
    return render_template('dashboard.html')

@app.route('/log-absensi')
def log_absensi():
    """Halaman log absensi"""
    return render_template('log_absensi.html')

@app.route('/statistik')
def statistik():
    """Halaman statistik kehadiran"""
    return render_template('statistik.html')

@app.route('/api/log-absensi')
def api_log_absensi():
    """API untuk mendapatkan data log absensi"""
    try:
        # Filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        nama = request.args.get('nama')
        departemen = request.args.get('departemen')
        
        # Base query
        query = """
            SELECT nama, departemen, posisi, tanggal, jam, path_gambar, created_at
            FROM log_absensi
            WHERE 1=1
        """
        params = []
        
        # Add filters
        if start_date:
            query += " AND tanggal >= %s" if db.db_type == 'postgresql' else " AND tanggal >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND tanggal <= %s" if db.db_type == 'postgresql' else " AND tanggal <= ?"
            params.append(end_date)
        
        if nama:
            query += " AND nama ILIKE %s" if db.db_type == 'postgresql' else " AND nama LIKE ?"
            params.append(f"%{nama}%")
        
        if departemen:
            query += " AND departemen = %s" if db.db_type == 'postgresql' else " AND departemen = ?"
            params.append(departemen)
        
        query += " ORDER BY tanggal DESC, jam DESC LIMIT 1000"
        
        logs = db.execute_query(query, params)
        return jsonify({
            'success': True,
            'data': logs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/departemen')
def api_departemen():
    """API untuk mendapatkan list departemen"""
    try:
        query = "SELECT DISTINCT departemen FROM karyawan WHERE departemen IS NOT NULL ORDER BY departemen"
        departemen_list = db.execute_query(query)
        return jsonify({
            'success': True,
            'data': [d['departemen'] for d in departemen_list]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/karyawan')
def api_karyawan():
    """API untuk mendapatkan list karyawan"""
    try:
        query = "SELECT nama, departemen, posisi FROM karyawan ORDER BY nama"
        karyawan_list = db.execute_query(query)
        return jsonify({
            'success': True,
            'data': karyawan_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/statistik/kehadiran-bulanan')
def api_statistik_bulanan():
    """API untuk statistik kehadiran bulanan"""
    try:
        year = request.args.get('year', datetime.now().year)
        month = request.args.get('month', datetime.now().month)
        
        # Query untuk mendapatkan kehadiran per hari dalam bulan
        if db.db_type == 'postgresql':
            query = """
                SELECT 
                    DATE(tanggal) as tanggal,
                    COUNT(DISTINCT nama) as jumlah_hadir
                FROM log_absensi 
                WHERE EXTRACT(YEAR FROM tanggal) = %s 
                AND EXTRACT(MONTH FROM tanggal) = %s
                GROUP BY DATE(tanggal)
                ORDER BY tanggal
            """
        else:
            query = """
                SELECT 
                    tanggal,
                    COUNT(DISTINCT nama) as jumlah_hadir
                FROM log_absensi 
                WHERE strftime('%Y', tanggal) = ? 
                AND strftime('%m', tanggal) = ?
                GROUP BY tanggal
                ORDER BY tanggal
            """
        
        params = [str(year), f"{int(month):02d}"]
        data = db.execute_query(query, params)
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/statistik/departemen')
def api_statistik_departemen():
    """API untuk statistik kehadiran per departemen"""
    try:
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        query = """
            SELECT 
                departemen,
                COUNT(*) as total_kehadiran,
                COUNT(DISTINCT nama) as jumlah_karyawan
            FROM log_absensi 
            WHERE tanggal BETWEEN %s AND %s
            AND departemen IS NOT NULL
            GROUP BY departemen
            ORDER BY total_kehadiran DESC
        """ if db.db_type == 'postgresql' else """
            SELECT 
                departemen,
                COUNT(*) as total_kehadiran,
                COUNT(DISTINCT nama) as jumlah_karyawan
            FROM log_absensi 
            WHERE tanggal BETWEEN ? AND ?
            AND departemen IS NOT NULL
            GROUP BY departemen
            ORDER BY total_kehadiran DESC
        """
        
        data = db.execute_query(query, [start_date, end_date])
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/statistik/karyawan-ranking')
def api_statistik_karyawan():
    """API untuk ranking kehadiran karyawan"""
    try:
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        query = """
            SELECT 
                nama,
                departemen,
                posisi,
                COUNT(*) as total_kehadiran,
                COUNT(DISTINCT tanggal) as hari_hadir
            FROM log_absensi 
            WHERE tanggal BETWEEN %s AND %s
            GROUP BY nama, departemen, posisi
            ORDER BY total_kehadiran DESC
            LIMIT 50
        """ if db.db_type == 'postgresql' else """
            SELECT 
                nama,
                departemen,
                posisi,
                COUNT(*) as total_kehadiran,
                COUNT(DISTINCT tanggal) as hari_hadir
            FROM log_absensi 
            WHERE tanggal BETWEEN ? AND ?
            GROUP BY nama, departemen, posisi
            ORDER BY total_kehadiran DESC
            LIMIT 50
        """
        
        data = db.execute_query(query, [start_date, end_date])
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard-summary')
def api_dashboard_summary():
    """API untuk data ringkasan dashboard"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Total karyawan
        total_karyawan = db.execute_query("SELECT COUNT(*) as total FROM karyawan")[0]['total']
        
        # Kehadiran hari ini
        kehadiran_hari_ini = db.execute_query(
            "SELECT COUNT(DISTINCT nama) as total FROM log_absensi WHERE tanggal = %s" if db.db_type == 'postgresql'
            else "SELECT COUNT(DISTINCT nama) as total FROM log_absensi WHERE tanggal = ?", 
            [today]
        )[0]['total']
        
        # Total departemen
        total_departemen = db.execute_query(
            "SELECT COUNT(DISTINCT departemen) as total FROM karyawan WHERE departemen IS NOT NULL"
        )[0]['total']
        
        # Absensi bulan ini
        current_month = datetime.now().strftime('%Y-%m')
        if db.db_type == 'postgresql':
            absensi_bulan_ini = db.execute_query(
                "SELECT COUNT(*) as total FROM log_absensi WHERE TO_CHAR(tanggal, 'YYYY-MM') = %s",
                [current_month]
            )[0]['total']
        else:
            absensi_bulan_ini = db.execute_query(
                "SELECT COUNT(*) as total FROM log_absensi WHERE strftime('%Y-%m', tanggal) = ?",
                [current_month]
            )[0]['total']
        
        return jsonify({
            'success': True,
            'data': {
                'total_karyawan': total_karyawan,
                'kehadiran_hari_ini': kehadiran_hari_ini,
                'total_departemen': total_departemen,
                'absensi_bulan_ini': absensi_bulan_ini
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
