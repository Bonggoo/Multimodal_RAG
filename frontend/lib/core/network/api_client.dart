import 'package:dio/dio.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'api_client.g.dart';

@riverpod
Dio dio(Ref ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: 'http://127.0.0.1:8000',
      headers: {'X-API-Key': '12345', 'Content-Type': 'application/json'},
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
    ),
  );

  // Add logging interceptor if needed
  dio.interceptors.add(LogInterceptor(responseBody: true, requestBody: true));

  return dio;
}
