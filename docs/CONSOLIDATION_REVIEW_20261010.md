# 一本化準備の独立検証（2026-10-10）
検証元コミット df0c22206ba0dc38751c9873d650a57b40b90419。GitHubから別の作業コピーへ取得。
- Linux python run_tests.py：44件PASS、失敗/エラー/スキップ0。
- python scripts/audit_flat_layout.py：133ファイル、errors=[]、意図したBAT差分5。
- python scripts/test_staged_acceptance.py：2件PASS。宣言/構文とfixture確認のみ。
- git diff --check：PASS（追加前の検証元）。
- 旧FW33の原本と修正後のルート構成は保持。
旧パスを案内していたdocs/04_TEST_GUIDE.mdを新ルートの手順に更新。
scripts/compare_local_staging.pyを追加。保持したFW33を比較対象に動作確認したが、利用者PCのstaging比較は未実施。
手元の差分回収、Windows全機能受入、依存ライセンス、API統合契約、旧パスCI依存撤去は未完了。PR #1はDraft維持。Nextのコードは変更しない。
