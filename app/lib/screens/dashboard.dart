import 'package:flutter/material.dart';
import '../theme.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Milo Hub')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Welcome to Milo Analytics', style: Theme.of(context).textTheme.displayMedium),
            const SizedBox(height: 8),
            Text('Professional Football Intelligence', style: Theme.of(context).textTheme.bodyMedium),
            const SizedBox(height: 32),
            
            _buildActionCard(
              context,
              title: 'Match Prediction Engine',
              subtitle: 'Elo & Poisson-based match simulations.',
              icon: Icons.sports_soccer_rounded,
              color: MiloTheme.accent,
            ),
            const SizedBox(height: 16),
            _buildActionCard(
              context,
              title: 'Player Scouting',
              subtitle: 'Find statistical clones using Cosine Similarity.',
              icon: Icons.person_search_rounded,
              color: Colors.purpleAccent,
            ),
            const SizedBox(height: 16),
            _buildActionCard(
              context,
              title: 'Market Valuation',
              subtitle: 'Estimate true market value via Random Forest.',
              icon: Icons.euro_symbol_rounded,
              color: MiloTheme.accentSecondary,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionCard(BuildContext context, {required String title, required String subtitle, required IconData icon, required Color color}) {
    return Container(
      decoration: BoxDecoration(
        color: MiloTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: MiloTheme.border),
      ),
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 28),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600)),
                const SizedBox(height: 4),
                Text(subtitle, style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          ),
          Icon(Icons.arrow_forward_ios_rounded, color: MiloTheme.textSecondary, size: 16),
        ],
      ),
    );
  }
}
