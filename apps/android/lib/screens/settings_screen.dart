import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: Consumer<ApiService>(
        builder: (_, api, __) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            const _SectionTitle('Connection'),
            _SettingsTile(
              icon: Icons.link,
              title: 'Desktop URL',
              subtitle: api.baseUrl,
              onTap: () {
                final controller = TextEditingController(text: api.baseUrl);
                showDialog(
                  context: context,
                  builder: (context) => AlertDialog(
                    backgroundColor: const Color(0xFF1A1A2E),
                    title: const Text('Desktop URL'),
                    content: TextField(
                      controller: controller,
                      decoration: const InputDecoration(
                        hintText: 'http://localhost:8000',
                      ),
                    ),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(context),
                        child: const Text('Cancel'),
                      ),
                      TextButton(
                        onPressed: () {
                          api.updateUrl(controller.text);
                          Navigator.pop(context);
                        },
                        child: const Text('Save'),
                      ),
                    ],
                  ),
                );
              },
            ),
            const SizedBox(height: 24),
            const _SectionTitle('About'),
            const _SettingsTile(
              icon: Icons.info_outline,
              title: 'DELIAH',
              subtitle: 'v0.1.0 - Digital Enhanced Local Intelligence Assistant Hub',
            ),
            const _SettingsTile(
              icon: Icons.code,
              title: 'Open Source',
              subtitle: 'Licensed under MIT',
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  final String title;
  const _SectionTitle(this.title);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title.toUpperCase(),
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: Colors.cyan.withOpacity(0.7),
          letterSpacing: 1,
        ),
      ),
    );
  }
}

class _SettingsTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback? onTap;

  const _SettingsTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFF12121A),
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon, color: Colors.cyan),
        title: Text(title),
        subtitle: Text(subtitle, style: const TextStyle(color: Colors.grey)),
        trailing: onTap != null ? const Icon(Icons.chevron_right, color: Colors.grey) : null,
        onTap: onTap,
      ),
    );
  }
}
