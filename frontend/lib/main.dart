import 'package:flutter/material.dart';
import 'core/providers/global_providers.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'core/theme/spectral_omega_theme.dart';
import 'features/chat/ui/chat_screen.dart';
import 'features/documents/ui/document_list_view.dart';
import 'core/constants/app_theme_constants.dart';
import 'package:google_fonts/google_fonts.dart';
import 'core/auth/auth_provider.dart';
import 'features/settings/ui/settings_screen.dart';

void main() {
  runApp(const ProviderScope(child: SpectralOmegaApp()));
}

class SpectralOmegaApp extends StatelessWidget {
  const SpectralOmegaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Stitch AI Manual',
      debugShowCheckedModeBanner: false,
      theme: SpectralOmegaTheme.lightTheme, // Switch to Light Theme
      home: const MainLayout(),
    );
  }
}

class MainLayout extends ConsumerWidget {
  const MainLayout({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isInitialized = ref.watch(
      authNotifierProvider.select((s) => s.isInitialized),
    );
    final hasUser = ref.watch(
      authNotifierProvider.select((s) => s.user != null),
    );
    final navIndex = ref.watch(navigationIndexProvider);

    if (!isInitialized) {
      return const Scaffold(
        backgroundColor: Colors.white,
        body: Center(
          child: CircularProgressIndicator(color: AppColors.stitchPrimary),
        ),
      );
    }

    if (!hasUser) {
      return const LoginScreen();
    }

    return Scaffold(
      backgroundColor: AppColors.stitchBackground,
      body: Stack(
        children: [
          // Main Content Area
          Positioned.fill(
            bottom: 80, // Reserve space for the dock
            child: IndexedStack(
              index: navIndex,
              children: const [
                ChatScreen(), // Index 0
                DocumentListView(), // Index 1
                SettingsScreen(), // Index 2
              ],
            ),
          ),

          // Bottom Navigation Bar (Docked)
          Positioned(
            bottom: 20,
            left: 24,
            right: 24,
            child: Container(
              height: 64, // Compact height
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(32), // Pill shape
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.1),
                    blurRadius: 20,
                    offset: const Offset(0, 8),
                  ),
                ],
                border: Border.all(color: AppColors.stitchBorderSoft),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _NavIcon(
                    icon: Icons.chat_bubble_outline_rounded,
                    label: '채팅',
                    isSelected: navIndex == 0,
                    onTap: () =>
                        ref.read(navigationIndexProvider.notifier).state = 0,
                  ),
                  _NavIcon(
                    icon: Icons.book_outlined,
                    label: '라이브러리',
                    isSelected: navIndex == 1,
                    onTap: () =>
                        ref.read(navigationIndexProvider.notifier).state = 1,
                  ),
                  _NavIcon(
                    icon: Icons.settings_outlined,
                    label: '설정',
                    isSelected: navIndex == 2,
                    onTap: () =>
                        ref.read(navigationIndexProvider.notifier).state = 2,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _NavIcon extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _NavIcon({
    required this.icon,
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: 64,
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: isSelected
            ? BoxDecoration(
                color: AppColors.stitchPrimary.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(16),
              )
            : null,
        child: Column(
          children: [
            Icon(
              icon,
              color: isSelected
                  ? AppColors.stitchPrimary
                  : AppColors.stitchTextDim,
              size: 26,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                color: isSelected
                    ? AppColors.stitchPrimary
                    : AppColors.stitchTextDim,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Login Screen (Legacy Dark Style -> Adapted to Light or Kept Dark?)
// User requested: "로그인 화면만 놔두고" -> Assuming Keep Logic, but maybe style can be adapted.
// Let's keep the logic but update style to match Stitch Light for consistency.
class LoginScreen extends ConsumerWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authNotifierProvider);

    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Container(
          width: 400,
          padding: const EdgeInsets.all(48),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(32),
            boxShadow: [AppShadows.iosSoft], // Stitch Shadow
            border: Border.all(color: AppColors.stitchBorderSoft),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.stitchPrimary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(24),
                ),
                child: const Icon(
                  Icons.bolt,
                  color: AppColors.stitchPrimary,
                  size: 48,
                ),
              ),
              const SizedBox(height: 32),
              const Text(
                'AI MANUAL',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                  color: AppColors.stitchTextPrimary,
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Sign in to access your library',
                style: TextStyle(
                  color: AppColors.stitchTextSecondary,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 48),
              if (authState.isLoading)
                const CircularProgressIndicator(color: AppColors.stitchPrimary)
              else ...[
                ElevatedButton(
                  onPressed: () =>
                      ref.read(authNotifierProvider.notifier).signIn(),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.stitchPrimary,
                    foregroundColor: Colors.white,
                    minimumSize: const Size(double.infinity, 56),
                    elevation: 5,
                    shadowColor: AppColors.stitchPrimary.withValues(alpha: 0.4),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.login),
                      const SizedBox(width: 12),
                      Text(
                        'Continue with Google',
                        style: GoogleFonts.inter(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ),
                ),
                if (authState.errorMessage != null) ...[
                  const SizedBox(height: 16),
                  Text(
                    authState.errorMessage!,
                    style: const TextStyle(
                      color: AppColors.accentRose,
                      fontSize: 12,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ],
            ],
          ),
        ),
      ),
    );
  }
}
