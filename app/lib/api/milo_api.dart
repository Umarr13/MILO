import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Since the backend is running locally, we use 10.0.2.2 for Android emulator
// If running on a physical device, this should be the LAN IP of the hosting machine.
final apiClientProvider = Provider<Dio>((ref) {
  return Dio(BaseOptions(
    baseUrl: 'http://10.0.2.2:8000',
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  ));
});

final miloApiProvider = Provider<MiloApi>((ref) {
  return MiloApi(ref.read(apiClientProvider));
});

class MiloApi {
  final Dio _dio;
  MiloApi(this._dio);

  Future<Map<String, dynamic>> predictMatch(int homeTeamId, int awayTeamId) async {
    final response = await _dio.post('/predict/match', data: {
      'home_team_id': homeTeamId,
      'away_team_id': awayTeamId,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> predictValue(Map<String, dynamic> playerStats) async {
    final response = await _dio.post('/predict/value', data: playerStats);
    return response.data;
  }

  Future<Map<String, dynamic>> scoutSimilar(String playerName) async {
    final response = await _dio.get('/scout/similar/$playerName');
    return response.data;
  }

  Future<List<dynamic>> getTeams() async {
    final response = await _dio.get('/teams');
    return response.data['teams'];
  }
}
