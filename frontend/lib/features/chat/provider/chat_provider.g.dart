// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'chat_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$chatHash() => r'60b702a93134e32cadeead2bbba84831869071f8';

/// See also [Chat].
@ProviderFor(Chat)
final chatProvider =
    AutoDisposeNotifierProvider<Chat, List<ChatMessage>>.internal(
      Chat.new,
      name: r'chatProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$chatHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

typedef _$Chat = AutoDisposeNotifier<List<ChatMessage>>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
