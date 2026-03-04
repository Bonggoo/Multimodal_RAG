import 'dart:io';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/document_model.dart';
import '../repositories/library_repository.dart';

part 'library_provider.g.dart';

@riverpod
class LibraryUploadProgress extends _$LibraryUploadProgress {
  @override
  double? build() => null;

  void setProgress(double? progress) => state = progress;
}

@riverpod
class LibraryNotifier extends _$LibraryNotifier {
  @override
  FutureOr<List<DocumentModel>> build() async {
    return ref.watch(libraryRepositoryProvider).getDocuments();
  }

  Future<void> uploadDocument(String filePath) async {
    final repository = ref.read(libraryRepositoryProvider);
    final progressNotifier = ref.read(libraryUploadProgressProvider.notifier);

    // list를 유지하며 프로그레스만 업데이트하기 위해 state를 강제로 loading으로 바꾸지 않음
    try {
      progressNotifier.setProgress(0.0);
      final file = File(filePath);
      await repository.uploadDocument(
        file,
        onSendProgress: (sent, total) {
          if (total > 0) {
            progressNotifier.setProgress(sent / total);
          }
        },
      );
      // 업로드 완료 후 잠깐 100% 보여줌
      progressNotifier.setProgress(1.0);
      await Future.delayed(const Duration(milliseconds: 500));
      progressNotifier.setProgress(null);

      await refresh();
    } catch (e) {
      progressNotifier.setProgress(null);
      rethrow;
    }
  }

  Future<void> toggleDocument(String docName, bool isActive) async {
    final repository = ref.read(libraryRepositoryProvider);
    try {
      await repository.toggleDocument(docName, isActive);
      // 백엔드 업데이트 후 목록을 다시 가져와서 UI가 정확한 상태를 유지하도록 함
      await refresh();
    } catch (e) {
      // 에러 발생 시 원래 상태를 유지하거나 사용자에게 알림 (여기서는 rethrow하여 스낵바 등 처리 유도)
      rethrow;
    }
  }

  Future<void> deleteDocument(String docName) async {
    final repository = ref.read(libraryRepositoryProvider);
    await repository.deleteDocument(docName);
    await refresh();
  }

  Future<void> refresh() async {
    // refresh 시에는 기존 데이터를 유지하며 로딩 표시 (AsyncValue.guard 권장)
    state = await AsyncValue.guard(
      () => ref.read(libraryRepositoryProvider).getDocuments(),
    );
  }
}
