import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_theme.dart';
import 'providers/auth_provider.dart';

class LoginScreen extends ConsumerWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: Stack(
        children: [
          // Background dynamic gradient or image
          _buildBackground(),

          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 32),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Glassmorphic Logo Container
                    _buildLogoSection(context),
                    const SizedBox(height: 48),

                    // Welcome Text
                    _buildWelcomeText(context),
                    const SizedBox(height: 64),

                    // Google Login Button
                    _buildGoogleSignInButton(context, ref),

                    const SizedBox(height: 32),
                    _buildFooterText(context),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBackground() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFF0F172A), // Dark slate
            Color(0xFF1E293B),
            Color(0xFF0F172A),
          ],
        ),
      ),
      child: Stack(
        children: [
          Positioned(
            top: -100,
            right: -100,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppColors.primary.withValues(alpha: 0.1),
              ),
            ),
          ),
          Positioned(
            bottom: -50,
            left: -50,
            child: Container(
              width: 250,
              height: 250,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.blueAccent.withValues(alpha: 0.05),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLogoSection(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(32),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.05),
            borderRadius: BorderRadius.circular(32),
            border: Border.all(
              color: Colors.white.withValues(alpha: 0.1),
              width: 1.5,
            ),
          ),
          child: const Icon(
            Icons.auto_awesome,
            color: AppColors.primary,
            size: 64,
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeText(BuildContext context) {
    return const Column(
      children: [
        Text(
          'Multimodal RAG',
          style: TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.w900,
            color: Colors.white,
            letterSpacing: -0.5,
          ),
        ),
        SizedBox(height: 12),
        Text(
          '지능형 매뉴얼 챗봇 서비스',
          style: TextStyle(
            fontSize: 16,
            color: Colors.white,
            letterSpacing: 0.5,
          ),
        ),
      ],
    );
  }

  Widget _buildGoogleSignInButton(BuildContext context, WidgetRef ref) {
    return Container(
      width: double.infinity,
      height: 56,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () async {
            try {
              await ref.read(authNotifierProvider.notifier).signIn();
            } catch (e, stack) {
              debugPrint('Login Error: $e');
              debugPrint('Stack Trace: $stack');
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('로그인 실패: $e'),
                    backgroundColor: Colors.redAccent,
                  ),
                );
              }
            }
          },
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Image.network(
                  'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/1200px-Google_%22G%22_logo.svg.png',
                  height: 24,
                ),
                const SizedBox(width: 12),
                const Text(
                  'Google로 계속하기',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1E293B),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFooterText(BuildContext context) {
    return Text(
      '시작함으로써 서비스 이용약관 및 \n개인정보 처리방침에 동의하게 됩니다.',
      textAlign: TextAlign.center,
      style: TextStyle(
        fontSize: 12,
        color: Colors.white.withValues(alpha: 0.4),
        height: 1.5,
      ),
    );
  }
}
