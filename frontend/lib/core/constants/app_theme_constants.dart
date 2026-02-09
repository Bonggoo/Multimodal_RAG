import 'package:flutter/material.dart';

class AppColors {
  // Deep & Premium Backgrounds (Legacy Dark)
  static const Color primaryBackground = Color(0xFF020617);
  static const Color sidebarBackground = Color(0xFF0F172A);

  // Vibrant Accents (Common)
  static const Color accentIndigo = Color(0xFF6366F1);
  static const Color accentPurple = Color(0xFFA855F7);
  static const Color accentCyan = Color(0xFF22D3EE);
  static const Color accentRose = Color(0xFFF43F5E);

  // Stitch Colors (Light Theme Base)
  static const Color stitchPrimary = Color(0xFF135bec); // Electric Blue
  static const Color stitchBackground = Color(0xFFF8FAFC); // Slate-50 ~ White
  static const Color stitchSurface = Color(0xFFFFFFFF); // White Card
  static const Color stitchSurfaceGlass = Color(0xB3FFFFFF); // 70% White
  static const Color stitchBorder = Color(0xFFE2E8F0); // Slate-200
  static const Color stitchBorderSoft = Color(0xFFF1F5F9); // Slate-100

  // Text Colors (Light Theme)
  static const Color stitchTextPrimary = Color(0xFF0F172A); // Slate-900
  static const Color stitchTextSecondary = Color(0xFF64748B); // Slate-500
  static const Color stitchTextDim = Color(0xFF94A3B8); // Slate-400

  // Glassmorphism Surfaces (Legacy Dark)
  static const Color surfaceGlass = Color(0x661E293B);
  static const Color glassBorder = Color(0x33FFFFFF);
  static const Color glassBorderThin = Color(0x1AFFFFFF);
  static const Color glassHighlight = Color(0x4DFFFFFF);
  static const Color glassCardDark = Color(
    0xFF161B22,
  ); // Stitch Card Background
}

class AppSpacing {
  static const double xs = 4.0;
  static const double s = 8.0;
  static const double m = 16.0;
  static const double l = 24.0;
  static const double xl = 32.0;
  static const double xxl = 48.0;
}

class AppAnimations {
  static const Duration fast = Duration(milliseconds: 200);
  static const Duration medium = Duration(milliseconds: 400);
  static const Duration slow = Duration(milliseconds: 800);

  static const Curve curveDefault = Curves.easeOutCubic;
  static const Curve curveEmphasized = Curves.elasticOut;
}

class AppShadows {
  // iOS Style Soft Shadows (Light Theme)
  static final BoxShadow iosSoft = BoxShadow(
    color: Colors.black.withValues(alpha: 0.06),
    blurRadius: 24,
    spreadRadius: -1,
    offset: const Offset(0, 4),
  );

  static final BoxShadow iosSubtle = BoxShadow(
    color: Colors.black.withValues(alpha: 0.04),
    blurRadius: 12,
    spreadRadius: -1,
    offset: const Offset(0, 2),
  );

  // Neon Shadows (Legacy Dark)
  static final BoxShadow neonBlue = BoxShadow(
    color: AppColors.stitchPrimary.withValues(alpha: 0.4),
    blurRadius: 15,
    spreadRadius: 0,
    offset: const Offset(0, 0),
  );

  static final BoxShadow neonCyan = BoxShadow(
    color: AppColors.accentCyan.withValues(alpha: 0.3),
    blurRadius: 15,
    spreadRadius: 0,
    offset: const Offset(0, 0),
  );
}
