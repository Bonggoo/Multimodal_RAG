import 'dart:convert';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../../core/auth/auth_provider.dart';

part 'chat_provider.g.dart';
part 'chat_provider.freezed.dart';

@freezed
class ChatMessage with _$ChatMessage {
  const factory ChatMessage({
    required String text,
    required bool isUser,
    List<String>? images,
    String? traceId,
  }) = _ChatMessage;
}

@freezed
class UserProfile with _$UserProfile {
  const factory UserProfile({
    String? name,
    String? role,
    List<String>? interests,
    String? customInstructions,
  }) = _UserProfile;
}

@freezed
class ChatState with _$ChatState {
  const factory ChatState({
    required List<ChatMessage> messages,
    required UserProfile profile,
  }) = _ChatState;
}

@riverpod
class Chat extends _$Chat {
  @override
  ChatState build() {
    // AuthNotifier에서 유저 정보를 구독하여 초기 프로필 설정
    final authUser = ref.watch(authNotifierProvider).user;

    return ChatState(
      messages: [],
      profile: UserProfile(
        name: authUser?.displayName ?? '최봉구',
        role: '소프트웨어 엔지니어',
        interests: ['Flutter', 'Python', 'AI'],
        customInstructions: '항상 친절하고 기술적인 답변을 제공해주세요.',
      ),
    );
  }

  void addMessage(
    String text,
    bool isUser, {
    List<String>? images,
    String? traceId,
  }) {
    state = state.copyWith(
      messages: [
        ...state.messages,
        ChatMessage(
          text: text,
          isUser: isUser,
          images: images,
          traceId: traceId,
        ),
      ],
    );
  }

  void deleteMessage(int index) {
    final newList = List<ChatMessage>.from(state.messages);
    newList.removeAt(index);
    state = state.copyWith(messages: newList);
  }

  void clearMessages() {
    state = state.copyWith(messages: []);
  }

  Future<void> retryMessage(int index) async {
    if (index < 0 || index >= state.messages.length) return;
    if (!state.messages[index].isUser) return;

    final query = state.messages[index].text;

    // 해당 메시지 이후의 모든 메시지 삭제
    final newList = state.messages.take(index).toList();
    state = state.copyWith(messages: newList);

    // 다시 전송
    await sendMessage(query);
  }

  Future<void> sendMessage(String query, {String? docName}) async {
    addMessage(query, true);

    final aiMessageIndex = state.messages.length;
    state = state.copyWith(
      messages: [
        ...state.messages,
        const ChatMessage(text: '', isUser: false),
      ],
    );

    // 구글 ID Token 가져오기
    final idToken = await ref.read(authNotifierProvider.notifier).getIdToken();
    final wsUrl = 'ws://127.0.0.1:8000/ws/qa?token=${idToken ?? "12345"}';
    final channel = WebSocketChannel.connect(Uri.parse(wsUrl));

    // 이전 대화 내역 추출 (현재 질문과 빈 AI 메시지 제외)
    final history = state.messages
        .take(state.messages.length - 2)
        .map(
          (m) => {'role': m.isUser ? 'user' : 'assistant', 'content': m.text},
        )
        .toList();

    final request = {
      'query': query,
      'history': history,
      'user_profile': {
        'name': state.profile.name,
        'role': state.profile.role,
        'interests': state.profile.interests,
        'custom_instructions': state.profile.customInstructions,
      },
      if (docName != null) 'filters': {'doc_name': docName},
    };

    channel.sink.add(jsonEncode(request));

    String fullAnswer = '';

    channel.stream.listen(
      (data) {
        final Map<String, dynamic> responseJson = jsonDecode(data);
        final String type = responseJson['type'] ?? '';
        final dynamic payload = responseJson['payload'];

        if (type == 'token') {
          fullAnswer += payload.toString();
          _updateAiMessage(aiMessageIndex, fullAnswer);
        } else if (type == 'metadata') {
          final List<String> images = List<String>.from(
            payload['image_paths'] ?? [],
          );
          final String traceId = payload['trace_id'] ?? '';
          final String displayAnswer = payload['final_answer'] ?? fullAnswer;
          _updateAiMessage(
            aiMessageIndex,
            displayAnswer,
            images: images,
            traceId: traceId,
          );
        } else if (type == 'error') {
          _updateAiMessage(aiMessageIndex, 'Error: $payload');
        } else if (responseJson.containsKey('answer')) {
          fullAnswer += responseJson['answer'];
          _updateAiMessage(aiMessageIndex, fullAnswer);
        }
      },
      onDone: () => channel.sink.close(),
      onError: (error) =>
          _updateAiMessage(aiMessageIndex, 'Connection Error: $error'),
    );
  }

  void _updateAiMessage(
    int index,
    String text, {
    List<String>? images,
    String? traceId,
  }) {
    final newList = List<ChatMessage>.from(state.messages);
    newList[index] = ChatMessage(
      text: text,
      isUser: false,
      images: images,
      traceId: traceId,
    );
    state = state.copyWith(messages: newList);
  }
}
