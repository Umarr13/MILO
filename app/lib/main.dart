import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'theme.dart';
import 'screens/dashboard.dart';
import 'screens/match_predictor.dart';
import 'screens/scouting.dart';
import 'screens/value_predictor.dart';

void main() {
  runApp(const ProviderScope(child: MiloApp()));
}

class MiloApp extends StatelessWidget {
  const MiloApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Milo Analytics',
      theme: MiloTheme.darkTheme,
      home: const MainNavigator(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class MainNavigator extends StatefulWidget {
  const MainNavigator({super.key});

  @override
  State<MainNavigator> createState() => _MainNavigatorState();
}

class _MainNavigatorState extends State<MainNavigator> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const DashboardScreen(),
    const MatchPredictorScreen(),
    const ScoutingScreen(),
    const ValuePredictorScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.dashboard_rounded), label: 'Hub'),
          BottomNavigationBarItem(icon: Icon(Icons.sports_soccer_rounded), label: 'Matches'),
          BottomNavigationBarItem(icon: Icon(Icons.person_search_rounded), label: 'Scouting'),
          BottomNavigationBarItem(icon: Icon(Icons.euro_symbol_rounded), label: 'Valuation'),
        ],
      ),
    );
  }
}
