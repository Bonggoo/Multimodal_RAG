import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../provider/chat_provider.dart';
import '../../../core/constants/app_theme_constants.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:google_fonts/google_fonts.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _isSmartRouting = false;

  @override
  void initState() {
    super.initState();
    _controller.addListener(_detectSmartRouting);
  }

  void _detectSmartRouting() {
    final text = _controller.text;
    final hasPage = RegExp(r'(\d+페이지|p\.\d+|page \d+)').hasMatch(text);
    if (hasPage != _isSmartRouting) {
      setState(() => _isSmartRouting = hasPage);
    }
  }

  void _handleSend() {
    if (_controller.text.trim().isEmpty) return;
    ref.read(chatProvider.notifier).sendMessage(_controller.text.trim());
    _controller.clear();

    Future.delayed(const Duration(milliseconds: 200), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 500),
          curve: Curves.easeOutBack,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatProvider);
    final messages = chatState.messages;

    return Container(
      decoration: BoxDecoration(
        color: AppColors.sidebarBackground.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(32),
        border: Border.all(color: AppColors.glassBorder),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.02),
              border: const Border(
                bottom: BorderSide(color: AppColors.glassBorder),
              ),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.chat_bubble_outline_rounded,
                  size: 20,
                  color: AppColors.accentIndigo,
                ),
                const SizedBox(width: 12),
                Text(
                  'KNOWLEDGE CHAT',
                  style: GoogleFonts.outfit(
                    fontWeight: FontWeight.w800,
                    fontSize: 14,
                    letterSpacing: 1.2,
                    color: Colors.white,
                  ),
                ),
                const Spacer(),
                AnimatedOpacity(
                  opacity: _isSmartRouting ? 1.0 : 0.0,
                  duration: const Duration(milliseconds: 300),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.accentIndigo.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: AppColors.accentIndigo.withValues(alpha: 0.3),
                      ),
                    ),
                    child: const Row(
                      children: [
                        Icon(
                          Icons.auto_awesome,
                          size: 14,
                          color: AppColors.accentIndigo,
                        ),
                        SizedBox(width: 6),
                        Text(
                          'SMART ROUTING',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w900,
                            color: AppColors.accentIndigo,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),

          Expanded(
            child: messages.isEmpty
                ? const EmptyChatView()
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 32,
                    ),
                    itemCount: messages.length,
                    itemBuilder: (context, index) {
                      final msg = messages[index];
                      return ChatBubble(message: msg, index: index);
                    },
                  ),
          ),

          Padding(
            padding: const EdgeInsets.all(24.0),
            child: Container(
              padding: const EdgeInsets.only(
                left: 20,
                right: 8,
                top: 4,
                bottom: 4,
              ),
              decoration: BoxDecoration(
                color: const Color(0xFF0F172A),
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: AppColors.glassBorder),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.2),
                    blurRadius: 20,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      style: const TextStyle(color: Colors.white, fontSize: 15),
                      decoration: const InputDecoration(
                        hintText: 'Type your question here...',
                        border: InputBorder.none,
                        hintStyle: TextStyle(
                          color: AppColors.textDim,
                          fontSize: 15,
                        ),
                      ),
                      onSubmitted: (_) => _handleSend(),
                    ),
                  ),
                  const SizedBox(width: 12),
                  InkWell(
                    onTap: _handleSend,
                    borderRadius: BorderRadius.circular(16),
                    child: Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        gradient: AppColors.primaryGradient,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Icon(
                        Icons.arrow_upward_rounded,
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class EmptyChatView extends StatelessWidget {
  const EmptyChatView({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.02),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.psychology_outlined,
              size: 64,
              color: AppColors.accentIndigo.withValues(alpha: 0.5),
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'Ready to assist',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Upload a document and ask me anything.',
            style: TextStyle(color: AppColors.textSecondary),
          ),
        ],
      ),
    );
  }
}

class ChatBubble extends ConsumerWidget {
  final ChatMessage message;
  final int index;
  const ChatBubble({super.key, required this.message, required this.index});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 32),
      child: Row(
        mainAxisAlignment: message.isUser
            ? MainAxisAlignment.end
            : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser)
            Container(
              margin: const EdgeInsets.only(top: 4, right: 12),
              child: CircleAvatar(
                radius: 18,
                backgroundColor: AppColors.accentIndigo.withValues(alpha: 0.1),
                child: const Icon(
                  Icons.smart_toy_outlined,
                  color: AppColors.accentIndigo,
                  size: 18,
                ),
              ),
            ),
          Flexible(
            child: Column(
              crossAxisAlignment: message.isUser
                  ? CrossAxisAlignment.end
                  : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    gradient: message.isUser ? AppColors.primaryGradient : null,
                    color: message.isUser ? null : const Color(0xFF1E293B),
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(24),
                      topRight: const Radius.circular(24),
                      bottomLeft: Radius.circular(message.isUser ? 24 : 4),
                      bottomRight: Radius.circular(message.isUser ? 4 : 24),
                    ),
                  ),
                  child: Text(
                    message.text,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 15,
                      height: 1.5,
                      fontWeight: message.isUser
                          ? FontWeight.w600
                          : FontWeight.w400,
                    ),
                  ),
                ),
                if (message.images != null && message.images!.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 16),
                    child: Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      children: message.images!
                          .map((path) => ImageThumb(path: path))
                          .toList(),
                    ),
                  ),
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (message.isUser)
                        _ActionButton(
                          icon: Icons.refresh_rounded,
                          onTap: () => ref
                              .read(chatProvider.notifier)
                              .retryMessage(index),
                          tooltip: 'Retry',
                        ),
                      _ActionButton(
                        icon: Icons.delete_outline_rounded,
                        onTap: () => ref
                            .read(chatProvider.notifier)
                            .deleteMessage(index),
                        tooltip: 'Delete',
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          if (message.isUser)
            Container(
              margin: const EdgeInsets.only(top: 4, left: 12),
              child: CircleAvatar(
                radius: 18,
                backgroundColor: AppColors.accentPurple.withValues(alpha: 0.1),
                child: const Icon(
                  Icons.person_outline_rounded,
                  color: AppColors.accentPurple,
                  size: 18,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  final String tooltip;

  const _ActionButton({
    required this.icon,
    required this.onTap,
    required this.tooltip,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: Tooltip(
        message: tooltip,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(8),
          child: Padding(
            padding: const EdgeInsets.all(4.0),
            child: Icon(
              icon,
              size: 16,
              color: Colors.white.withValues(alpha: 0.3),
            ),
          ),
        ),
      ),
    );
  }
}

class ImageThumb extends StatelessWidget {
  final String path;
  const ImageThumb({super.key, required this.path});

  @override
  Widget build(BuildContext context) {
    final imageUrl = path.startsWith('http')
        ? path
        : 'http://127.0.0.1:8000/$path';

    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.glassBorder),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.3),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: CachedNetworkImage(
          imageUrl: imageUrl,
          width: 240,
          fit: BoxFit.cover,
          placeholder: (context, url) => Container(
            width: 240,
            height: 150,
            color: Colors.white.withValues(alpha: 0.05),
            child: const Center(
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
          ),
          errorWidget: (context, url, error) => Container(
            width: 240,
            height: 150,
            color: Colors.white.withValues(alpha: 0.05),
            child: const Icon(
              Icons.image_not_supported_outlined,
              color: Colors.white24,
            ),
          ),
        ),
      ),
    );
  }
}
