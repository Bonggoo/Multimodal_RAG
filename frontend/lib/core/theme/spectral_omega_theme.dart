import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../constants/app_theme_constants.dart';

class SpectralOmegaTheme {
  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: AppColors.primaryBackground,
      primaryColor: AppColors.accentIndigo,
      useMaterial3: true,

      // Typography Overhaul
      textTheme: GoogleFonts.outfitTextTheme().copyWith(
        displayLarge: GoogleFonts.outfit(
          fontSize: 36,
          fontWeight: FontWeight.w800,
          color: AppColors.textPrimary,
          letterSpacing: -1.0,
        ),
        titleMedium: GoogleFonts.outfit(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
          letterSpacing: 0.5,
        ),
        bodyLarge: GoogleFonts.inter(
          fontSize: 16,
          fontWeight: FontWeight.w400,
          color: AppColors.textPrimary,
          height: 1.6,
        ),
        bodySmall: GoogleFonts.inter(
          fontSize: 12,
          fontWeight: FontWeight.w500,
          color: AppColors.textSecondary,
        ),
      ),

      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.accentIndigo,
        brightness: Brightness.dark,
        surface: AppColors.sidebarBackground,
        onSurface: AppColors.textPrimary,
        primary: AppColors.accentIndigo,
        secondary: AppColors.accentPurple,
      ),

      // Component Styles
      cardTheme: CardThemeData(
        color: AppColors.surfaceGlass,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(28),
          side: BorderSide(color: AppColors.glassBorder, width: 0.8),
        ),
        elevation: 0,
      ),

      iconTheme: const IconThemeData(color: AppColors.textPrimary, size: 22),
    );
  }
}
