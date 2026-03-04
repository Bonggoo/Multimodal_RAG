import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/app_dialog.dart';
import '../providers/chat_provider.dart';
import '../providers/session_provider.dart';

class ChatDrawer extends ConsumerWidget {
  final String? currentSid;

  const ChatDrawer({super.key, this.currentSid});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sessionsAsync = ref.watch(sessionNotifierProvider);

    return Drawer(
      child: Column(
        children: [
          DrawerHeader(
            decoration: BoxDecoration(
              color: Theme.of(context).scaffoldBackgroundColor,
            ),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.chat_bubble,
                    color: AppColors.primary,
                    size: 40,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    '대화 내역',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).colorScheme.onSurface,
                    ),
                  ),
                ],
              ),
            ),
          ),
          Expanded(
            child: sessionsAsync.when(
              data: (sessions) => ListView.builder(
                padding: EdgeInsets.zero,
                itemCount: sessions.length,
                itemBuilder: (context, index) {
                  final session = sessions[index];
                  final isSelected = session.sessionId == currentSid;
                  return ListTile(
                    leading: Icon(
                      Icons.chat_outlined,
                      color: isSelected
                          ? AppColors.primary
                          : const Color(0xFF94A3B8),
                    ),
                    title: Text(
                      session.title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontWeight: isSelected
                            ? FontWeight.bold
                            : FontWeight.normal,
                        color: isSelected
                            ? AppColors.primary
                            : Theme.of(context).colorScheme.onSurface,
                      ),
                    ),
                    subtitle: Text(
                      session.lastMessageAt.substring(0, 10),
                      style: TextStyle(
                        fontSize: 12,
                        color: Theme.of(
                          context,
                        ).colorScheme.onSurface.withValues(alpha: 0.5),
                      ),
                    ),
                    onTap: () {
                      ref
                          .read(currentSessionIdProvider.notifier)
                          .set(session.sessionId);
                      ref
                          .read(chatNotifierProvider.notifier)
                          .loadSession(session.sessionId);
                      Navigator.pop(context);
                    },
                    trailing: isSelected
                        ? const Icon(
                            Icons.check,
                            color: AppColors.primary,
                            size: 16,
                          )
                        : IconButton(
                            icon: const Icon(
                              Icons.delete_outline,
                              size: 18,
                              color: Color(0xFF94A3B8),
                            ),
                            onPressed: () {
                              AppDialog.show(
                                context: context,
                                title: '대화 삭제',
                                content: '이 대화 내역을 삭제하시겠습니까?',
                                confirmText: '삭제',
                                confirmColor: Colors.redAccent,
                                onConfirm: () {
                                  ref
                                      .read(sessionNotifierProvider.notifier)
                                      .deleteSession(session.sessionId);
                                },
                              );
                            },
                          ),
                  );
                },
              ),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('에러 발생: $e')),
            ),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.add, color: AppColors.primary),
            title: const Text(
              '새 대화 시작하기',
              style: TextStyle(
                color: AppColors.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
            onTap: () {
              ref.read(currentSessionIdProvider.notifier).set(null);
              ref.read(chatNotifierProvider.notifier).loadSession(null);
              Navigator.pop(context);
            },
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}
