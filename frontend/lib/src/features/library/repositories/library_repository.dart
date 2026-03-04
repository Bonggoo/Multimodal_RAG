import 'dart:io';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/api/dio_provider.dart';
import '../models/document_model.dart';

part 'library_repository.g.dart';

class LibraryRepository {
  final Dio _dio;
  const LibraryRepository(this._dio);

  Future<List<DocumentModel>> getDocuments() async {
    final response = await _dio.get('/documents');
    final data = response.data['documents'] as List;
    return data
        .map((e) => DocumentModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Map<String, dynamic>> uploadDocument(
    File file, {
    bool force = false,
    void Function(int sent, int total)? onSendProgress,
  }) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(
        file.path,
        filename: file.path.split('/').last,
      ),
    });

    final response = await _dio.post(
      '/ingest',
      queryParameters: {'force': force},
      data: formData,
      onSendProgress: onSendProgress,
    );
    return response.data as Map<String, dynamic>;
  }

  Future<void> toggleDocument(String docName, bool isActive) async {
    await _dio.post(
      '/documents/$docName/toggle',
      data: {'is_active': isActive},
    );
  }

  Future<void> deleteDocument(String docName) async {
    await _dio.delete('/documents/$docName');
  }
}

@riverpod
LibraryRepository libraryRepository(LibraryRepositoryRef ref) {
  return LibraryRepository(ref.watch(dioProvider));
}
