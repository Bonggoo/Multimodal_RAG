import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'core/theme/spectral_omega_theme.dart';
import 'features/chat/ui/chat_screen.dart';
import 'features/documents/ui/document_list_view.dart';
import 'features/documents/provider/document_provider.dart';
import 'package:file_picker/file_picker.dart';
import 'package:dio/dio.dart';
import 'core/network/api_client.dart';
import 'core/constants/app_theme_constants.dart';
import 'package:google_fonts/google_fonts.dart';

void main() {
  runApp(const ProviderScope(child: SpectralOmegaApp()));
}

class SpectralOmegaApp extends StatelessWidget {
  const SpectralOmegaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Spectral Omega RAG',
      debugShowCheckedModeBanner: false,
      theme: SpectralOmegaTheme.darkTheme,
      home: const MainLayout(),
    );
  }
}

class MainLayout extends ConsumerWidget {
  const MainLayout({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: AppColors.primaryBackground,
      body: SelectionArea(
        child: Stack(
          children: [
            Positioned(
              top: -100,
              left: -100,
              child: Container(
                width: 400,
                height: 400,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppColors.accentIndigo.withValues(alpha: 0.1),
                ),
              ),
            ),

            const Row(
              children: [
                SideMenu(),
                Expanded(
                  child: Padding(
                    padding: EdgeInsets.only(top: 24, right: 24, bottom: 24),
                    child: ChatScreen(),
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

class SideMenu extends ConsumerStatefulWidget {
  const SideMenu({super.key});

  @override
  ConsumerState<SideMenu> createState() => _SideMenuState();
}

class _SideMenuState extends ConsumerState<SideMenu> {
  bool _isUploading = false;

  Future<void> _pickAndUpload() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
    );

    if (result != null && result.files.single.path != null) {
      final path = result.files.single.path!;
      final filename = result.files.single.name;

      setState(() => _isUploading = true);

      try {
        final dio = ref.read(dioProvider);
        final formData = FormData.fromMap({
          'file': await MultipartFile.fromFile(path, filename: filename),
        });

        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('⚡ Uploading $filename...'),
            backgroundColor: AppColors.accentIndigo,
            behavior: SnackBarBehavior.floating,
          ),
        );

        await dio.post('/ingest', data: formData);

        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Upload completed! Start chatting.'),
            backgroundColor: Colors.green,
            behavior: SnackBarBehavior.floating,
          ),
        );

        // Wait for background processing and refresh
        await Future.delayed(const Duration(seconds: 2));
        ref.read(documentListProvider.notifier).refresh();
      } catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error: $e'),
            backgroundColor: AppColors.accentRose,
            behavior: SnackBarBehavior.floating,
          ),
        );
      } finally {
        if (mounted) setState(() => _isUploading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 300,
      margin: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppColors.sidebarBackground.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(32),
        border: Border.all(color: AppColors.glassBorder),
      ),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(32.0),
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    gradient: AppColors.primaryGradient,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.accentIndigo.withValues(alpha: 0.4),
                        blurRadius: 20,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: const Icon(Icons.bolt, color: Colors.white, size: 32),
                ),
                const SizedBox(height: 16),
                const Text(
                  'SPECTRAL',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 2.0,
                    color: Colors.white,
                  ),
                ),
                Text(
                  'OMEGA RAG',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.white.withValues(alpha: 0.3),
                    letterSpacing: 4.0,
                  ),
                ),
              ],
            ),
          ),
          const Divider(color: Colors.white10),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            child: Row(
              children: [
                const Icon(
                  Icons.folder_outlined,
                  size: 16,
                  color: AppColors.accentCyan,
                ),
                const SizedBox(width: 8),
                Text(
                  'DOCUMENTS',
                  style: GoogleFonts.outfit(
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textSecondary,
                    letterSpacing: 1.0,
                  ),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(
                    Icons.refresh_rounded,
                    size: 14,
                    color: AppColors.textDim,
                  ),
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                  splashRadius: 16,
                  onPressed: () =>
                      ref.read(documentListProvider.notifier).refresh(),
                  tooltip: 'Refresh documents',
                ),
              ],
            ),
          ),
          const Expanded(child: DocumentListView()),
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: InkWell(
              onTap: _isUploading ? null : _pickAndUpload,
              borderRadius: BorderRadius.circular(20),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: _isUploading ? null : AppColors.primaryGradient,
                  color: _isUploading ? AppColors.textDim : null,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: _isUploading
                      ? []
                      : [
                          BoxShadow(
                            color: AppColors.accentIndigo.withValues(
                              alpha: 0.3,
                            ),
                            blurRadius: 12,
                            offset: const Offset(0, 6),
                          ),
                        ],
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    _isUploading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Icon(Icons.add, color: Colors.white),
                    const SizedBox(width: 12),
                    Text(
                      _isUploading ? 'INDEXING...' : 'NEW DOCUMENT',
                      style: const TextStyle(
                        fontWeight: FontWeight.w900,
                        color: Colors.white,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
