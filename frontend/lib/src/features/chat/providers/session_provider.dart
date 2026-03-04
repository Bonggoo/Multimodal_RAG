import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/chat_session.dart';
import '../repositories/chat_repository.dart';

part 'session_provider.g.dart';

@Riverpod(keepAlive: true)
class SessionNotifier extends _$SessionNotifier {
  @override
  FutureOr<List<ChatSession>> build() async {
    return _fetchSessions();
  }

  Future<List<ChatSession>> _fetchSessions() async {
    final repository = ref.read(chatRepositoryProvider);
    return repository.getSessions();
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchSessions());
  }

  Future<void> deleteSession(String sessionId) async {
    final repository = ref.read(chatRepositoryProvider);
    await repository.deleteSession(sessionId);
    await refresh();
  }
}

@Riverpod(keepAlive: true)
class CurrentSessionId extends _$CurrentSessionId {
  @override
  String? build() => null;

  void set(String? id) => state = id;
}
