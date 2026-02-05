// ignore_for_file: invalid_annotation_target

import 'package:freezed_annotation/freezed_annotation.dart';

part 'app_models.freezed.dart';
part 'app_models.g.dart';

@freezed
class DocumentModel with _$DocumentModel {
  const factory DocumentModel({required String filename, String? title}) =
      _DocumentModel;

  factory DocumentModel.fromJson(Map<String, dynamic> json) =>
      _$DocumentModelFromJson(json);
}

@freezed
class QAResponse with _$QAResponse {
  const factory QAResponse({
    required String answer,
    @JsonKey(name: 'retrieved_images') List<String>? retrievedImages,
    @JsonKey(name: 'doc_name') String? docName,
    @JsonKey(name: 'trace_id') String? traceId,
    @JsonKey(name: 'session_id') String? sessionId,
  }) = _QAResponse;

  factory QAResponse.fromJson(Map<String, dynamic> json) =>
      _$QAResponseFromJson(json);
}
