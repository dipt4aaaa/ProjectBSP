import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'main.dart'; 

String? globalAccessToken;

class LoginPage extends StatefulWidget {
  final String apiUrl;
  const LoginPage({super.key, required this.apiUrl});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  void _login() async {
    setState(() => _isLoading = true);
    final res = await http.post(
      Uri.parse('${widget.apiUrl}/login'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "username": _usernameController.text.trim(),
        "password": _passwordController.text
      }),
    );
    setState(() => _isLoading = false);

    if (res.statusCode == 200) {
      final body = jsonDecode(res.body);
      globalAccessToken = body['access_token']; // Simpan token JWT
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Login sukses! Selamat datang ${body['data']['nama']}"), backgroundColor: Colors.green),
      );
      // Navigasi ke halaman presensi, kirim token
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => AttendancePage(accessToken: globalAccessToken!),
        ),
      );
    } else {
      String msg = "Login gagal";
      try {
        final body = jsonDecode(res.body);
        msg = body['message'] ?? msg;
      } catch (_) {}
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(msg), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Login"),
        centerTitle: true,
        elevation: 2,
      ),
      body: Center(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Card(
              elevation: 4,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircleAvatar(
                      radius: 38,
                      backgroundColor: Colors.blue[100],
                      child: Icon(Icons.person, size: 48, color: Colors.blue[700]),
                    ),
                    const SizedBox(height: 18),
                    Text(
                      "Selamat Datang",
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue[700],
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      "Silakan login untuk presensi wajah",
                      style: TextStyle(color: Colors.grey[700]),
                    ),
                    const SizedBox(height: 24),
                    TextField(
                      controller: _usernameController,
                      decoration: InputDecoration(
                        labelText: "Username",
                        prefixIcon: const Icon(Icons.person),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _passwordController,
                      decoration: InputDecoration(
                        labelText: "Password",
                        prefixIcon: const Icon(Icons.lock),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      obscureText: true,
                    ),
                    const SizedBox(height: 28),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _isLoading ? null : _login,
                        icon: const Icon(Icons.login),
                        label: _isLoading
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                              )
                            : const Text("Login"),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue[700],
                          minimumSize: const Size(120, 44),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}