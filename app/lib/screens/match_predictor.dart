import 'package:flutter/material.dart';
import '../theme.dart';

class MatchPredictorScreen extends StatelessWidget {
  const MatchPredictorScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Match Predictor')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildMatchupHeader(context),
            const SizedBox(height: 24),
            Text('Smart Insights', style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            _buildInsightsCard(context),
            const SizedBox(height: 24),
            Text('Win/Draw/Loss Probability', style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            _buildProbabilityGauge(),
            const SizedBox(height: 24),
            Text('Physical Readiness', style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            _buildFatigueMeters(),
            const SizedBox(height: 24),
            Text('Expected Scoreline (Poisson Heatmap)', style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            _buildPlaceholderMatrix(context),
          ],
        ),
      ),
    );
  }

  Widget _buildMatchupHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: MiloTheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: MiloTheme.border),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          _buildTeamBadge(context, 'ARS', 'Arsenal', true),
          Text('VS', style: Theme.of(context).textTheme.displayLarge?.copyWith(color: MiloTheme.accent, fontSize: 24)),
          _buildTeamBadge(context, 'MCI', 'Man City', false),
        ],
      ),
    );
  }

  Widget _buildTeamBadge(BuildContext context, String shortName, String name, bool isHome) {
    return Column(
      children: [
        Container(
          width: 60, height: 60,
          decoration: BoxDecoration(
            color: MiloTheme.background,
            shape: BoxShape.circle,
            border: Border.all(color: isHome ? MiloTheme.accent : Colors.redAccent, width: 2),
          ),
          child: Center(child: Text(shortName, style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.bold))),
        ),
        const SizedBox(height: 8),
        Text(name, style: Theme.of(context).textTheme.bodyMedium),
      ],
    );
  }

  Widget _buildInsightsCard(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: MiloTheme.accent.withOpacity(0.1), borderRadius: BorderRadius.circular(12), border: Border.all(color: MiloTheme.accent.withOpacity(0.3))),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.lightbulb_outline, color: MiloTheme.accent),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'Arsenal has a massive physical advantage with 3 extra rest days, combined with a higher expected goals rating. Expect a high-tempo home victory.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: MiloTheme.accent),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProbabilityGauge() {
    return Container(
      height: 40,
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(borderRadius: BorderRadius.circular(20)),
      child: Row(
        children: [
          Expanded(flex: 55, child: Container(color: MiloTheme.accent, child: const Center(child: Text('55%', style: TextStyle(fontWeight: FontWeight.bold, color: MiloTheme.background))))),
          Expanded(flex: 15, child: Container(color: MiloTheme.border, child: const Center(child: Text('15%', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white))))),
          Expanded(flex: 30, child: Container(color: Colors.redAccent, child: const Center(child: Text('30%', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white))))),
        ],
      ),
    );
  }

  Widget _buildFatigueMeters() {
    return Row(
      children: [
        Expanded(child: _buildMeter('Arsenal', 0.9, MiloTheme.accent, '7 Days Rest')),
        const SizedBox(width: 16),
        Expanded(child: _buildMeter('Man City', 0.4, Colors.orangeAccent, '3 Days Rest')),
      ],
    );
  }

  Widget _buildMeter(String team, double percentage, Color color, String label) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(team, style: const TextStyle(color: MiloTheme.textSecondary, fontSize: 12)),
        const SizedBox(height: 4),
        LinearProgressIndicator(value: percentage, backgroundColor: MiloTheme.border, color: color, minHeight: 8),
        const SizedBox(height: 4),
        Text(label, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _buildPlaceholderMatrix(BuildContext context) {
    return Container(
      height: 200,
      decoration: BoxDecoration(color: MiloTheme.surface, borderRadius: BorderRadius.circular(16), border: Border.all(color: MiloTheme.border)),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.grid_on_rounded, size: 48, color: MiloTheme.border),
            const SizedBox(height: 16),
            Text('Scoreline Heatmap Rendering...', style: Theme.of(context).textTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}
