# モジュール・API部品台帳

| ID | module / api | 主な公開コマンド |
|---|---|---|
| tree | `01_tree` | refresh, scan, export, filter |
| rename | `02_rename` | configure, refresh, preview, rename |
| preview | `03_preview` | release, play, pause, stop, seek, refresh, next, previous |
| compare | `04_compare` | refresh, compare, filter |
| hash | `05_hash` | refresh, scan, filter, export |
| recycle | `06_recycle` | search, restore |
| tags | `07_tags` | `api/module.json` を参照 |
| organizer | `08_organizer` | `api/module.json` を参照 |

各フォルダーの`api/module.json`をコマンド定義の一次資料とし、`api/interface.py`と`module/module.py`を照合してください。モジュールの実行環境には`00_shared`も必要です。

**試験の位置付け:** 8モジュールの構造・組み立て検査と、タグ／ファイル整理の個別試験を実施。全機能の実機保証ではありません。
