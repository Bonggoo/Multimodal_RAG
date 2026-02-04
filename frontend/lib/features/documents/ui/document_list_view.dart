import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../provider/document_provider.dart';
import '../../../core/constants/app_theme_constants.dart';

class DocumentListView extends ConsumerWidget {
  const DocumentListView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final docsAsync = ref.watch(documentListProvider);

    return docsAsync.when(
      data: (docs) {
        if (docs.isEmpty) {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.folder_open_outlined,
                  color: Colors.white24,
                  size: 40,
                ),
                SizedBox(height: 12),
                Text(
                  'No documents yet',
                  style: TextStyle(color: Colors.white24, fontSize: 13),
                ),
              ],
            ),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          itemCount: docs.length,
          itemBuilder: (context, index) {
            final doc = docs[index];
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: DocumentTile(
                title: doc.title ?? doc.filename,
                subtitle: doc.filename,
                onDelete: () => ref
                    .read(documentListProvider.notifier)
                    .deleteDocument(doc.filename),
              ),
            );
          },
        );
      },
      loading: () => const Center(
        child: CircularProgressIndicator(color: AppColors.accentIndigo),
      ),
      error: (e, st) => Padding(
        padding: const EdgeInsets.all(16.0),
        child: Text(
          'Error: $e',
          style: const TextStyle(color: Colors.redAccent, fontSize: 12),
        ),
      ),
    );
  }
}

class DocumentTile extends StatelessWidget {
  final String title;
  final String subtitle;
  final VoidCallback onDelete;

  const DocumentTile({
    super.key,
    required this.title,
    required this.subtitle,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.03),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withValues(alpha: 0.05)),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        title: Text(
          title,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w700,
            color: Colors.white,
          ),
        ),
        subtitle: Text(
          subtitle,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            fontSize: 11,
            color: Colors.white.withValues(alpha: 0.3),
          ),
        ),
        trailing: IconButton(
          icon: const Icon(
            Icons.delete_outline_rounded,
            size: 18,
            color: AppColors.accentRose,
          ),
          onPressed: () {
            showDialog(
              context: context,
              builder: (ctx) => AlertDialog(
                backgroundColor: AppColors.sidebarBackground,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(24),
                ),
                title: const Text('Delete Document'),
                content: const Text(
                  'Are you sure you want to remove this document?',
                ),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(ctx),
                    child: const Text('Cancel'),
                  ),
                  TextButton(
                    onPressed: () {
                      onDelete();
                      Navigator.pop(ctx);
                    },
                    child: const Text(
                      'Delete',
                      style: TextStyle(color: Colors.redAccent),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}
