import 'package:google_sign_in/google_sign_in.dart';
import '../models/user_model.dart';
import 'dart:async';

class AuthRepository {
  final GoogleSignIn _googleSignIn = GoogleSignIn.instance;

  Future<void> initialize() async {
    await _googleSignIn.initialize(
      clientId:
          '206500529944-g65qi9u1p55udr3nq255ac0rablp5j1v.apps.googleusercontent.com',
    );
  }

  Future<UserModel?> signIn() async {
    try {
      final googleUser = await _googleSignIn.authenticate();
      // ignore: unnecessary_null_comparison, dead_code
      if (googleUser == null) return null;

      // ignore: await_only_futures
      final googleAuth = await googleUser.authentication;

      return UserModel(
        id: googleUser.id,
        email: googleUser.email,
        displayName: googleUser.displayName,
        photoUrl: googleUser.photoUrl,
        idToken: googleAuth.idToken,
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<void> signOut() async {
    await _googleSignIn.signOut();
  }

  Future<UserModel?> attemptSilentLogin() async {
    try {
      final googleUser = await _googleSignIn.attemptLightweightAuthentication();
      // ignore: unnecessary_null_comparison, dead_code
      if (googleUser == null) return null;

      // ignore: await_only_futures
      final googleAuth = await googleUser.authentication;

      return UserModel(
        id: googleUser.id,
        email: googleUser.email,
        displayName: googleUser.displayName,
        photoUrl: googleUser.photoUrl,
        idToken: googleAuth.idToken,
      );
    } catch (e) {
      return null;
    }
  }
}
