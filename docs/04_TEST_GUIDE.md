# ModuForge 試験ガイド

## Windows 11
1. `FW33`の`requirements.txt`に従って依存関係を導入
2. `FW33/test_all.bat`で非GUIの一括試験
3. `FW33/test_chord/test_start.bat`で既存テストUI
4. タグやファイル整理の単独画面から複製済み試験データを使用

## コマンドライン

```powershell
cd FW33
py run_tests.py
```

`FW33/tests/`内の試験は初期基準版で合計21件。構造確認2件、ファイル整理10件、タグ9件です。

## ログ

非GUIランナーは`%LOCALAPPDATA%\FileWorkbenchNext\logs\tests\`に出力します。CIでは一時環境のログをアーティファクトとして保管します。公開リポジトリにログやユーザー固有パスをコミットしないでください。

## 合格範囲

- 自動試験はAPI構造・組み立て・タグ・ファイル整理等の限定範囲
- GUI起動、メディア再生、ごみ箱操作、Windows特有の長いパス処理などは別枠の試験
