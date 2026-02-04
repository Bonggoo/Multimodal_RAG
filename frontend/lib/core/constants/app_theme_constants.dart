import 'package:flutter/material.dart';

class AppColors {
  // Deep & Premium Backgrounds
  static const Color primaryBackground = Color(0xFF020617);
  static const Color sidebarBackground = Color(0xFF0F172A);

  // Vibrant Accents
  static const Color accentIndigo = Color(0xFF6366F1);
  static const Color accentPurple = Color(0xFFA855F7);
  static const Color accentCyan = Color(0xFF22D3EE);
  static const Color accentRose = Color(0xFFF43F5E);

  // Glassmorphism Surfaces
  static const Color surfaceGlass = Color(0x661E293B);
  static const Color glassBorder = Color(0x1AFFFFFF);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF6366F1), Color(0xFFA855F7)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient surfaceGradient = LinearGradient(
    colors: [Colors.white10, Colors.transparent],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // Text Colors
  static const Color textPrimary = Color(0xFFF8FAFC);
  static const Color textSecondary = Color(0xFF94A3B8);
  static const Color textDim = Color(0xFF64748B);
}

class AppSpacing {
  static const double xs = 4.0;
  static const double s = 8.0;
  static const double m = 16.0;
  static const double l = 24.0;
  static const double xl = 32.0;
  static const double xxl = 48.0;
}
