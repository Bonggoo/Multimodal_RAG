// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$DocumentModelImpl _$$DocumentModelImplFromJson(Map<String, dynamic> json) =>
    _$DocumentModelImpl(
      filename: json['filename'] as String,
      title: json['title'] as String?,
    );

Map<String, dynamic> _$$DocumentModelImplToJson(_$DocumentModelImpl instance) =>
    <String, dynamic>{'filename': instance.filename, 'title': instance.title};

_$QAResponseImpl _$$QAResponseImplFromJson(Map<String, dynamic> json) =>
    _$QAResponseImpl(
      answer: json['answer'] as String,
      retrievedImages: (json['retrieved_images'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      docName: json['doc_name'] as String?,
      traceId: json['trace_id'] as String?,
    );

Map<String, dynamic> _$$QAResponseImplToJson(_$QAResponseImpl instance) =>
    <String, dynamic>{
      'answer': instance.answer,
      'retrieved_images': instance.retrievedImages,
      'doc_name': instance.docName,
      'trace_id': instance.traceId,
    };
