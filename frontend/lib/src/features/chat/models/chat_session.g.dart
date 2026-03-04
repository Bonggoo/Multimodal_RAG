// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'chat_session.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ChatSessionImpl _$$ChatSessionImplFromJson(Map<String, dynamic> json) =>
    _$ChatSessionImpl(
      sessionId: json['session_id'] as String,
      title: json['title'] as String,
      createdAt: json['created_at'] as String,
      lastMessageAt: json['last_message_at'] as String,
    );

Map<String, dynamic> _$$ChatSessionImplToJson(_$ChatSessionImpl instance) =>
    <String, dynamic>{
      'session_id': instance.sessionId,
      'title': instance.title,
      'created_at': instance.createdAt,
      'last_message_at': instance.lastMessageAt,
    };
