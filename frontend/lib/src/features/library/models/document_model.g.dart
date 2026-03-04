// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'document_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$DocumentModelImpl _$$DocumentModelImplFromJson(Map<String, dynamic> json) =>
    _$DocumentModelImpl(
      filename: json['filename'] as String,
      title: json['title'] as String,
      isActive: json['is_active'] as bool? ?? true,
      uploadTime: json['uploadTime'] as String?,
    );

Map<String, dynamic> _$$DocumentModelImplToJson(_$DocumentModelImpl instance) =>
    <String, dynamic>{
      'filename': instance.filename,
      'title': instance.title,
      'is_active': instance.isActive,
      'uploadTime': instance.uploadTime,
    };
