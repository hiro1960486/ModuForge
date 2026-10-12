# ModuForge

**Reusable Python Modules, APIs & Testing Platform**  
**Status:** v0.1.0-alpha — 開発中 / Public

ModuForgeは、複数のPythonアプリから再利用できるモジュールとAPIを、単独試験・連携試験・仕様管理とともに育てるオープンソースの研究開発プロジェクトです。

最初の研究対象はFileWorkbench Next 3.3 RCから分離した部品群です。FileWorkbench Next自体がModuForgeの本体ではなく、将来の接続先アプリの一例です。

## 利用前のお知らせ：既知の不具合（2026-10-10）

現在のmainにある旧`FW33/`のTags・Organizerには、移動先・整理先が空欄の場合、アプリの起動フォルダーを移動先として扱う不具合があります。確認画面でYesを押すと、意図しない場所へ移動・コピーする可能性があります。

**移動先は必ず明示的に選び、確認画面の元・先・操作種別を確認してください。移動先が空欄のまま実行せず、不明な確認画面ではNoを選んでください。試験には複製したファイルだけを使用してください。**

ほかに、選択した行のリネーム、大文字・小文字だけのリネーム、Organizerのコピー先作成が競合した場合のエラー処理に不具合を確認し、修正を進めています。

修正コードと試験記録は[Draft PR #1](https://github.com/hiro1960486/ModuForge/pull/1)の`refactor/safe-root-layout`ブランチにあります。修正対象はリポジトリ直下の新しいモジュールです。**main・保持している旧FW33・既存のFileWorkbench Next v3.3.0-rc1・配布済みZIP/EXEには、この修正は反映されていません。** 作業ブランチでも旧`FW33/`から起動すれば修正前のコードです。作業ブランチは検証中であり、正式な修正版リリースではありません。

## 現在の部品

| フォルダー | 機能 |
|---|---|
| `01_tree` | ツリー構造 |
| `02_rename` | 一括リネーム |
| `03_preview` | プレビュー |
| `04_compare` | 比較 |
| `05_hash` | ハッシュ・重複 |
| `06_recycle` | ごみ箱・復元 |
| `07_tags` | タグ・メディア情報 |
| `08_organizer` | ファイル整理 |

各部品は `module/`（実装）・`api/`（公開インターフェース）の形で管理します。共通コードは`00_shared/`です。現時点では各部品に共通基盤への依存があり、完全な独立パッケージ化は未完了です。

## 試験

Windowsで`scripts/test_all.bat`を実行すると一括試験、`test_chord/test_start.bat`で試験用UIを起動できます。Pythonからは`python run_tests.py`です。

初期基準版では非GUIの**21件**をWindowsで合格確認済みです。既存6部品は主に構成・組み立ての検査であり、全機能の動作保証ではありません。

## 安全方針

- コピー・移動は確認を必要とし、同名ファイルを無断で上書きしません
- 実データではなく複製したサンプルで試験してください
- ログ・個人データ・DB・機密情報は公開リポジトリへアップロードしません
- タグ付きファイル移動後のタグDB追従など、統合未完了の範囲があります

## 資料

- [プロジェクト概要](docs/01_PROJECT_OVERVIEW.md)
- [モジュール台帳](docs/02_MODULE_CATALOG.md)
- [API接続方針](docs/03_API_CONTRACT.md)
- [試験ガイド](docs/04_TEST_GUIDE.md)
- [既知の制限](docs/05_KNOWN_LIMITATIONS.md)
- [変更履歴](CHANGELOG.md)


## 公開資料ライブラリ

- [開発資料公開室（Google Drive・閲覧用）](https://drive.google.com/drive/folders/1LNXJLESZWZ37oeZSP2_McYiSDEVtcDVC)
- [公開資料の一覧と位置づけ](docs/PUBLIC_DOCUMENTS.md)

構想資料には**未実装・未検証**の内容を含みます。GitHubのソースコードの状態や安全性の保証と混同しないでください。

## CI

GitHub Actionsで非GUIユニット試験を実行します。Windows GUI操作、実際のごみ箱連携、メディア再生は別途Windows実機で検証します。

**License:** 初期ソースの原本は `FW33/LICENSE.txt`、分類保管版は `migration_review/LICENSE.txt` です。全体の適用範囲は確認中です。

## 再構成作業中

現在のルート配置は **`refactor/safe-root-layout` 作業ブランチ**で検証中です。旧 `FW33/` は完全性照合と安全な切り戻しのため保持しています。新構成はまだ `main` に統合されていません。

- 単独GUI起動: `python run_component.py tree`（他の7部品も指定可）
- テスト: `python run_tests.py` または `scripts/test_all.bat`
- API仕様: [接続契約](docs/03_API_CONTRACT.md)
- 9件の旧資料: [分類台帳](docs/MIGRATION_DOCUMENT_INVENTORY.md)
- 受入試験: [チェックリスト](docs/FUNCTIONAL_ACCEPTANCE_CHECKLIST.md)

GUI表示と機能動作の合否は区別してください。ファイルの移動・リネーム・復元は複製データ以外に対して試験しないでください。

## 正式な管理先と独立開発

[管理方針](docs/REPOSITORY_CONSOLIDATION_20261010.md)に従い、ModuForgeとFileWorkbench-Nextは独立して開発・試験・版管理します。部品が整った後のNextへの組み込みは別作業です。
