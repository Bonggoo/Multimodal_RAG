import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/src/core/theme/app_theme.dart';
import 'package:frontend/src/features/chat/providers/chat_provider.dart';
import 'package:frontend/src/features/chat/providers/session_provider.dart';
import 'package:frontend/src/features/chat/widgets/chat_bubble.dart';
import 'package:frontend/src/features/chat/widgets/chat_drawer.dart';
import 'package:frontend/src/features/chat/widgets/chat_input_area.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  void _sendMessage() {
    final text = _controller.text.trim();
    if (text.isNotEmpty) {
      ref.read(chatNotifierProvider.notifier).addMessage(text);
      _controller.clear();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final messages = ref.watch(chatNotifierProvider);
    final currentSid = ref.watch(currentSessionIdProvider);
    final sessionsAsync = ref.watch(sessionNotifierProvider);

    String title = 'AI 매뉴얼 챗봇';
    if (currentSid != null) {
      sessionsAsync.whenData((sessions) {
        final current = sessions.firstWhere(
          (s) => s.sessionId == currentSid,
          orElse: () => sessions.first,
        );
        title = current.title;
      });
    }

    return Scaffold(
      key: _scaffoldKey,
      extendBodyBehindAppBar: true,
      drawer: ChatDrawer(currentSid: currentSid),
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(60),
        child: ClipRRect(
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
            child: AppBar(
              backgroundColor: Theme.of(
                context,
              ).scaffoldBackgroundColor.withValues(alpha: 0.8),
              elevation: 0,
              centerTitle: false,
              leading: IconButton(
                icon: Icon(
                  Icons.menu,
                  color: Theme.of(context).colorScheme.onSurface,
                ),
                onPressed: () => _scaffoldKey.currentState?.openDrawer(),
              ),
              title: Row(
                children: [
                  const Icon(
                    Icons.auto_awesome,
                    color: AppColors.primary,
                    size: 24,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      title,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Theme.of(context).colorScheme.onSurface,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ),
                ],
              ),
              actions: [
                IconButton(
                  icon: const Icon(
                    Icons.add_comment_outlined,
                    color: AppColors.primary,
                  ),
                  onPressed: () {
                    ref.read(currentSessionIdProvider.notifier).set(null);
                    ref.read(chatNotifierProvider.notifier).loadSession(null);
                  },
                ),
                const SizedBox(width: 8),
              ],
              bottom: PreferredSize(
                preferredSize: const Size.fromHeight(1),
                child: Container(
                  color: Theme.of(context).colorScheme.outlineVariant,
                  height: 1,
                ),
              ),
            ),
          ),
        ),
      ),
      body: Stack(
        children: [
          ListView.builder(
            padding: const EdgeInsets.only(
              top: 110,
              bottom: 120,
              left: 16,
              right: 16,
            ),
            itemCount: messages.length,
            itemBuilder: (context, index) {
              return ChatBubble(message: messages[index]);
            },
          ),
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: ChatInputArea(controller: _controller, onSend: _sendMessage),
          ),
        ],
      ),
    );
  }
}
