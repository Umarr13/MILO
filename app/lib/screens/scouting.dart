import 'package:flutter/material.dart';
import '../theme.dart';

class ScoutingScreen extends StatelessWidget {
  const ScoutingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Player Scouting')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              decoration: BoxDecoration(color: MiloTheme.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: MiloTheme.border)),
              child: const TextField(
                decoration: InputDecoration(
                  hintText: 'Search for a player...',
                  border: InputBorder.none,
                  icon: Icon(Icons.search, color: MiloTheme.textSecondary),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text('Statistical Clones (Cosine Similarity)', style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600)),
            const SizedBox(height: 16),
            _buildCloneCard(context, 'Kevin De Bruyne', '98.5% Match', 'Man City'),
            const SizedBox(height: 8),
            _buildCloneCard(context, 'Martin Ødegaard', '94.2% Match', 'Arsenal'),
            const SizedBox(height: 8),
            _buildCloneCard(context, 'Bruno Fernandes', '91.8% Match', 'Man Utd'),
          ],
        ),
      ),
    );
  }

  Widget _buildCloneCard(BuildContext context, String name, String matchPct, String team) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: MiloTheme.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: MiloTheme.border)),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              CircleAvatar(backgroundColor: MiloTheme.accent.withOpacity(0.2), child: const Icon(Icons.person, color: MiloTheme.accent)),
              const SizedBox(width: 16),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(name, style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600)),
                  Text(team, style: Theme.of(context).textTheme.bodyMedium),
                ],
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(color: MiloTheme.accentSecondary.withOpacity(0.2), borderRadius: BorderRadius.circular(20)),
            child: Text(matchPct, style: const TextStyle(color: MiloTheme.accentSecondary, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}
