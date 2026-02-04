import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/network/api_client.dart';
import '../../../core/models/app_models.dart';

part 'document_provider.g.dart';

@riverpod
class DocumentList extends _$DocumentList {
  @override
  FutureOr<List<DocumentModel>> build() async {
    return _fetchDocuments();
  }

  Future<List<DocumentModel>> _fetchDocuments() async {
    final dio = ref.read(dioProvider);
    final response = await dio.get('/documents');

    final List<dynamic> docsJson = response.data['documents'];
    return docsJson.map((json) => DocumentModel.fromJson(json)).toList();
  }

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
