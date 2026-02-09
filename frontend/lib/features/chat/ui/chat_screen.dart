import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../provider/chat_provider.dart';
import '../../../core/constants/app_theme_constants.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../documents/provider/document_provider.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final FocusNode _focusNode = FocusNode();
  bool _isSidebarOpen = false; // Initial State: Collapsed

  @override
  void initState() {
    super.initState();
    // 초기 포커스 (Optional)
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _focusNode.requestFocus();
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _handleSend() {
    if (_controller.text.trim().isEmpty) return;
    final chatState = ref.read(chatProvider);
    if (chatState.isLoading) return;

    ref.read(chatProvider.notifier).sendMessage(_controller.text.trim());
    _controller.clear();
    _focusNode.requestFocus();

    Future.delayed(const Duration(milliseconds: 200), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 500),
          curve: Curves.easeOutCubic,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatProvider);
    final messages = chatState.messages;

    return Row(
      children: [
        // 0. Left Sidebar (Collapsible)
        AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
          width: _isSidebarOpen ? 280 : 0,
          decoration: const BoxDecoration(
            color: Colors.white,
            border: Border(
              right: BorderSide(color: AppColors.stitchBorderSoft),
            ),
          ),
          child: OverflowBox(
            minWidth: 0,
            maxWidth: 280,
            alignment: Alignment.centerLeft,
            child: SizedBox(
              width: 280,
              child: Column(
                children: [
                  // Sidebar Header
                  Padding(
                    padding: const EdgeInsets.all(24),
                    child: Row(
                      children: [
                        const Text(
                          '채팅 기록',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w800,
                            color: AppColors.stitchTextPrimary,
                            letterSpacing: -0.5,
                          ),
                        ),
                        const Spacer(),
                        IconButton(
                          icon: const Icon(
                            Icons.edit_square,
                            color: AppColors.stitchPrimary,
                          ),
                          onPressed: () {
                            // New Chat Logic
                            ref
                                .read(chatProvider.notifier)
                                .clearMessages(); // Temporary
                          },
                          tooltip: '새 채팅',
                        ),
                      ],
                    ),
                  ),

                  // New Chat Button
                  Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 8,
                    ),
                    child: ElevatedButton.icon(
                      onPressed: () {
                        ref.read(chatProvider.notifier).clearMessages();
                      },
                      icon: const Icon(Icons.add_rounded, size: 20),
                      label: const Text('새로운 채팅'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.stitchPrimary.withValues(
                          alpha: 0.1,
                        ),
                        foregroundColor: AppColors.stitchPrimary,
                        elevation: 0,
                        minimumSize: const Size(double.infinity, 48),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // History List
                  Expanded(
                    child: ListView(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      children: const [
                        Padding(
                          padding: EdgeInsets.only(left: 12, bottom: 8),
                          child: Text(
                            '오늘',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: AppColors.stitchTextDim,
                            ),
                          ),
                        ),
                        _HistoryItem(title: '에러 코드 104번 해결 방법', isActive: true),
                        _HistoryItem(title: 'QD77MS 모듈 설정', isActive: false),
                        SizedBox(height: 24),
                        Padding(
                          padding: EdgeInsets.only(left: 12, bottom: 8),
                          child: Text(
                            '지난 7일',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: AppColors.stitchTextDim,
                            ),
                          ),
                        ),
                        _HistoryItem(title: '안전 수칙 가이드', isActive: false),
                        _HistoryItem(title: '배선 점검 리스트', isActive: false),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
              ),
            ),
          ),
        ),

        // Right Sync (Chat Area)
        Expanded(
          child: Column(
            children: [
              // 1. Header (Stitch Clean Header)
              Container(
                height: 72,
                padding: const EdgeInsets.symmetric(horizontal: 24),
                decoration: const BoxDecoration(
                  color: Colors.white,
                  border: Border(
                    bottom: BorderSide(color: AppColors.stitchBorderSoft),
                  ),
                ),
                child: Row(
                  children: [
                    // Title
                    Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Text(
                              'AI 매뉴얼 챗봇',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w800,
                                color: AppColors.stitchTextPrimary,
                                letterSpacing: -0.5,
                              ),
                            ),
                            const SizedBox(width: 8),
                            // Sidebar Toggle Button
                            IconButton(
                              icon: Icon(
                                _isSidebarOpen
                                    ? Icons.keyboard_double_arrow_left_rounded
                                    : Icons.keyboard_double_arrow_right_rounded,
                                size: 20,
                                color: AppColors.stitchTextDim,
                              ),
                              onPressed: () {
                                setState(() {
                                  _isSidebarOpen = !_isSidebarOpen;
                                });
                              },
                              tooltip: _isSidebarOpen ? '기록 접기' : '기록 펼치기',
                              padding: EdgeInsets.zero,
                              constraints: const BoxConstraints(),
                              splashRadius: 20,
                            ),
                            const SizedBox(width: 8),
                            Container(
                              width: 8,
                              height: 8,
                              decoration: const BoxDecoration(
                                color: Colors
                                    .greenAccent, // Emerald-500 equivalent
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 4),
                            const Text(
                              '동기화 중',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: AppColors.stitchTextDim,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const Spacer(),

                    // Ref Doc Chip
                    Consumer(
                      builder: (context, ref, child) {
                        final docs =
                            ref.watch(documentListProvider).value ?? [];
                        final activeDoc = docs.isNotEmpty
                            ? docs.first.filename
                            : '선택된 문서 없음';

                        return Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            color: AppColors.stitchBackground,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: AppColors.stitchBorder),
                          ),
                          child: Row(
                            children: [
                              const Icon(
                                Icons.auto_stories_outlined,
                                size: 14,
                                color: AppColors.stitchPrimary,
                              ),
                              const SizedBox(width: 8),
                              ConstrainedBox(
                                constraints: const BoxConstraints(
                                  maxWidth: 150,
                                ),
                                child: Text(
                                  '참조: $activeDoc',
                                  style: const TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                    color: AppColors.stitchTextSecondary,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 4),
                              const Icon(
                                Icons.expand_more_rounded,
                                size: 14,
                                color: AppColors.stitchTextDim,
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ),

              // 2. Chat Area
              Expanded(
                child: Container(
                  color: AppColors.stitchBackground, // Light Slate Background
                  child: ListView.builder(
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
              ),

              // 3. Input Area (Floating Style with Bottom Padding for Nav)
              Container(
                padding: const EdgeInsets.only(
                  left: 24,
                  right: 24,
                  top: 24,
                  bottom: 100,
                ), // Extra bottom padding for floating nav
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.9),
                  border: const Border(
                    top: BorderSide(color: AppColors.stitchBorderSoft),
                  ),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    // Add Button
                    Container(
                      width: 48,
                      height: 48,
                      margin: const EdgeInsets.only(right: 12),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppColors.stitchBorder),
                        boxShadow: [AppShadows.iosSubtle],
                      ),
                      child: IconButton(
                        icon: const Icon(
                          Icons.add_circle_outline_rounded,
                          color: AppColors.stitchTextDim,
                        ),
                        onPressed: () {}, // Attachment Logic
                      ),
                    ),

                    // Text Field
                    Expanded(
                      child: Container(
                        constraints: const BoxConstraints(
                          minHeight: 48,
                          maxHeight: 120,
                        ),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: AppColors.stitchBorder),
                          boxShadow: [AppShadows.iosSubtle],
                        ),
                        child: TextField(
                          controller: _controller,
                          focusNode: _focusNode,
                          maxLines: null,
                          decoration: const InputDecoration(
                            hintText: '질문을 입력하세요...',
                            border: InputBorder.none,
                            hintStyle: TextStyle(
                              color: AppColors.stitchTextDim,
                              fontSize: 15,
                            ),
                          ),
                          style: const TextStyle(
                            fontSize: 15,
                            color: AppColors.stitchTextPrimary,
                          ),
                          onSubmitted: (_) => _handleSend(),
                        ),
                      ),
                    ),

                    // Send Button
                    const SizedBox(width: 12),
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: AppColors.stitchPrimary,
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: AppColors.stitchPrimary.withValues(
                              alpha: 0.3,
                            ),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: IconButton(
                        icon: chatState.isLoading
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  color: Colors.white,
                                  strokeWidth: 2,
                                ),
                              )
                            : const Icon(
                                Icons.auto_awesome_rounded,
                                color: Colors.white,
                                size: 22,
                              ),
                        onPressed: _handleSend,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class ChatBubble extends ConsumerWidget {
  final ChatMessage message;
  final int index;
  const ChatBubble({super.key, required this.message, required this.index});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isUser = message.isUser;

    return Padding(
      padding: const EdgeInsets.only(bottom: 24),
      child: Column(
        crossAxisAlignment: isUser
            ? CrossAxisAlignment.end
            : CrossAxisAlignment.start,
        children: [
          // Header (Name & Avatar)
          Padding(
            padding: const EdgeInsets.only(bottom: 6, left: 4, right: 4),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (!isUser) ...[
                  Container(
                    width: 28,
                    height: 28,
                    decoration: BoxDecoration(
                      color: AppColors.stitchPrimary.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: AppColors.stitchPrimary.withValues(alpha: 0.2),
                      ),
                    ),
                    child: const Icon(
                      Icons.smart_toy_outlined,
                      size: 16,
                      color: AppColors.stitchPrimary,
                    ),
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    '매뉴얼 AI',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: AppColors.stitchTextSecondary,
                    ),
                  ),
                ],
                if (isUser) ...[
                  const Text(
                    'User',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: AppColors.stitchTextSecondary,
                    ),
                  ),
                ],
              ],
            ),
          ),

          // Message Box
          Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.7,
            ),
            padding: const EdgeInsets.all(16),
            decoration: isUser
                ? BoxDecoration(
                    // User Bubble (Primary Blue)
                    color: AppColors.stitchPrimary,
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(20),
                      topRight: Radius.zero,
                      bottomLeft: Radius.circular(20),
                      bottomRight: Radius.circular(20),
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.stitchPrimary.withValues(alpha: 0.25),
                        blurRadius: 8,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  )
                : BoxDecoration(
                    // AI Bubble (Slate White)
                    color: Colors.white, // White Card
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.zero,
                      topRight: Radius.circular(20),
                      bottomLeft: Radius.circular(20),
                      bottomRight: Radius.circular(20),
                    ),
                    border: Border.all(color: AppColors.stitchBorderSoft),
                    boxShadow: [AppShadows.iosSubtle],
                  ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  message.text,
                  style: TextStyle(
                    fontSize: 15,
                    height: 1.6,
                    color: isUser ? Colors.white : AppColors.stitchTextPrimary,
                    fontWeight: isUser ? FontWeight.w500 : FontWeight.w400,
                  ),
                ),
                if (message.images != null && message.images!.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 12),
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: message.images!
                          .map((path) => ImageThumb(path: path))
                          .toList(),
                    ),
                  ),
              ],
            ),
          ),

          // Action Buttons (Only for User)
          if (isUser)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    icon: const Icon(
                      Icons.refresh_rounded,
                      size: 16,
                      color: AppColors.stitchTextDim,
                    ),
                    onPressed: () =>
                        ref.read(chatProvider.notifier).retryMessage(index),
                    splashRadius: 16,
                    constraints: const BoxConstraints(),
                    padding: const EdgeInsets.all(4),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(
                      Icons.delete_outline_rounded,
                      size: 16,
                      color: AppColors.stitchTextDim,
                    ),
                    onPressed: () =>
                        ref.read(chatProvider.notifier).deleteMessage(index),
                    splashRadius: 16,
                    constraints: const BoxConstraints(),
                    padding: const EdgeInsets.all(4),
                  ),
                ],
              ),
            ),
        ],
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
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.stitchBorder),
        boxShadow: const [
          BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 2)),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: CachedNetworkImage(
          imageUrl: imageUrl,
          width: 200,
          fit: BoxFit.cover,
          placeholder: (context, url) => Container(
            width: 200,
            height: 120,
            color: AppColors.stitchBackground,
            child: const Center(
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
          ),
          errorWidget: (context, url, error) => Container(
            width: 200,
            height: 120,
            color: AppColors.stitchBackground,
            child: const Icon(
              Icons.broken_image_outlined,
              color: AppColors.stitchTextDim,
            ),
          ),
        ),
      ),
    );
  }
}

class _HistoryItem extends StatelessWidget {
  final String title;
  final bool isActive;

  const _HistoryItem({required this.title, required this.isActive});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      decoration: BoxDecoration(
        color: isActive
            ? AppColors.stitchPrimary.withValues(alpha: 0.08)
            : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
      ),
      child: ListTile(
        dense: true,
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 0),
        leading: Icon(
          Icons.chat_bubble_outline_rounded,
          size: 16,
          color: isActive ? AppColors.stitchPrimary : AppColors.stitchTextDim,
        ),
        title: Text(
          title,
          style: TextStyle(
            fontSize: 13,
            fontWeight: isActive ? FontWeight.w600 : FontWeight.w500,
            color: isActive
                ? AppColors.stitchTextPrimary
                : AppColors.stitchTextSecondary,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: isActive
            ? const Icon(
                Icons.more_horiz_rounded,
                size: 16,
                color: AppColors.stitchTextDim,
              )
            : null,
        onTap: () {
          // History Item Tap Logic
        },
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
  }
}
