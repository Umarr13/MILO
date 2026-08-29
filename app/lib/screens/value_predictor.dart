import 'package:flutter/material.dart';
import '../theme.dart';

class ValuePredictorScreen extends StatelessWidget {
  const ValuePredictorScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Market Valuation')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: [MiloTheme.accent.withOpacity(0.8), MiloTheme.accentSecondary.withOpacity(0.8)]),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  Text('Estimated Market Value', style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: Colors.white70)),
                  const SizedBox(height: 8),
                  Text('€ 45,500,000', style: Theme.of(context).textTheme.displayLarge?.copyWith(fontSize: 36, color: Colors.white)),
                  const SizedBox(height: 8),
                  Text('+/- €3.5M Confidence Range', style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.white70)),
                ],
              ),
            ),
            const SizedBox(height: 32),
            Text('Player Input Parameters', style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600)),
            const SizedBox(height: 16),
            _buildSlider(context, 'Age', 24.0, 15.0, 45.0),
            _buildSlider(context, 'Goals (Per Season)', 12.0, 0.0, 50.0),
            _buildSlider(context, 'Assists (Per Season)', 8.0, 0.0, 30.0),
            _buildSlider(context, 'Contract Years Left', 2.5, 0.0, 7.0),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {},
                child: const Text('Calculate Value'),
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _buildSlider(BuildContext context, String label, double val, double min, double max) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: Theme.of(context).textTheme.bodyMedium),
            Text(val.toStringAsFixed(1), style: const TextStyle(fontWeight: FontWeight.bold, color: MiloTheme.textPrimary)),
          ],
        ),
        Slider(
          value: val,
          min: min,
          max: max,
          activeColor: MiloTheme.accent,
          inactiveColor: MiloTheme.border,
          onChanged: (v) {},
        ),
      ],
    );
  }
}
