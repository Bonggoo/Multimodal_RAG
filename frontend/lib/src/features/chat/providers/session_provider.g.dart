// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'session_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$sessionNotifierHash() => r'fc15488485d33db3335f07b46fc27b074b630068';

/// See also [SessionNotifier].
@ProviderFor(SessionNotifier)
final sessionNotifierProvider =
    AsyncNotifierProvider<SessionNotifier, List<ChatSession>>.internal(
  SessionNotifier.new,
  name: r'sessionNotifierProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$sessionNotifierHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$SessionNotifier = AsyncNotifier<List<ChatSession>>;
String _$currentSessionIdHash() => r'731b22bec027a13750be5c356cb526173f0d2ecb';

/// See also [CurrentSessionId].
@ProviderFor(CurrentSessionId)
final currentSessionIdProvider =
    NotifierProvider<CurrentSessionId, String?>.internal(
  CurrentSessionId.new,
  name: r'currentSessionIdProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$currentSessionIdHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$CurrentSessionId = Notifier<String?>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member
