import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/user_model.dart';
import '../repositories/auth_repository.dart';

part 'auth_provider.g.dart';

@Riverpod(keepAlive: true)
class AuthNotifier extends _$AuthNotifier {
  late final AuthRepository _repository;

  @override
  UserModel? build() {
    _repository = AuthRepository();
    // 초기화 시 조용히 로그인 시도
    _initialize();
    return null;
  }

  Future<void> _initialize() async {
    try {
      await _repository.initialize();
      final user = await _repository.attemptSilentLogin();
      state = user;
    } catch (e) {
      state = null;
    }
  }

  Future<void> signIn() async {
    try {
      final user = await _repository.signIn();
      state = user;
    } catch (e) {
      state = null;
      rethrow;
    }
  }

  Future<void> signOut() async {
    await _repository.signOut();
    state = null;
  }
}

@Riverpod(keepAlive: true)
AuthRepository authRepository(AuthRepositoryRef ref) {
  return AuthRepository();
}
