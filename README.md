# 📌 Sistem Presensi Face Recognition BSP

Sistem presensi berbasis **pengenalan wajah** dengan arsitektur **multi-platform**:

* **Aplikasi Desktop (Tkinter)** untuk registrasi & presensi yang dipegang admin.
* **Aplikasi Mobile (Flutter)** untuk presensi mandiri karyawan.
* **Dashboard Web (Flask)** untuk HR monitoring.
* **API Server (Flask)** untuk integrasi Flutter mobile app.
* **Clean Architecture** dengan **Service Layer** terpisah.

---

## 🏗️ Arsitektur Sistem

```
Project_BSP/
├── 🖥️ desktop_app/              # Aplikasi Desktop + Service Layer + API
│   ├── main.py                   # Refactored Tkinter App (pakai service layer)
│   ├── face_recognition_service.py # Core business logic
│   ├── api_server.py              # Flask API untuk Flutter
│   ├── desktop_database_config.py # Database config
│   ├── requirements.txt           # Dependencies desktop
│   └── API_DOCUMENTATION.md       # Dokumentasi API
│
├── 🌐 dashboard_web/             # Web Dashboard HR
│   ├── app.py                     # Flask application
│   ├── requirements.txt           # Dependencies web
│   ├── .env.example               # Template environment
│   └── templates/                 # HTML Templates
│       ├── base.html
│       ├── dashboard.html
│       ├── log_presensi.html
│       └── statistik.html
│
├── 🐳 docker/                    # Docker Configuration
│   ├── docker-compose.yml
│   ├── Dockerfile.web
│   ├── init.sql                   # Schema database
│   └── pgadmin_servers.json
│
└── 📚 README.md                   # Dokumentasi (file ini)
```

---

## ✨ Fitur

### Aplikasi Desktop (Tkinter)

* ✅ Pendaftaran karyawan dengan data lengkap
* ✅ Presensi real-time menggunakan kamera
* ✅ Koneksi ke database PostgreSQL
* ✅ Refactor dengan service layer (lebih bersih & reusable)

### Dashboard Web HR (Flask)

* ✅ Dashboard overview dengan statistik
* ✅ Log presensi dengan filter & pencarian
* ✅ Visualisasi data (grafik pie, bar, line)
* ✅ Statistik kehadiran per departemen & karyawan
* ✅ Export data (coming soon)

### API Server (Flask, untuk Flutter)

* ✅ Registrasi wajah via HTTP API
* ✅ Presensi via mobile (kirim foto base64)
* ✅ Ambil daftar karyawan & log presensi
* ✅ Flutter mobile app bisa integrasi dengan mudah

---

## 🚀 Instalasi & Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd Project_BSP
```

### 2. Setup Docker (Database + Dashboard)

```bash
cd docker
docker-compose up -d
```

Services:

* PostgreSQL → `localhost:5432`
* Web Dashboard → `http://localhost:5000`
* pgAdmin (optional) → `http://localhost:8080`

### 3. Setup Desktop App

```bash
cd desktop_app
pip install -r requirements.txt
python main_refactored.py   # versi refactored
```

### 4. Setup API Server (untuk Flutter)

```bash
cd desktop_app
python api_server.py
```

API berjalan di: `http://localhost:5050/api`

---

## 🗄️ Database Schema

### Tabel `karyawan`

| Field                | Type         | Description              |
| -------------------- | ------------ | ------------------------ |
| id                   | SERIAL       | Primary key              |
| nama                 | VARCHAR(100) | Nama karyawan            |
| departemen           | VARCHAR(100) | Departemen               |
| posisi               | VARCHAR(100) | Posisi/jabatan           |
| face\_encoding\_path | TEXT         | Path file encoding wajah |
| created\_at          | TIMESTAMP    | Waktu pendaftaran        |

### Tabel `log_presensi`

| Field        | Type         | Description         |
| ------------ | ------------ | ------------------- |
| id           | SERIAL       | Primary key         |
| nama         | VARCHAR(100) | Nama karyawan       |
| departemen   | VARCHAR(100) | Departemen          |
| posisi       | VARCHAR(100) | Posisi              |
| tanggal      | DATE         | Tanggal presensi    |
| jam          | TIME         | Jam presensi        |
| path\_gambar | TEXT         | Path foto presensi  |
| created\_at  | TIMESTAMP    | Waktu record dibuat |

---

## 📊 API Endpoints

Base URL: `http://localhost:5050/api`

* `POST /register` – Registrasi karyawan baru
* `POST /presensi` – Rekam presensi (foto base64)
* `GET /employees` – List karyawan
* `GET /attendance-logs` – Riwayat presensi
* `POST /reload-faces` – Reload encoding wajah
* `GET /health` – Health check

📄 Detail: lihat `desktop_app/API_DOCUMENTATION.md`

---

## 🔧 Konfigurasi

### Dashboard Web

`.env`

```env
DB_HOST=localhost
DB_NAME=presensi_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432
```

---

## 🎯 Usage Flow

1. Jalankan `docker-compose` untuk DB & dashboard
2. Registrasi karyawan via desktop app
3. Presensi via desktop atau Flutter (API)
4. Monitoring via dashboard web

---

## 📱 Flutter Integration

1. Pastikan device & PC 1 jaringan WiFi
2. Dapatkan IP PC (`ipconfig` di Windows)
3. Contoh Flutter request:

```dart
class FaceRecognitionAPI {
  static const String baseUrl = 'http://192.168.1.100:5050/api';
  
  static Future<Map<String, dynamic>> recordPresensi(String base64Image) async {
    final response = await http.post(
      Uri.parse('$baseUrl/presensi'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'image': base64Image}),
    );
    return json.decode(response.body);
  }
}
```

---

## 🔍 Troubleshooting

### Desktop App

* Kamera tidak terdeteksi → cek driver & index kamera
* Face recognition error → install **Visual C++ Redistributable**
* DB error → cek PostgreSQL berjalan

### Web Dashboard

* DB connection failed → cek docker container
* Charts tidak muncul → cek Chart.js load
* Gambar tidak tampil → cek path `log_presensi`

### API/Flutter

* API tidak bisa diakses → cek firewall & IP PC
* Face tidak dikenali → pastikan pencahayaan bagus

---

## 🔄 Development Workflow

### Desktop

* Kembangkan di `main.py`
* UI terpisah dari logic

### API / Flutter

* Jalankan `api_server.py`
* Tes API dengan Postman
* Implementasikan ke Flutter

---

## 🚧 Next Steps

* 🔒 Tambah autentikasi (JWT)
* ⚡ Optimasi kecepatan face recognition
* 📊 Tambah logging & monitoring
* 📱 Flutter: integrasi kamera & offline mode
* 🐳 Deployment dengan Docker + Nginx

---

## 📞 Support

Buat issue di repository ini untuk pertanyaan atau bug report.

---

**© 2025 Sistem Presensi Face Recognition BSP**

---
