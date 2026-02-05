// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'app_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

DocumentModel _$DocumentModelFromJson(Map<String, dynamic> json) {
  return _DocumentModel.fromJson(json);
}

/// @nodoc
mixin _$DocumentModel {
  String get filename => throw _privateConstructorUsedError;
  String? get title => throw _privateConstructorUsedError;

  /// Serializes this DocumentModel to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DocumentModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DocumentModelCopyWith<DocumentModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DocumentModelCopyWith<$Res> {
  factory $DocumentModelCopyWith(
    DocumentModel value,
    $Res Function(DocumentModel) then,
  ) = _$DocumentModelCopyWithImpl<$Res, DocumentModel>;
  @useResult
  $Res call({String filename, String? title});
}

/// @nodoc
class _$DocumentModelCopyWithImpl<$Res, $Val extends DocumentModel>
    implements $DocumentModelCopyWith<$Res> {
  _$DocumentModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DocumentModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? filename = null, Object? title = freezed}) {
    return _then(
      _value.copyWith(
            filename: null == filename
                ? _value.filename
                : filename // ignore: cast_nullable_to_non_nullable
                      as String,
            title: freezed == title
                ? _value.title
                : title // ignore: cast_nullable_to_non_nullable
                      as String?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$DocumentModelImplCopyWith<$Res>
    implements $DocumentModelCopyWith<$Res> {
  factory _$$DocumentModelImplCopyWith(
    _$DocumentModelImpl value,
    $Res Function(_$DocumentModelImpl) then,
  ) = __$$DocumentModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String filename, String? title});
}

/// @nodoc
class __$$DocumentModelImplCopyWithImpl<$Res>
    extends _$DocumentModelCopyWithImpl<$Res, _$DocumentModelImpl>
    implements _$$DocumentModelImplCopyWith<$Res> {
  __$$DocumentModelImplCopyWithImpl(
    _$DocumentModelImpl _value,
    $Res Function(_$DocumentModelImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of DocumentModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? filename = null, Object? title = freezed}) {
    return _then(
      _$DocumentModelImpl(
        filename: null == filename
            ? _value.filename
            : filename // ignore: cast_nullable_to_non_nullable
                  as String,
        title: freezed == title
            ? _value.title
            : title // ignore: cast_nullable_to_non_nullable
                  as String?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$DocumentModelImpl implements _DocumentModel {
  const _$DocumentModelImpl({required this.filename, this.title});

  factory _$DocumentModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$DocumentModelImplFromJson(json);

  @override
  final String filename;
  @override
  final String? title;

  @override
  String toString() {
    return 'DocumentModel(filename: $filename, title: $title)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DocumentModelImpl &&
            (identical(other.filename, filename) ||
                other.filename == filename) &&
            (identical(other.title, title) || other.title == title));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, filename, title);

  /// Create a copy of DocumentModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DocumentModelImplCopyWith<_$DocumentModelImpl> get copyWith =>
      __$$DocumentModelImplCopyWithImpl<_$DocumentModelImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DocumentModelImplToJson(this);
  }
}

abstract class _DocumentModel implements DocumentModel {
  const factory _DocumentModel({
    required final String filename,
    final String? title,
  }) = _$DocumentModelImpl;

  factory _DocumentModel.fromJson(Map<String, dynamic> json) =
      _$DocumentModelImpl.fromJson;

  @override
  String get filename;
  @override
  String? get title;

  /// Create a copy of DocumentModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DocumentModelImplCopyWith<_$DocumentModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

QAResponse _$QAResponseFromJson(Map<String, dynamic> json) {
  return _QAResponse.fromJson(json);
}

/// @nodoc
mixin _$QAResponse {
  String get answer => throw _privateConstructorUsedError;
  @JsonKey(name: 'retrieved_images')
  List<String>? get retrievedImages => throw _privateConstructorUsedError;
  @JsonKey(name: 'doc_name')
  String? get docName => throw _privateConstructorUsedError;
  @JsonKey(name: 'trace_id')
  String? get traceId => throw _privateConstructorUsedError;
  @JsonKey(name: 'session_id')
  String? get sessionId => throw _privateConstructorUsedError;

  /// Serializes this QAResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of QAResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $QAResponseCopyWith<QAResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $QAResponseCopyWith<$Res> {
  factory $QAResponseCopyWith(
    QAResponse value,
    $Res Function(QAResponse) then,
  ) = _$QAResponseCopyWithImpl<$Res, QAResponse>;
  @useResult
  $Res call({
    String answer,
    @JsonKey(name: 'retrieved_images') List<String>? retrievedImages,
    @JsonKey(name: 'doc_name') String? docName,
    @JsonKey(name: 'trace_id') String? traceId,
    @JsonKey(name: 'session_id') String? sessionId,
  });
}

/// @nodoc
class _$QAResponseCopyWithImpl<$Res, $Val extends QAResponse>
    implements $QAResponseCopyWith<$Res> {
  _$QAResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of QAResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? answer = null,
    Object? retrievedImages = freezed,
    Object? docName = freezed,
    Object? traceId = freezed,
    Object? sessionId = freezed,
  }) {
    return _then(
      _value.copyWith(
            answer: null == answer
                ? _value.answer
                : answer // ignore: cast_nullable_to_non_nullable
                      as String,
            retrievedImages: freezed == retrievedImages
                ? _value.retrievedImages
                : retrievedImages // ignore: cast_nullable_to_non_nullable
                      as List<String>?,
            docName: freezed == docName
                ? _value.docName
                : docName // ignore: cast_nullable_to_non_nullable
                      as String?,
            traceId: freezed == traceId
                ? _value.traceId
                : traceId // ignore: cast_nullable_to_non_nullable
                      as String?,
            sessionId: freezed == sessionId
                ? _value.sessionId
                : sessionId // ignore: cast_nullable_to_non_nullable
                      as String?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$QAResponseImplCopyWith<$Res>
    implements $QAResponseCopyWith<$Res> {
  factory _$$QAResponseImplCopyWith(
    _$QAResponseImpl value,
    $Res Function(_$QAResponseImpl) then,
  ) = __$$QAResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String answer,
    @JsonKey(name: 'retrieved_images') List<String>? retrievedImages,
    @JsonKey(name: 'doc_name') String? docName,
    @JsonKey(name: 'trace_id') String? traceId,
    @JsonKey(name: 'session_id') String? sessionId,
  });
}

/// @nodoc
class __$$QAResponseImplCopyWithImpl<$Res>
    extends _$QAResponseCopyWithImpl<$Res, _$QAResponseImpl>
    implements _$$QAResponseImplCopyWith<$Res> {
  __$$QAResponseImplCopyWithImpl(
    _$QAResponseImpl _value,
    $Res Function(_$QAResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of QAResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? answer = null,
    Object? retrievedImages = freezed,
    Object? docName = freezed,
    Object? traceId = freezed,
    Object? sessionId = freezed,
  }) {
    return _then(
      _$QAResponseImpl(
        answer: null == answer
            ? _value.answer
            : answer // ignore: cast_nullable_to_non_nullable
                  as String,
        retrievedImages: freezed == retrievedImages
            ? _value._retrievedImages
            : retrievedImages // ignore: cast_nullable_to_non_nullable
                  as List<String>?,
        docName: freezed == docName
            ? _value.docName
            : docName // ignore: cast_nullable_to_non_nullable
                  as String?,
        traceId: freezed == traceId
            ? _value.traceId
            : traceId // ignore: cast_nullable_to_non_nullable
                  as String?,
        sessionId: freezed == sessionId
            ? _value.sessionId
            : sessionId // ignore: cast_nullable_to_non_nullable
                  as String?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$QAResponseImpl implements _QAResponse {
  const _$QAResponseImpl({
    required this.answer,
    @JsonKey(name: 'retrieved_images') final List<String>? retrievedImages,
    @JsonKey(name: 'doc_name') this.docName,
    @JsonKey(name: 'trace_id') this.traceId,
    @JsonKey(name: 'session_id') this.sessionId,
  }) : _retrievedImages = retrievedImages;

  factory _$QAResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$QAResponseImplFromJson(json);

  @override
  final String answer;
  final List<String>? _retrievedImages;
  @override
  @JsonKey(name: 'retrieved_images')
  List<String>? get retrievedImages {
    final value = _retrievedImages;
    if (value == null) return null;
    if (_retrievedImages is EqualUnmodifiableListView) return _retrievedImages;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  @JsonKey(name: 'doc_name')
  final String? docName;
  @override
  @JsonKey(name: 'trace_id')
  final String? traceId;
  @override
  @JsonKey(name: 'session_id')
  final String? sessionId;

  @override
  String toString() {
    return 'QAResponse(answer: $answer, retrievedImages: $retrievedImages, docName: $docName, traceId: $traceId, sessionId: $sessionId)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$QAResponseImpl &&
            (identical(other.answer, answer) || other.answer == answer) &&
            const DeepCollectionEquality().equals(
              other._retrievedImages,
              _retrievedImages,
            ) &&
            (identical(other.docName, docName) || other.docName == docName) &&
            (identical(other.traceId, traceId) || other.traceId == traceId) &&
            (identical(other.sessionId, sessionId) ||
                other.sessionId == sessionId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    answer,
    const DeepCollectionEquality().hash(_retrievedImages),
    docName,
    traceId,
    sessionId,
  );

  /// Create a copy of QAResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$QAResponseImplCopyWith<_$QAResponseImpl> get copyWith =>
      __$$QAResponseImplCopyWithImpl<_$QAResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$QAResponseImplToJson(this);
  }
}

abstract class _QAResponse implements QAResponse {
  const factory _QAResponse({
    required final String answer,
    @JsonKey(name: 'retrieved_images') final List<String>? retrievedImages,
    @JsonKey(name: 'doc_name') final String? docName,
    @JsonKey(name: 'trace_id') final String? traceId,
    @JsonKey(name: 'session_id') final String? sessionId,
  }) = _$QAResponseImpl;

  factory _QAResponse.fromJson(Map<String, dynamic> json) =
      _$QAResponseImpl.fromJson;

  @override
  String get answer;
  @override
  @JsonKey(name: 'retrieved_images')
  List<String>? get retrievedImages;
  @override
  @JsonKey(name: 'doc_name')
  String? get docName;
  @override
  @JsonKey(name: 'trace_id')
  String? get traceId;
  @override
  @JsonKey(name: 'session_id')
  String? get sessionId;

  /// Create a copy of QAResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$QAResponseImplCopyWith<_$QAResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
