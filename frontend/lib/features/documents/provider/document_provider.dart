import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/network/api_client.dart';
import '../../../core/models/app_models.dart';
import '../../../core/auth/auth_provider.dart';

part 'document_provider.g.dart';

@riverpod
class DocumentList extends _$DocumentList {
  @override
  FutureOr<List<DocumentModel>> build() async {
    // 인증 상태를 감시하여 로그인되지 않은 경우 빈 리스트 반환
    final authState = ref.watch(authNotifierProvider);
    if (authState.user == null) {
      return [];
    }
    return _fetchDocuments();
  }

  Future<List<DocumentModel>> _fetchDocuments() async {
    final dio = ref.read(dioProvider);
    try {
      final response = await dio.get('/documents');
      final List<dynamic> docsJson = response.data['documents'];
      return docsJson.map((json) => DocumentModel.fromJson(json)).toList();
    } catch (e) {
      // 401 에러 등의 경우 빈 리스트 반환 (또는 에러 처리)
      return [];
    }
  }
  // ... rest of the functions

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchDocuments());
  }

  Future<void> deleteDocument(String docName) async {
    final dio = ref.read(dioProvider);
    await dio.delete('/documents/$docName');
    await refresh();
  }
}
