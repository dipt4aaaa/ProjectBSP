import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:geolocator/geolocator.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Absensi Wajah',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: Colors.grey[100],
        snackBarTheme: const SnackBarThemeData(
          behavior: SnackBarBehavior.floating,
        ),
      ),
      home: const AttendancePage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class AttendancePage extends StatefulWidget {
  const AttendancePage({super.key});

  @override
  State<AttendancePage> createState() => _AttendancePageState();
}

class _AttendancePageState extends State<AttendancePage> {
  File? _imageFile;
  bool _isLoading = false;
  String? _lastStatus;
  Color? _lastStatusColor;

  final String apiUrl = "http://192.168.100.205:5050/api/absensi"; // Ganti IP laptop

  // Lokasi kantor
  final double officeLat = 0.51195;
  final double officeLon = 101.44910;
  final double maxDistanceMeters = 100;

  final ImagePicker _picker = ImagePicker();

  Position? _currentPosition;
  double? _distanceToOffice;
  String? _locationError;

  Future<void> _getCurrentLocation() async {
    setState(() {
      _locationError = null;
      _currentPosition = null;
      _distanceToOffice = null;
    });
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        setState(() => _locationError = "Location service tidak aktif.");
        return;
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          setState(() => _locationError = "Izin lokasi ditolak.");
          return;
        }
      }
      if (permission == LocationPermission.deniedForever) {
        setState(() => _locationError = "Izin lokasi ditolak permanen.");
        return;
      }

      Position position = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
      double distance = Geolocator.distanceBetween(
        position.latitude, position.longitude,
        officeLat, officeLon,
      );
      setState(() {
        _currentPosition = position;
        _distanceToOffice = distance;
      });
    } catch (e) {
      setState(() => _locationError = "Gagal mendapatkan lokasi: $e");
    }
  }

  Future<void> _getImage() async {
    try {
      final pickedFile = await _picker.pickImage(source: ImageSource.camera, imageQuality: 70);
      if (pickedFile != null) {
        setState(() => _imageFile = File(pickedFile.path));
      }
    } catch (e) {
      _showStatus("Gagal akses kamera: $e", Colors.red);
    }
  }

  Future<bool> _isAtOffice() async {
    await _getCurrentLocation();
    if (_distanceToOffice == null) return false;
    return _distanceToOffice! <= maxDistanceMeters;
  }

  Future<void> _sendAttendance() async {
    if (_imageFile == null) {
      _showStatus("Ambil foto dulu!", Colors.orange);
      return;
    }

    setState(() => _isLoading = true);

    bool inOffice = await _isAtOffice();
    if (!inOffice) {
      setState(() => _isLoading = false);
      _showStatus(_locationError ?? "Harus di kantor untuk absensi!", Colors.red);
      return;
    }

    List<int> imageBytes = await _imageFile!.readAsBytes();
    String base64Image = base64Encode(imageBytes);

    try {
      var res = await http.post(
        Uri.parse(apiUrl),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"image": base64Image}),
      );

      setState(() => _isLoading = false);

      if (res.statusCode == 200) {
        setState(() => _imageFile = null); // Bersihkan foto setelah sukses
        _showStatus("Absensi berhasil!", Colors.green);
      } else {
        // Ambil pesan error dari API
        String errMsg = "Gagal: ${res.body}";
        try {
          final body = jsonDecode(res.body);
          if (body is Map && body.containsKey('message')) {
            final msg = body['message'].toString().toLowerCase();
            if (msg.contains('no face detected')) {
              errMsg = "Wajah tidak terdeteksi. Pastikan wajah terlihat jelas di kamera.";
            } else if (msg.contains('not recognized') || msg.contains('tidak dikenali')) {
              errMsg = "Wajah tidak dikenali. Silakan daftar terlebih dahulu.";
            } else {
              errMsg = body['message'];
            }
          }
        } catch (_) {}
        _showStatus(errMsg, Colors.red);
      }
    } catch (e) {
      setState(() => _isLoading = false);
      _showStatus("Error: $e", Colors.red);
    }
  }

  void _showStatus(String msg, Color color) {
    setState(() {
      _lastStatus = msg;
      _lastStatusColor = color;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg),
        backgroundColor: color,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Scaffold(
          appBar: AppBar(
            title: const Text("Absensi Wajah"),
            centerTitle: true,
            elevation: 2,
          ),
          body: SingleChildScrollView(
            child: Padding(
              padding: const EdgeInsets.all(18.0),
              child: Column(
                children: [
                  Card(
                    elevation: 3,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: [
                          _imageFile != null
                              ? ClipRRect(
                                  borderRadius: BorderRadius.circular(12),
                                  child: Image.file(_imageFile!, height: 220, fit: BoxFit.cover),
                                )
                              : Icon(Icons.camera_alt, size: 90, color: Colors.grey[400]),
                          const SizedBox(height: 16),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              ElevatedButton.icon(
                                onPressed: _isLoading ? null : _getImage,
                                icon: const Icon(Icons.camera),
                                label: const Text("Ambil Foto"),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.blue[700],
                                  minimumSize: const Size(120, 40),
                                ),
                              ),
                              const SizedBox(width: 16),
                              ElevatedButton.icon(
                                onPressed: (_isLoading || _imageFile == null) ? null : _sendAttendance,
                                icon: const Icon(Icons.send),
                                label: _isLoading
                                    ? const SizedBox(
                                        width: 18,
                                        height: 18,
                                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                                      )
                                    : const Text("Kirim Absensi"),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.green[700],
                                  minimumSize: const Size(120, 40),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    child: Padding(
                      padding: const EdgeInsets.all(14.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            "Status Lokasi",
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                          ),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              Icon(
                                _distanceToOffice != null && _distanceToOffice! <= maxDistanceMeters
                                    ? Icons.check_circle
                                    : Icons.location_off,
                                color: _distanceToOffice != null && _distanceToOffice! <= maxDistanceMeters
                                    ? Colors.green
                                    : Colors.red,
                              ),
                              const SizedBox(width: 8),
                              if (_locationError != null)
                                Expanded(
                                  child: Text(_locationError!, style: const TextStyle(color: Colors.red)),
                                )
                              else if (_currentPosition != null)
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        "Lat: ${_currentPosition!.latitude.toStringAsFixed(5)}, "
                                        "Lon: ${_currentPosition!.longitude.toStringAsFixed(5)}",
                                      ),
                                      Text(
                                        "Jarak ke kantor: ${_distanceToOffice?.toStringAsFixed(1) ?? '-'} meter",
                                        style: TextStyle(
                                          color: _distanceToOffice != null && _distanceToOffice! <= maxDistanceMeters
                                              ? Colors.green
                                              : Colors.red,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ],
                                  ),
                                )
                              else
                                const Text("Mencari lokasi..."),
                              IconButton(
                                icon: const Icon(Icons.refresh),
                                tooltip: "Refresh Lokasi",
                                onPressed: _isLoading ? null : _getCurrentLocation,
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),
                  if (_lastStatus != null)
                    Card(
                      color: _lastStatusColor?.withOpacity(0.12),
                      elevation: 0,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Row(
                          children: [
                            Icon(
                              _lastStatusColor == Colors.green
                                  ? Icons.check_circle
                                  : _lastStatusColor == Colors.red
                                      ? Icons.error
                                      : Icons.info,
                              color: _lastStatusColor,
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Text(
                                _lastStatus!,
                                style: TextStyle(
                                  color: _lastStatusColor,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  const SizedBox(height: 10),
                  const Divider(),
                  const SizedBox(height: 8),
                  Text(
                    "Pastikan Anda berada di area kantor dan wajah terlihat jelas saat foto.",
                    style: TextStyle(color: Colors.grey[700]),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ),
        ),
        if (_isLoading)
          Container(
            color: Colors.black.withOpacity(0.15),
            child: const Center(
              child: CircularProgressIndicator(),
            ),
          ),
      ],
    );
  }
}