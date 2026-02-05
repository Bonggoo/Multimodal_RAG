import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/network/api_client.dart';
import '../../../core/auth/auth_provider.dart';

part 'session_provider.g.dart';

@riverpod
class SessionList extends _$SessionList {
  @override
  FutureOr<List<Map<String, dynamic>>> build() async {
    final authState = ref.watch(authNotifierProvider);
    if (authState.user == null) {
      return [];
    }
    return _fetchSessions();
  }

  Future<List<Map<String, dynamic>>> _fetchSessions() async {
    final dio = ref.read(dioProvider);
    try {
      final response = await dio.get('/sessions');
      final List<dynamic> sessionsJson = response.data['sessions'];
      return sessionsJson.cast<Map<String, dynamic>>();
    } catch (e) {
      return [];
    }
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchSessions());
  }

  Future<void> deleteSession(String sessionId) async {
    final dio = ref.read(dioProvider);
    await dio.delete('/sessions/$sessionId');
    await refresh();
  }
}
