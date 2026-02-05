import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../provider/session_provider.dart';
import '../provider/chat_provider.dart';
import '../../../core/constants/app_theme_constants.dart';

class SessionListView extends ConsumerWidget {
  const SessionListView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sessionsAsync = ref.watch(sessionListProvider);

    return sessionsAsync.when(
      data: (sessions) {
        if (sessions.isEmpty) {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.chat_bubble_outline_rounded,
                  color: Colors.white24,
                  size: 40,
                ),
                SizedBox(height: 12),
                Text(
                  'No chats yet',
                  style: TextStyle(color: Colors.white24, fontSize: 13),
                ),
              ],
            ),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          itemCount: sessions.length,
          itemBuilder: (context, index) {
            final session = sessions[index];
            final sessionId = session['session_id'];
            final title = session['title'] ?? '새로운 채팅';
            final lastMsgAt = session['last_message_at'] ?? '';

            // 현재 활성화된 세션인지 확인
            final currentSessionId = ref.watch(chatProvider).currentSessionId;
            final isActive = currentSessionId == sessionId;

            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: SessionTile(
                title: title,
                subtitle: lastMsgAt.toString().split('T').first,
                isActive: isActive,
                onTap: () =>
                    ref.read(chatProvider.notifier).loadSession(sessionId),
                onDelete: () => ref
                    .read(sessionListProvider.notifier)
                    .deleteSession(sessionId),
              ),
            );
          },
        );
      },
      loading: () => const Center(
        child: CircularProgressIndicator(
          color: AppColors.accentIndigo,
          strokeWidth: 2,
        ),
      ),
      error: (e, st) => Padding(
        padding: const EdgeInsets.all(16.0),
        child: Text(
          'Error: $e',
          style: const TextStyle(color: Colors.redAccent, fontSize: 12),
        ),
      ),
    );
  }
}

class SessionTile extends StatefulWidget {
  final String title;
  final String subtitle;
  final bool isActive;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  const SessionTile({
    super.key,
    required this.title,
    required this.subtitle,
    required this.isActive,
    required this.onTap,
    required this.onDelete,
  });

  @override
  State<SessionTile> createState() => _SessionTileState();
}

class _SessionTileState extends State<SessionTile> {
  bool _isHovering = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _isHovering = true),
      onExit: (_) => setState(() => _isHovering = false),
      child: Container(
        decoration: BoxDecoration(
          color: widget.isActive
              ? AppColors.accentIndigo.withValues(alpha: 0.15)
              : _isHovering
              ? Colors.white.withValues(alpha: 0.06)
              : Colors.white.withValues(alpha: 0.03),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: widget.isActive
                ? AppColors.accentIndigo.withValues(alpha: 0.3)
                : _isHovering
                ? Colors.white.withValues(alpha: 0.1)
                : Colors.white.withValues(alpha: 0.05),
          ),
        ),
        child: ListTile(
          onTap: widget.onTap,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 0,
          ),
          dense: true,
          title: Text(
            widget.title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              fontSize: 13,
              fontWeight: widget.isActive ? FontWeight.w800 : FontWeight.w600,
              color: widget.isActive ? Colors.white : Colors.white70,
            ),
          ),
          subtitle: Text(
            widget.subtitle,
            style: TextStyle(
              fontSize: 10,
              color: Colors.white.withValues(alpha: 0.3),
            ),
          ),
          trailing: (widget.isActive || _isHovering)
              ? IconButton(
                  icon: const Icon(
                    Icons.delete_outline_rounded,
                    size: 16,
                    color: AppColors.accentRose,
                  ),
                  onPressed: () => _confirmDelete(context),
                )
              : null,
        ),
      ),
    );
  }

  void _confirmDelete(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.sidebarBackground,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        title: const Text(
          '채팅 삭제',
          style: TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        content: const Text(
          '이 대화 내역을 정말로 삭제하시겠습니까?',
          style: TextStyle(color: Colors.white70, fontSize: 14),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('취소', style: TextStyle(color: Colors.white38)),
          ),
          TextButton(
            onPressed: () {
              widget.onDelete();
              Navigator.pop(ctx);
            },
            child: const Text(
              '삭제',
              style: TextStyle(
                color: AppColors.accentRose,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
