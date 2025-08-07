# Sistem Absensi Face Recognition

Sistem absensi berbasis pengenalan wajah dengan arsitektur terpisah antara aplikasi desktop dan dashboard web HR.

## 🏗️ Arsitektur Sistem

```
├── desktop_app/          # Aplikasi Tkinter untuk pendaftaran dan absensi
├── dashboard_web/        # Web dashboard HR (Flask)
├── docker/              # Docker configuration
├── data_wajah/          # Penyimpanan foto dan encoding wajah
├── log_absensi/         # Log foto absensi
└── GFPGAN/              # AI enhancement untuk foto
```

## ✨ Fitur

### Aplikasi Desktop (Tkinter)

- ✅ Pendaftaran karyawan dengan data lengkap (nama, departemen, posisi)
- ✅ Absensi real-time menggunakan kamera
- ✅ Face recognition dengan GFPGAN enhancement
- ✅ Koneksi ke database PostgreSQL/SQLite

### Dashboard Web HR (Flask)

- ✅ Dashboard overview dengan statistik
- ✅ Log absensi dengan filter dan pencarian
- ✅ Visualisasi data (grafik pie, bar, line chart)
- ✅ Statistik kehadiran per departemen dan karyawan
- ✅ Export data (coming soon)

## 🚀 Instalasi dan Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd Absen_BSP
```

### 2. Setup Docker (Dashboard Web + Database)

```bash
cd docker
docker-compose up -d
```

Services yang akan berjalan:

- **PostgreSQL**: `localhost:5432`
- **Web Dashboard**: `http://localhost:5000`
- **pgAdmin**: `http://localhost:8080` (optional)

### 3. Setup Aplikasi Desktop

```bash
cd desktop_app
pip install -r requirements.txt
python main.py
```

## 🗄️ Database Schema

### Tabel `karyawan`

| Field              | Type         | Description              |
| ------------------ | ------------ | ------------------------ |
| id                 | SERIAL       | Primary key              |
| nama               | VARCHAR(100) | Nama karyawan            |
| departemen         | VARCHAR(100) | Departemen               |
| posisi             | VARCHAR(100) | Posisi/jabatan           |
| face_encoding_path | TEXT         | Path file encoding wajah |
| created_at         | TIMESTAMP    | Waktu pendaftaran        |

### Tabel `log_absensi`

| Field       | Type         | Description         |
| ----------- | ------------ | ------------------- |
| id          | SERIAL       | Primary key         |
| nama        | VARCHAR(100) | Nama karyawan       |
| departemen  | VARCHAR(100) | Departemen          |
| posisi      | VARCHAR(100) | Posisi              |
| tanggal     | DATE         | Tanggal absensi     |
| jam         | TIME         | Jam absensi         |
| path_gambar | TEXT         | Path foto absensi   |
| created_at  | TIMESTAMP    | Waktu record dibuat |

## 🔧 Konfigurasi

### Environment Variables (Dashboard Web)

```env
DB_HOST=localhost
DB_NAME=absensi_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432
```

### Database Connection Fallback

Aplikasi akan otomatis fallback ke SQLite jika PostgreSQL tidak tersedia.

## 📊 API Endpoints

### Dashboard API

- `GET /api/dashboard-summary` - Ringkasan data dashboard
- `GET /api/log-absensi` - Data log absensi dengan filter
- `GET /api/departemen` - List departemen
- `GET /api/karyawan` - List karyawan
- `GET /api/statistik/kehadiran-bulanan` - Statistik bulanan
- `GET /api/statistik/departemen` - Statistik per departemen
- `GET /api/statistik/karyawan-ranking` - Ranking kehadiran karyawan

## 🔍 Troubleshooting

### Desktop App Issues

1. **Camera tidak terdeteksi**: Pastikan kamera terhubung dan driver terinstall
2. **Face recognition error**: Install Visual C++ Redistributable
3. **Database connection error**: Pastikan PostgreSQL berjalan di port 5432

### Web Dashboard Issues

1. **Database connection failed**: Cek docker container PostgreSQL
2. **Charts tidak muncul**: Pastikan Chart.js terload
3. **Images tidak tampil**: Cek path folder log_absensi

### Docker Issues

```bash
# Restart services
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs web_dashboard
docker-compose logs postgres
```

## 🎯 Usage Flow

1. **Setup**: Jalankan docker-compose untuk database dan web dashboard
2. **Registrasi**: Gunakan aplikasi desktop untuk mendaftarkan karyawan
3. **Absensi**: Karyawan melakukan absensi via aplikasi desktop
4. **Monitoring**: HR mengakses dashboard web untuk melihat laporan

## 🔄 Development

### Adding New Features

1. **Desktop App**: Modifikasi `desktop_app/main.py`
2. **Web Dashboard**:
   - Backend: `dashboard_web/app.py`
   - Frontend: `dashboard_web/templates/`
3. **Database**: Update `docker/init.sql`

### Testing

```bash
# Test desktop app
cd desktop_app
python main.py

# Test web dashboard
cd dashboard_web
python app.py
```

## 📝 TODO

- [ ] Export data ke Excel/PDF
- [ ] Real-time notifications
- [ ] Mobile app integration
- [ ] Advanced analytics
- [ ] Multi-camera support
- [ ] Cloud storage integration

## 📞 Support

Untuk pertanyaan dan support, silakan buat issue di repository ini.

---

**© 2025 Sistem Absensi Face Recognition**
