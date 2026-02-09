import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../constants/app_theme_constants.dart';

class SpectralOmegaTheme {
  // Legacy Dark Theme (Optional, kept for reference or fallback)
  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: AppColors.primaryBackground,
      primaryColor: AppColors.accentIndigo,
      useMaterial3: true,
      textTheme: GoogleFonts.outfitTextTheme().apply(
        bodyColor: AppColors.stitchTextPrimary, // Fallback to Stitch
        displayColor: AppColors.stitchTextPrimary,
      ),
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.accentIndigo,
        brightness: Brightness.dark,
      ),
    );
  }

  // New Stitch Light Theme
  static ThemeData get lightTheme {
    return ThemeData(
      brightness: Brightness.light,
      scaffoldBackgroundColor: AppColors.stitchBackground, // #F8FAFC
      primaryColor: AppColors.stitchPrimary,
      useMaterial3: true,

      // Typography
      textTheme: GoogleFonts.interTextTheme().copyWith(
        displayLarge: GoogleFonts.inter(
          fontSize: 32,
          fontWeight: FontWeight.w800,
          color: AppColors.stitchTextPrimary,
          letterSpacing: -0.5,
        ),
        titleLarge: GoogleFonts.inter(
          fontSize: 24,
          fontWeight: FontWeight.w700,
          color: AppColors.stitchTextPrimary,
          letterSpacing: -0.5,
        ),
        titleMedium: GoogleFonts.inter(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: AppColors.stitchTextPrimary,
        ),
        bodyLarge: GoogleFonts.inter(
          fontSize: 16,
          fontWeight: FontWeight.w400,
          color: AppColors.stitchTextPrimary,
          height: 1.6,
        ),
        bodySmall: GoogleFonts.inter(
          fontSize: 12,
          fontWeight: FontWeight.w500,
          color: AppColors.stitchTextSecondary,
        ),
      ),

      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.stitchPrimary,
        brightness: Brightness.light,
        surface: AppColors.stitchSurface,
        onSurface: AppColors.stitchTextPrimary,
        primary: AppColors.stitchPrimary,
        outline: AppColors.stitchBorder,
      ),

      // Component Styles
      cardTheme: CardThemeData(
        color: AppColors.stitchSurface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: AppColors.stitchBorder, width: 1),
        ),
        elevation: 0,
        // Manual shadow handling via Container decoration usually
      ),

      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.stitchPrimary,
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 48),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 0, // Flat with custom shadow if needed
          textStyle: GoogleFonts.inter(
            fontWeight: FontWeight.w600,
            fontSize: 15,
          ),
        ),
      ),

      iconTheme: const IconThemeData(
        color: AppColors.stitchTextSecondary,
        size: 24,
      ),

      dividerTheme: const DividerThemeData(
        color: AppColors.stitchBorder,
        thickness: 1,
      ),
    );
  }
}
