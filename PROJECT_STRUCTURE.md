# 📁 STRUKTUR PROJECT SISTEM ABSENSI

## 🎯 Overview

Sistem absensi berbasis face recognition dengan arsitektur terpisah:

- **Desktop App** (Tkinter) - Pendaftaran dan absensi
- **Web Dashboard** (Flask) - Monitoring dan laporan HR
- **Database** (PostgreSQL/SQLite) - Penyimpanan data

## 📂 Struktur File

```
Project_BSP/
├── 🖥️ desktop_app/              # Aplikasi Desktop Tkinter
│   ├── main.py                   # Aplikasi utama (MODIFIED)
│   ├── requirements.txt          # Dependencies Python
│   └── desktop_database.py       # Database configuration khusus untuk desktop app
│
├── 🌐 dashboard_web/             # Web Dashboard HR
│   ├── app.py                    # Flask application
│   ├── requirements.txt          # Dependencies web
│   ├── .env.example             # Template environment
│   └── templates/               # HTML Templates
│       ├── base.html            # Template dasar
│       ├── dashboard.html       # Halaman dashboard
│       ├── log_absensi.html     # Halaman log absensi
│       └── statistik.html       # Halaman statistik
│
├── 🐳 docker/                    # Docker Configuration
│   ├── docker-compose.yml       # Orchestrasi services
│   ├── Dockerfile.web          # Container web dashboard
│   ├── init.sql                # Schema database
│   └── pgadmin_servers.json    # Konfigurasi pgAdmin
│
└── 📚 README.md                 # Dokumentasi lengkap
```

## ✨ Fitur Yang Ditambahkan

### Desktop App (MODIFIED)

- ✅ **Field tambahan** saat registrasi: Departemen, Posisi
- ✅ **Database PostgreSQL** dengan fallback SQLite
- ✅ **Dialog pendaftaran** yang lebih user-friendly
- ✅ **Koneksi shared** menggunakan database_config

### Web Dashboard (NEW)

- ✅ **Dashboard overview** dengan statistik real-time
- ✅ **Log absensi** dengan filter dan pencarian
- ✅ **Visualisasi data** menggunakan Chart.js
- ✅ **Statistik kehadiran** per departemen dan karyawan
- ✅ **API REST** untuk semua data
- ✅ **Responsive design** dengan Bootstrap

### Database Schema (IMPROVED)

- ✅ **Tabel karyawan** dengan field departemen dan posisi
- ✅ **Tabel log_absensi** dengan data lengkap
- ✅ **PostgreSQL** sebagai database utama
- ✅ **SQLite fallback** untuk kompatibilitas
- ✅ **Indexing** untuk performa optimal

### Docker Infrastructure (NEW)

- ✅ **PostgreSQL container** dengan persistent storage
- ✅ **Web dashboard container** dengan auto-restart
- ✅ **pgAdmin container** untuk database management
- ✅ **Docker network** untuk komunikasi antar service
- ✅ **Volume mounting** untuk foto absensi

## 🔧 Technology Stack

| Component        | Technology                | Purpose                      |
| ---------------- | ------------------------- | ---------------------------- |
| Desktop App      | Python + Tkinter          | UI aplikasi desktop          |
| Face Recognition | face_recognition + OpenCV | Deteksi dan pengenalan wajah |
| Web Backend      | Flask                     | REST API dan web server      |
| Database         | PostgreSQL + SQLite       | Penyimpanan data             |
| Frontend         | Bootstrap + Chart.js      | Interface web responsive     |
| Containerization | Docker + Docker Compose   | Deployment dan orchestration |

## 🚀 Quick Start


### Manual Setup

```bash
# 1. Start Docker services
cd docker
docker-compose up -d

# 2. Install desktop dependencies
cd desktop_app
pip install -r requirements.txt

# 3. Start desktop app
python main.py
```

### Akses Services

- 🌐 **Web Dashboard**: http://localhost:5000
- 🗄️ **pgAdmin**: http://localhost:8080
- 🖥️ **Desktop App**: Jalankan `desktop_app/main.py`

## 📊 API Endpoints

| Endpoint                           | Method | Description                    |
| ---------------------------------- | ------ | ------------------------------ |
| `/api/dashboard-summary`           | GET    | Ringkasan statistik dashboard  |
| `/api/log-absensi`                 | GET    | Data log absensi dengan filter |
| `/api/departemen`                  | GET    | List semua departemen          |
| `/api/karyawan`                    | GET    | List semua karyawan            |
| `/api/statistik/kehadiran-bulanan` | GET    | Statistik kehadiran bulanan    |
| `/api/statistik/departemen`        | GET    | Statistik per departemen       |
| `/api/statistik/karyawan-ranking`  | GET    | Ranking kehadiran karyawan     |

## 🔐 Database Access

### PostgreSQL (Production)

- **Host**: localhost:5432
- **Database**: absensi_db
- **User**: postgres
- **Password**: postgres

### SQLite (Fallback)

- **File**: absensi.db
- **Auto-created** jika PostgreSQL tidak tersedia

## 🎯 Usage Flow

1. **Setup**: Jalankan `install.bat` atau setup manual
2. **Register**: Gunakan desktop app untuk mendaftar karyawan baru
3. **Absensi**: Karyawan melakukan absensi via desktop app
4. **Monitor**: HR mengakses web dashboard untuk laporan
5. **Analyze**: Gunakan statistik untuk analisis kehadiran

## 🔄 Migration

Data lama akan otomatis dimigrasikan dari schema SQLite ke PostgreSQL:

```bash
cd shared
python migrate.py
```

## 📈 Features Comparison

| Feature       | Before      | After                        |
| ------------- | ----------- | ---------------------------- |
| Database      | SQLite only | PostgreSQL + SQLite fallback |
| Registration  | Nama saja   | Nama + Departemen + Posisi   |
| Monitoring    | Desktop app | Web dashboard terpisah       |
| Visualization | Tidak ada   | Charts dan statistik         |
| Deployment    | Manual      | Docker containerized         |
| API Access    | Tidak ada   | REST API lengkap             |

## 🎨 UI/UX Improvements

### Desktop App

- Dialog pendaftaran yang lebih baik
- Informasi koneksi database
- Pesan error yang lebih jelas
- Loading indicators

### Web Dashboard

- Modern responsive design
- Interactive charts
- Advanced filtering
- Real-time updates
- Professional HR dashboard look

---

**🎉 Sistem siap digunakan dengan arsitektur yang scalable dan maintainable!**
