import 'package:flutter_test/flutter_test.dart';
import 'package:spectral_omega_rag/main.dart';

void main() {
  testWidgets('Basic smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const SpectralOmegaApp());
    expect(find.text('SPECTRAL OMEGA'), findsOneWidget);
  });
}
