# 左右比較 (compare)

左右フォルダーの比較と絞り込み

## ファイル

- module/: 実装（module.py、補助ファイル、パッケージ定義）
- api/: 外部から呼ぶ窓口（interface.py）と能力定義（module.json）
- 共通依存: ../00_shared/。詳細は DEPENDENCIES.txt。

## API

Python内で使うAPIです。HTTP/RESTサーバーではありません。
窓口クラス: `CompareInterface`

共通メソッド: create_widget(parent=None), receive_context(context), current_context(), execute(command, payload=None), subscribe(callback), unsubscribe(callback), shutdown()。
入力: ModuleContext(selected_paths, working_directory, options, source_module)。
イベント: ModuleEvent(name, source, payload)。

- 受付入力（元の定義）: left_folder, right_folder, left_path, right_path, files
- 実装済みコマンド: refresh, compare, filter
- イベント（元の定義）: context.received, command.completed, module.error, preview.requested, files.will_change, files.changed, rename.requested, target.individual_requested

実際の引数の扱い・条件分岐は api/interface.py の apply_context と commands を参照してください。
能力一覧とAPIコマンド一覧は別です。画面にある操作すべてが execute で呼べるとは限りません。

## 試す

ZIP全体を展開し、ルートで `python run_component.py compare` を実行します。
このフォルダーだけを移動する場合は 00_shared、run_component.py、requirements.txt も必要です。
