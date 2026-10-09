# FileWorkbench Next 3.3 RC — 分離モジュール仕様まとめ

| ID | 部品 | API/主要用途 |
|---|---|---|
| 01 | tree | ファイルツリー・選択・出力 |
| 02 | rename | ファイル名変更 |
| 03 | preview | ファイルプレビュー |
| 04 | compare | 比較 |
| 05 | hash | ハッシュ計算 |
| 06 | recycle | ごみ箱連携 |
| 07 | tags | タグDB・検索・メディア確認（既存の試験実装を維持） |
| 08 | organizer | 情報取得・移動先指定・コピー/移動計画・確認後実行 |

## APIの基本方針
- 各フォルダーの `api/` は外部インターフェース、`module/` は機能実装。
- GUIは共通ModulePortで独立起動。タグと整理の連携は今後の接続試験対象。
- プレビューやタグは既存の実装を保持し、ファイル整理から重複実装しない。
- ファイルの削除・上書き・コピー後削除は **未実装**。
- 移動は確認必須・同名衝突拒否・別ファイルシステムは拒否。

## ログ
- 標準ログAPIは `00_shared/src/fileworkbench/services/diagnostic_log.py`。
- Windows保存先: `%LOCALAPPDATA%\FileWorkbenchNext\logs\events.jsonl`。
- JSONL、2MB×最大5世代。ログ内容にはパスが含まれるので外部共有前に確認する。
- **標準ログAPIを新設**。現段階で全旧モジュールのイベント配線までは未完了。

## テストと制約
- `test_all.bat` にタグ・ファイル整理のコア試験を集約。
- `run_organizer.bat`, `run_tags.bat` はPySide6が必要。GUI操作はWindows実機で要確認。
- `sample_data/`は合成データ。実際の画像動画ではない。
- 他の6モジュールの既存仕様は各部品のREADMEも参照。
