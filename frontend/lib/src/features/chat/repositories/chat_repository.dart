import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/api/dio_provider.dart';
import '../models/chat_session.dart';
import '../models/chat_message.dart';

part 'chat_repository.g.dart';

class ChatRepository {
  final Dio _dio;
  const ChatRepository(this._dio);

  Future<Map<String, dynamic>> sendQuery(
    String query, {
    String? docName,
    String? sessionId,
  }) async {
    final response = await _dio.post(
      '/qa',
      data: {
        'query': query,
        if (docName != null) 'filters': {'doc_name': docName},
        if (sessionId != null) 'session_id': sessionId,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  Future<List<ChatSession>> getSessions() async {
    final response = await _dio.get('/sessions');
    final data = response.data['sessions'] as List;
    return data
        .map((e) => ChatSession.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<ChatMessage>> getSessionDetail(String sessionId) async {
    final response = await _dio.get('/sessions/$sessionId');
    final data = response.data['messages'] as List;
    return data.map((e) {
      final role = e['role'] == 'user'
          ? MessageRole.user
          : MessageRole.assistant;
      return ChatMessage(
        id: e['trace_id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
        role: role,
        content: e['content'] as String,
        timestamp: DateTime.tryParse(e['timestamp'] ?? '') ?? DateTime.now(),
      );
    }).toList();
  }

  Future<void> deleteSession(String sessionId) async {
    await _dio.delete('/sessions/$sessionId');
  }
}

@riverpod
ChatRepository chatRepository(ChatRepositoryRef ref) {
  return ChatRepository(ref.watch(dioProvider));
}
