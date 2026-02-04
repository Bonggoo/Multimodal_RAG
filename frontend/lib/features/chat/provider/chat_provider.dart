import 'dart:convert';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

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

@riverpod
class Chat extends _$Chat {
  @override
  List<ChatMessage> build() {
    return [];
  }

  void addMessage(
    String text,
    bool isUser, {
    List<String>? images,
    String? traceId,
  }) {
    state = [
      ...state,
      ChatMessage(text: text, isUser: isUser, images: images, traceId: traceId),
    ];
  }

  Future<void> sendMessage(String query, {String? docName}) async {
    addMessage(query, true);

    final aiMessageIndex = state.length;
    state = [...state, const ChatMessage(text: '', isUser: false)];

    const wsUrl = 'ws://127.0.0.1:8000/ws/qa?token=12345';
    final channel = WebSocketChannel.connect(Uri.parse(wsUrl));

    final request = {
      'query': query,
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
          // Legacy support for direct answer key
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
    final newList = List<ChatMessage>.from(state);
    newList[index] = ChatMessage(
      text: text,
      isUser: false,
      images: images,
      traceId: traceId,
    );
    state = newList;
  }
}
