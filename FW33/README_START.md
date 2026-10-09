# 実行ガイド
1. Windows 11でZIPを短いパスへ展開。
2. `py -m pip install -r requirements.txt`（依存の導入）。
3. `test_all.bat` で自動試験。
4. `run_tags.bat` と `run_organizer.bat` で単独GUI試験。
5. `sample_data/inbox` のダミーを使用し `sample_data/destination` を整理先に指定。
6. ログは `%LOCALAPPDATA%\FileWorkbenchNext\logs` に出力。
**重要**: 実際の個人ファイルを移動する前に必ずコピーで試験。

## テスト配置更新
試験コードとGUI試験ツール本体は `tests/` に集約しました。 `test_all.bat` で全試験、`test_tags.bat` と `test_organizer.bat` で個別実行できます。 `tests/README.md` を参照してください。
