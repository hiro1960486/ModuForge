# tests: FileWorkbench Next 3.3 RC v3

## 一括実行
ルート `FW33/test_all.bat` または `py run_tests.py`。各試験で `OK` を確認してください。

## 分類
- `test_modules_contract.py`: 01〜08のモジュール定義、APIの存在、構文、組み立てを検査（機能/GUIの実動作は未検証）
- `test_tags.py`: タグの保存・検索・移動・安全性試験
- `test_organizer.py`: 整理計画・コピー・移動・最終確認・上書き防止・接続定義検査
- `gui/test_runner_ui.py`: GUI単独起動を手で確認するための試験ハーネス。`test_chord/test_start.bat` から呼び出し

## ログ
テスト結果: `%LOCALAPPDATA%\FileWorkbenchNext\logs\tests\` （`latest.json`、日時別テキスト）
GUI試験ログ: `%LOCALAPPDATA%\FileWorkbenchNext\logs\test_gui\`

## 注意
01〜06はAPI契約・組み立て試験のみで、機能動作の全件試験ではありません。
ファイル移動や削除の手動試験は `sample_data` のコピーだけで行ってください。
本テストはGUI操作やWindows固有機能の全動作を保証しません。
