import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../provider/document_provider.dart';
import '../../../core/constants/app_theme_constants.dart';
import '../../../core/models/app_models.dart';

class DocumentListView extends ConsumerWidget {
  const DocumentListView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final docsAsync = ref.watch(documentListProvider);

    return Scaffold(
      backgroundColor: AppColors.stitchBackground,
      body: CustomScrollView(
        slivers: [
          // Header Section
          const SliverToBoxAdapter(
            child: Padding(
              padding: EdgeInsets.only(
                left: 24,
                right: 24,
                top: 48,
                bottom: 24,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '지식 베이스',
                    style: TextStyle(
                      color: AppColors.stitchPrimary,
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                  SizedBox(height: 4),
                  Text(
                    '매뉴얼 관리',
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.w800,
                      color: AppColors.stitchTextPrimary,
                      letterSpacing: -1.0,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'RAG AI 답변 생성을 위해 문서를 업로드하고 활성화하세요.',
                    style: TextStyle(
                      color: AppColors.stitchTextSecondary,
                      fontSize: 15,
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Upload Button (Wide)
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
              child: _UploadButton(
                onTap: () {
                  // Upload Logic Trigger (Maybe via modal or file picker)
                  // For now, assume SideMenu handles it or add logic here
                },
              ),
            ),
          ),

          // Grid Content
          docsAsync.when(
            data: (docs) {
              if (docs.isEmpty) {
                return const SliverFillRemaining(
                  child: Center(
                    child: Text(
                      'No documents found.',
                      style: TextStyle(color: AppColors.stitchTextDim),
                    ),
                  ),
                );
              }

              return SliverPadding(
                padding: const EdgeInsets.all(24),
                sliver: SliverGrid(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2, // 2 Column Grid like HTML
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    childAspectRatio: 1.6, // Aspect Ratio for Card
                  ),
                  delegate: SliverChildBuilderDelegate((context, index) {
                    final doc = docs[index];
                    // First doc active simulation
                    final isActive = index == 0;

                    return DocumentCard(
                      doc: doc,
                      isActive: isActive,
                      onDelete: () => ref
                          .read(documentListProvider.notifier)
                          .deleteDocument(doc.filename),
                    );
                  }, childCount: docs.length),
                ),
              );
            },
            loading: () => const SliverFillRemaining(
              child: Center(
                child: CircularProgressIndicator(
                  color: AppColors.stitchPrimary,
                ),
              ),
            ),
            error: (err, stack) => SliverFillRemaining(
              child: Center(
                child: Text(
                  'Error loading docs: $err',
                  style: const TextStyle(color: Colors.red),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _UploadButton extends StatelessWidget {
  final VoidCallback onTap;
  const _UploadButton({required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        height: 100, // h-24 equivalent
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: AppColors.stitchBorderSoft,
            style: BorderStyle
                .none, // Dotted border difficult in standard Flutter without package, using custom painter or dashed decoration
            // For simplicity, using solid light border or customized DottedBorder package if available.
            // Let's use standard border for now, maybe Dashed later.
          ),
          boxShadow: [
            BoxShadow(
              color: AppColors.stitchPrimary.withValues(alpha: 0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        // Dashed border simulation with custom painter can be added here
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: AppColors.stitchPrimary.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.add_rounded,
                color: AppColors.stitchPrimary,
                size: 28,
              ),
            ),
            const SizedBox(width: 16),
            Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '새 매뉴얼 업로드',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppColors.stitchTextPrimary,
                  ),
                ),
                Text(
                  'PDF, DOCX 최대 20MB',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.stitchTextDim.withValues(alpha: 0.8),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class DocumentCard extends StatelessWidget {
  final DocumentModel doc;
  final bool isActive;
  final VoidCallback onDelete;

  const DocumentCard({
    super.key,
    required this.doc,
    required this.isActive,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.stitchBorderSoft),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: Icon & Toggle
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: isActive
                      ? Colors.green.withValues(alpha: 0.1)
                      : Colors.blue.withValues(
                          alpha: 0.1,
                        ), // Green-50 / Blue-50
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Icon(
                  isActive
                      ? Icons.check_circle_outlined
                      : Icons.description_outlined,
                  color: isActive ? Colors.green : Colors.blue,
                  size: 24,
                ),
              ),
              // Toggle Switch (Visual Only)
              Container(
                width: 44,
                height: 24,
                padding: const EdgeInsets.all(2),
                decoration: BoxDecoration(
                  color: isActive
                      ? AppColors.stitchPrimary
                      : AppColors.stitchBorder,
                  borderRadius: BorderRadius.circular(12),
                ),
                alignment: isActive
                    ? Alignment.centerRight
                    : Alignment.centerLeft,
                child: Container(
                  width: 20,
                  height: 20,
                  decoration: const BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.white,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black12,
                        blurRadius: 2,
                        offset: Offset(0, 1),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),

          const Spacer(),

          // Title
          Text(
            doc.filename,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.bold,
              color: AppColors.stitchTextPrimary,
              height: 1.3,
            ),
          ),
          const SizedBox(height: 4),

          // Metadata
          const Text(
            '2일 전 업로드됨', // Mock
            style: TextStyle(fontSize: 11, color: AppColors.stitchTextDim),
          ),

          const SizedBox(height: 16),

          // Status Footer
          Container(
            padding: const EdgeInsets.only(top: 12),
            decoration: const BoxDecoration(
              border: Border(
                top: BorderSide(color: AppColors.stitchBorderSoft),
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 6,
                  height: 6,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isActive
                        ? Colors.greenAccent[700]
                        : AppColors.stitchTextDim,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  isActive ? '채팅 활성 중' : '비활성화',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: isActive
                        ? AppColors.stitchTextSecondary
                        : AppColors.stitchTextDim,
                  ),
                ),
                const Spacer(),
                InkWell(
                  onTap: onDelete,
                  borderRadius: BorderRadius.circular(8),
                  child: const Padding(
                    padding: EdgeInsets.all(4.0),
                    child: Icon(
                      Icons.delete_outline_rounded,
                      size: 16,
                      color: AppColors.stitchTextDim,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
