import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../../core/constants/app_theme_constants.dart';

class AuroraBackground extends StatefulWidget {
  final Widget child;
  const AuroraBackground({super.key, required this.child});

  @override
  State<AuroraBackground> createState() => _AuroraBackgroundState();
}

class _AuroraBackgroundState extends State<AuroraBackground>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 15),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Base Dark Background
        Positioned.fill(child: Container(color: AppColors.primaryBackground)),

        // Dynamic Aurora Circles
        AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            return Stack(
              children: [
                _buildAuroraCircle(
                  color: AppColors.accentIndigo.withValues(alpha: 0.15),
                  size: 600,
                  offset: Offset(
                    math.cos(_controller.value * 2 * math.pi) * 100,
                    math.sin(_controller.value * 2 * math.pi) * 100,
                  ),
                ),
                _buildAuroraCircle(
                  color: AppColors.accentPurple.withValues(alpha: 0.15),
                  size: 500,
                  offset: Offset(
                    math.sin(_controller.value * 2 * math.pi) * 150 + 200,
                    math.cos(_controller.value * 2 * math.pi) * 150 + 100,
                  ),
                ),
                _buildAuroraCircle(
                  color: AppColors.accentCyan.withValues(alpha: 0.1),
                  size: 400,
                  offset: Offset(
                    math.cos(_controller.value * 2 * math.pi + math.pi) * 120 -
                        100,
                    math.sin(_controller.value * 2 * math.pi + math.pi) * 120 +
                        300,
                  ),
                ),
              ],
            );
          },
        ),

        // Main Content
        Positioned.fill(child: widget.child),
      ],
    );
  }

  Widget _buildAuroraCircle({
    required Color color,
    required double size,
    required Offset offset,
  }) {
    return Positioned(
      left: offset.dx,
      top: offset.dy,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: RadialGradient(colors: [color, color.withValues(alpha: 0)]),
        ),
      ),
    );
  }
}
