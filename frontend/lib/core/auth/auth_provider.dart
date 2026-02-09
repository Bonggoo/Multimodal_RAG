import 'package:google_sign_in/google_sign_in.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'dart:async';

part 'auth_provider.g.dart';
part 'auth_provider.freezed.dart';

@freezed
class AuthState with _$AuthState {
  const factory AuthState({
    GoogleSignInAccount? user,
    @Default(false) bool isLoading,
    String? errorMessage,
    @Default(false) bool isInitialized,
  }) = _AuthState;
}

@riverpod
class AuthNotifier extends _$AuthNotifier {
  @override
  AuthState build() {
    // 초기화 및 이벤트 리스너 설정
    _init();
    return const AuthState();
  }

  Future<void> _init() async {
    try {
      // 7.0+ 에서는 initialize() 호출이 필요할 수 있습니다 (원본 유지)
      // ignore: undefined_get_block
      try {
        await (GoogleSignIn.instance as dynamic).initialize();
      } catch (_) {}

      // 사용자 변경 이벤트 구독 (원본 방식 유지)
      // ignore: undefined_get_block
      (GoogleSignIn.instance as dynamic).authenticationEvents.listen((
        dynamic event,
      ) {
        try {
          final eventString = event.toString().toLowerCase();
          if (eventString.contains('signin') ||
              eventString.contains('signedin')) {
            final dynamic user =
                (event as Map<dynamic, dynamic>?)?['user'] ??
                (event as dynamic).user;
            state = state.copyWith(user: user, isInitialized: true);
          } else if (eventString.contains('signout') ||
              eventString.contains('signedout')) {
            state = state.copyWith(user: null, isInitialized: true);
          }
        } catch (innerError) {
          // 이벤트 파싱 실패 시 무시
        }
      });

      // 자동 로그인 시도
      // ignore: undefined_get_block
      try {
        await (GoogleSignIn.instance as dynamic)
            .attemptLightweightAuthentication();
      } catch (_) {}

      state = state.copyWith(isInitialized: true);
    } catch (e) {
      state = state.copyWith(
        isInitialized: true,
        errorMessage: '구글 로그인 초기화 실패: $e',
      );
    }
  }

  Future<void> signIn() async {
    if (state.isLoading) return;
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      // macOS 등에서 authenticate() 사용 (원본 방식 유지)
      // ignore: undefined_get_block
      final result = await (GoogleSignIn.instance as dynamic).authenticate();
      state = state.copyWith(user: result, isLoading: false);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        user: null, // 실패 시 사용자 캐시 초기화
        errorMessage: '로그인 실패: ${e.toString()}',
      );
    }
  }

  Future<void> signOut() async {
    await GoogleSignIn.instance.signOut();
    state = state.copyWith(user: null);
  }

  Future<String?> getIdToken() async {
    if (state.user == null) return null;
    try {
      // 린트 결과에 따라 authentication은 Future가 아니므로 await 제거
      final dynamic auth = state.user!.authentication;
      return auth.idToken;
    } catch (e) {
      return null;
    }
  }
}
