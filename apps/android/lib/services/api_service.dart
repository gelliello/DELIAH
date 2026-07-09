import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

class ApiService extends ChangeNotifier {
  String baseUrl = 'http://localhost:8000';
  bool connected = false;

  Future<void> checkHealth() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health'));
      final data = jsonDecode(response.body);
      connected = data['status'] == 'healthy';
      notifyListeners();
    } catch (e) {
      connected = false;
      notifyListeners();
    }
  }

  Future<Map<String, dynamic>> sendMessage(String message, {String mode = 'general'}) async {
    final response = await http.post(
      Uri.parse('$baseUrl/chat'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'message': message, 'mode': mode}),
    );
    return jsonDecode(response.body);
  }

  void updateUrl(String url) {
    baseUrl = url;
    notifyListeners();
  }
}
