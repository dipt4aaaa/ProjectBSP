# Face Recognition API Documentation

## Overview
API untuk sistem absensi face recognition yang dapat digunakan oleh Flutter mobile app. API ini menyediakan endpoint untuk registrasi karyawan dan pencatatan absensi berdasarkan recognition wajah.

## Base URL
```
http://localhost:5050/api
```

Untuk akses dari jaringan LAN (mobile device):
```
http://YOUR_COMPUTER_IP:5050/api
```

## Authentication
API ini tidak menggunakan authentication untuk development. Untuk production, implement JWT atau API key.

## Endpoints

### 1. Health Check
**GET** `/health`

Mengecek status API server.

**Response:**
```json
{
  "status": "success",
  "message": "Face Recognition API is running",
  "version": "1.0.0"
}
```

### 2. Register Employee
**POST** `/register`

Mendaftarkan karyawan baru dengan foto wajah.

**Request Body:**
```json
{
  "name": "John Doe",
  "departemen": "Finance & ICT",
  "posisi": "Manager",
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

**Parameters:**
- `name` (string, required): Nama karyawan
- `departemen` (string, required): Departemen karyawan
  - Values: 'Finance & ICT', 'Human Capital', 'Supply Chain', 'Exploration', 'Exploitation', 'Internal Affairs', 'External Audit', 'Production'
- `posisi` (string, required): Posisi karyawan  
  - Values: 'Manager', 'Senior Staff', 'Staff', 'Junior Staff', 'Intern'
- `image` (string, required): Base64 encoded image

**Success Response (201):**
```json
{
  "status": "success",
  "message": "Employee John Doe registered successfully",
  "data": {
    "name": "John Doe",
    "departemen": "Finance & ICT",
    "posisi": "Manager",
    "image_path": "/path/to/image.jpg"
  }
}
```

**Error Response (400):**
```json
{
  "status": "error",
  "message": "No face detected in image"
}
```

### 3. Record Attendance
**POST** `/absensi`

Mencatat absensi berdasarkan foto wajah.

**Request Body:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

**Parameters:**
- `image` (string, required): Base64 encoded image

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Attendance recorded for John Doe",
  "data": {
    "nama": "John Doe",
    "departemen": "Finance & ICT",
    "posisi": "Manager",
    "tanggal": "2025-08-13",
    "jam": "08:30:45",
    "image_path": "/path/to/attendance_image.jpg"
  }
}
```

**Error Response (400):**
```json
{
  "status": "error",
  "message": "Face not recognized"
}
```

### 4. Get All Employees
**GET** `/employees`

Mendapatkan daftar semua karyawan yang terdaftar.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "nama": "John Doe",
      "departemen": "Finance & ICT",
      "posisi": "Manager"
    },
    {
      "id": 2,
      "nama": "Jane Smith",
      "departemen": "Human Capital",
      "posisi": "Staff"
    }
  ],
  "count": 2
}
```

### 5. Get Attendance Logs
**GET** `/attendance-logs`

Mendapatkan log absensi.

**Query Parameters:**
- `start_date` (string, optional): Tanggal mulai (YYYY-MM-DD)
- `end_date` (string, optional): Tanggal akhir (YYYY-MM-DD)

**Example:**
```
GET /attendance-logs?start_date=2025-08-01&end_date=2025-08-31
```

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "nama": "John Doe",
      "departemen": "Finance & ICT",
      "posisi": "Manager",
      "tanggal": "2025-08-13",
      "jam": "08:30:45",
      "path_gambar": "images/john_doe_2025-08-13_08-30-45.jpg"
    }
  ],
  "count": 1
}
```

### 6. Reload Known Faces
**POST** `/reload-faces`

Memuat ulang data wajah yang dikenal dari database.

**Response (200):**
```json
{
  "status": "success",
  "message": "Known faces reloaded successfully",
  "count": 10
}
```

## Flutter Integration Example

### 1. Setup HTTP Client
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class FaceRecognitionAPI {
  static const String baseUrl = 'http://192.168.1.100:5050/api';
  
  static Future<Map<String, dynamic>> register({
    required String name,
    required String departemen,
    required String posisi,
    required String imageBase64,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/register'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'name': name,
        'departemen': departemen,
        'posisi': posisi,
        'image': imageBase64,
      }),
    );
    
    return json.decode(response.body);
  }
  
  static Future<Map<String, dynamic>> recordAttendance({
    required String imageBase64,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/absensi'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'image': imageBase64,
      }),
    );
    
    return json.decode(response.body);
  }
}
```

### 2. Convert Camera Image to Base64
```dart
import 'dart:convert';
import 'dart:typed_data';

String imageToBase64(Uint8List imageBytes) {
  return base64Encode(imageBytes);
}

// For camera plugin
import 'package:camera/camera.dart';

Future<String> captureAndConvert() async {
  final XFile image = await controller.takePicture();
  final Uint8List imageBytes = await image.readAsBytes();
  return 'data:image/jpeg;base64,${base64Encode(imageBytes)}';
}
```

### 3. Usage Example
```dart
// Register new employee
final result = await FaceRecognitionAPI.register(
  name: 'John Doe',
  departemen: 'Finance & ICT',
  posisi: 'Manager',
  imageBase64: await captureAndConvert(),
);

if (result['status'] == 'success') {
  print('Registration successful: ${result['message']}');
} else {
  print('Registration failed: ${result['message']}');
}

// Record attendance
final attendanceResult = await FaceRecognitionAPI.recordAttendance(
  imageBase64: await captureAndConvert(),
);

if (attendanceResult['status'] == 'success') {
  final data = attendanceResult['data'];
  print('Attendance recorded for: ${data['nama']}');
  print('Time: ${data['tanggal']} ${data['jam']}');
} else {
  print('Attendance failed: ${attendanceResult['message']}');
}
```

## Error Handling

Semua endpoint mengembalikan response dengan format:
```json
{
  "status": "success" | "error",
  "message": "Description",
  "data": {} // Optional, hanya untuk success response
}
```

**Common Error Responses:**
- `400 Bad Request`: Invalid input atau validation error
- `404 Not Found`: Endpoint tidak ditemukan
- `405 Method Not Allowed`: HTTP method tidak diizinkan
- `500 Internal Server Error`: Server error

## Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run API server:
```bash
python api_server.py
```

3. API akan berjalan di:
- Local: `http://localhost:5050`
- LAN: `http://YOUR_IP:5050`

## Network Configuration

Untuk mengakses API dari mobile device:

1. Pastikan komputer dan mobile device terhubung ke jaringan Wi-Fi yang sama
2. Dapatkan IP address komputer:
   ```bash
   ipconfig  # Windows
   ifconfig  # macOS/Linux
   ```
3. Update base URL di Flutter app dengan IP address tersebut
4. Pastikan firewall tidak memblokir port 5050

## Production Considerations

1. **Security**: Implement authentication (JWT tokens)
2. **HTTPS**: Use SSL/TLS encryption
3. **Rate Limiting**: Prevent API abuse
4. **Image Storage**: Consider cloud storage for images
5. **Database**: Use production database (PostgreSQL)
6. **Deployment**: Use production WSGI server (Gunicorn + Nginx)
