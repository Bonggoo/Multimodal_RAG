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
      // 7.0+ 에서는 initialize() 호출이 필수입니다.
      await GoogleSignIn.instance.initialize();

      // 사용자 변경 이벤트 구독
      GoogleSignIn.instance.authenticationEvents.listen((dynamic event) {
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
      await GoogleSignIn.instance.attemptLightweightAuthentication();
      state = state.copyWith(isInitialized: true);
    } catch (e) {
      state = state.copyWith(
        isInitialized: true,
        errorMessage: '구글 로그인 초기화 실패: $e',
      );
    }
  }

  Future<void> signIn() async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final result = await GoogleSignIn.instance.authenticate();
      if (result == null) {
        state = state.copyWith(isLoading: false);
        return;
      }
      state = state.copyWith(user: result, isLoading: false);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
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
      return state.user!.authentication.idToken;
    } catch (e) {
      return null;
    }
  }
}
