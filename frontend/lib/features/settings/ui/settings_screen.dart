import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../core/constants/app_theme_constants.dart';
import '../../../core/auth/auth_provider.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authNotifierProvider).user;

    return Scaffold(
      backgroundColor: AppColors.stitchBackground,
      body: CustomScrollView(
        slivers: [
          // Header
          const SliverToBoxAdapter(
            child: Padding(
              padding: EdgeInsets.only(
                top: 48,
                bottom: 24,
                left: 24,
                right: 24,
              ),
              child: Center(
                child: Text(
                  '설정',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                    color: AppColors.stitchTextPrimary,
                  ),
                ),
              ),
            ),
          ),

          // Profile Section
          SliverToBoxAdapter(
            child: Column(
              children: [
                Stack(
                  alignment: Alignment.bottomRight,
                  children: [
                    Container(
                      width: 96,
                      height: 96,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 4),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.1),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                        image: user?.photoUrl != null
                            ? DecorationImage(
                                image: NetworkImage(user!.photoUrl!),
                                fit: BoxFit.cover,
                              )
                            : null,
                        color: user?.photoUrl == null
                            ? AppColors.stitchPrimary.withValues(alpha: 0.1)
                            : null,
                      ),
                      child: user?.photoUrl == null
                          ? const Icon(
                              Icons.person,
                              size: 48,
                              color: AppColors.stitchPrimary,
                            )
                          : null,
                    ),
                    Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: AppColors.stitchPrimary,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 2),
                      ),
                      child: const Icon(
                        Icons.edit,
                        size: 14,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  user?.displayName ?? 'Guest User',
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: AppColors.stitchTextPrimary,
                  ),
                ),
                Text(
                  user?.email ?? 'guest@example.com',
                  style: const TextStyle(
                    fontSize: 14,
                    color: AppColors.stitchTextDim,
                  ),
                ),
                const SizedBox(height: 32),
              ],
            ),
          ),

          // Settings Group 1
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    _SettingsTile(
                      icon: Icons.dark_mode_outlined,
                      title: '테마 설정',
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          // 3-Way Selector Simulation (Segmented Control style)
                          Container(
                            height: 32,
                            decoration: BoxDecoration(
                              color: AppColors.stitchBackground,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Row(
                              children: [
                                _ThemeIcon(
                                  icon: Icons.light_mode,
                                  isSelected: true,
                                ),
                                _ThemeIcon(
                                  icon: Icons.dark_mode,
                                  isSelected: false,
                                ),
                                _ThemeIcon(
                                  icon: Icons.brightness_auto,
                                  isSelected: false,
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          const SliverToBoxAdapter(child: SizedBox(height: 24)),

          // Logout Button
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Material(
                  color: Colors.transparent,
                  child: InkWell(
                    onTap: () =>
                        ref.read(authNotifierProvider.notifier).signOut(),
                    borderRadius: BorderRadius.circular(20),
                    child: const Padding(
                      padding: EdgeInsets.all(16),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.logout_rounded, color: Colors.red),
                          SizedBox(width: 8),
                          Text(
                            '로그아웃',
                            style: TextStyle(
                              color: Colors.red,
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),

          const SliverToBoxAdapter(child: SizedBox(height: 48)),

          // Footer
          const SliverToBoxAdapter(
            child: Column(
              children: [
                Text(
                  'AI Manual Chatbot v2.4.0',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.stitchTextDim,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  '© 2026 AI Solutions Co.',
                  style: TextStyle(
                    fontSize: 10,
                    color: AppColors.stitchTextDim,
                  ),
                ),
              ],
            ),
          ),

          const SliverToBoxAdapter(child: SizedBox(height: 48)),
        ],
      ),
    );
  }
}

class _SettingsTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final Widget? trailing;

  const _SettingsTile({required this.icon, required this.title, this.trailing});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppColors.stitchPrimary.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: AppColors.stitchPrimary, size: 20),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w500,
                color: AppColors.stitchTextPrimary,
              ),
            ),
          ),
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}

class _ThemeIcon extends StatelessWidget {
  final IconData icon;
  final bool isSelected;

  const _ThemeIcon({required this.icon, required this.isSelected});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.all(2),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(6),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.1),
                    blurRadius: 2,
                    offset: const Offset(0, 1),
                  ),
                ]
              : null,
        ),
        child: Icon(
          icon,
          size: 16,
          color: isSelected
              ? AppColors.stitchTextPrimary
              : AppColors.stitchTextDim,
        ),
      ),
    );
  }
}
