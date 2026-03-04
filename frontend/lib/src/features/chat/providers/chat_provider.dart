import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/chat_message.dart';
import '../repositories/chat_repository.dart';
import 'session_provider.dart';

part 'chat_provider.g.dart';

@Riverpod(keepAlive: true)
class ChatNotifier extends _$ChatNotifier {
  @override
  List<ChatMessage> build() {
    return [];
  }

  Future<void> loadSession(String? sessionId) async {
    if (sessionId == null) {
      state = [];
      return;
    }

    state = []; // Loading state or clear
    final repository = ref.read(chatRepositoryProvider);
    try {
      final messages = await repository.getSessionDetail(sessionId);
      state = messages;
    } catch (e) {
      state = [
        ChatMessage(
          id: 'error-load',
          role: MessageRole.assistant,
          content: '대화 내역을 불러오는 중 오류가 발생했습니다: $e',
          timestamp: DateTime.now(),
        ),
      ];
    }
  }

  Future<void> addMessage(String text) async {
    final sessionId = ref.read(currentSessionIdProvider);

    // 1. Add user message
    final userMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      role: MessageRole.user,
      content: text,
      timestamp: DateTime.now(),
    );
    state = [...state, userMessage];

    try {
      // 2. Add temporary assistant message (loading)
      final tempAiId = 'temp-${DateTime.now().millisecondsSinceEpoch}';
      state = [
        ...state,
        ChatMessage(
          id: tempAiId,
          role: MessageRole.assistant,
          content: '답변을 생성 중입니다...',
          timestamp: DateTime.now(),
        ),
      ];

      // 3. Call API
      final repository = ref.read(chatRepositoryProvider);
      final result = await repository.sendQuery(text, sessionId: sessionId);

      // 4. Update with actual response
      final assistantMessage = ChatMessage(
        id:
            result['trace_id'] ??
            DateTime.now().millisecondsSinceEpoch.toString(),
        role: MessageRole.assistant,
        content: result['answer'] as String,
        imageUrl: (result['retrieved_images'] as List?)?.isNotEmpty == true
            ? 'http://localhost:8000/${(result['retrieved_images'] as List).first}'
            : null,
        citations: result['doc_name'] != null
            ? ['출처: ${result['doc_name']}']
            : null,
        traceId: result['trace_id'] as String?,
        timestamp: DateTime.now(),
      );

      state = [
        for (final m in state)
          if (m.id == tempAiId) assistantMessage else m,
      ];

      // 5. Handle new session
      if (sessionId == null && result['session_id'] != null) {
        final newSessionId = result['session_id'] as String;
        ref.read(currentSessionIdProvider.notifier).set(newSessionId);
        // Refresh session list
        ref.read(sessionNotifierProvider.notifier).refresh();
      }
    } catch (e) {
      // Error handling
      state = [
        ...state,
        ChatMessage(
          id: 'error-${DateTime.now().millisecondsSinceEpoch}',
          role: MessageRole.assistant,
          content: '오류가 발생했습니다: $e',
          timestamp: DateTime.now(),
        ),
      ];
    }
  }
}
