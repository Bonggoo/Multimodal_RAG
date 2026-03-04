import 'package:freezed_annotation/freezed_annotation.dart';

part 'chat_session.freezed.dart';
part 'chat_session.g.dart';

@freezed
class ChatSession with _$ChatSession {
  const factory ChatSession({
    @JsonKey(name: 'session_id') required String sessionId,
    required String title,
    @JsonKey(name: 'created_at') required String createdAt,
    @JsonKey(name: 'last_message_at') required String lastMessageAt,
  }) = _ChatSession;

  factory ChatSession.fromJson(Map<String, dynamic> json) =>
      _$ChatSessionFromJson(json);
}
