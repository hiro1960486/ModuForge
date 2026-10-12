# FileWorkbench Next 3.3 RC 部品・API研究パック

2026-10-09作成。保存済み FileWorkbench_Next_3.3_RC_Development_Derivative_TestFix.zip（版4）のソースを使用。GitHub上の現在のソースとの照合は行っていません。

6つのコンテンツの実装とAPIをフォルダー単位で分離しました。元ソースは内容を変えずにコピーしています。共通部品は00_sharedにまとめています。完全な依存なしの部品ではなく、共通UI・サービス・契約への依存を保持しています。

| フォルダー | コンテンツ | APIコマンド |
|---|---|---|
| 01_tree | 構成ツリー | refresh, scan, export, filter |
| 02_rename | 一括リネーム | configure, refresh, preview, rename |
| 03_preview | プレビュー | release, play, pause, stop, seek, refresh, next, previous |
| 04_compare | 左右比較 | refresh, compare, filter |
| 05_hash | HASH・重複 | refresh, scan, filter, export |
| 06_recycle | ごみ箱・復元 | search, restore |

## 開く順番

1. 各部品のREADME.mdで役割を確認する。
2. api/module.jsonで公開能力・入力・イベントを見る。
3. api/interface.pyでAPIから実装への接続を見る。
4. module/module.pyで画面・処理を読む。
5. DEPENDENCIES.txtと00_shared/src/fileworkbenchを見て共通部品を追う。

## 単独起動

Python 3.10以上の環境で、展開したルートを開いて実行します。

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python run_component.py tree
```

treeをrename、preview、compare、hash、recycleに置き換えて試せます。起動スクリプトは選んだ1部品だけを共通部品と組み立てます。ごみ箱のWindows連携にはWindowsが必要です。統合APPの選択連携・他コンテンツへのイベント転送は単独起動では提供しません。ファイル操作やリネームは実際の対象に作用するため、研究時はコピーした試験用ファイルを指定してください。

## APIの位置付け

ここでのAPIはPython内のModulePortインターフェースです。ネットワークAPIではありません。共通契約は00_shared/src/fileworkbench/interfaces/contracts.py、共通実装はadapter.pyにあります。各部品のinterface.pyが入力・コマンドを画面処理につなぎます。

00_sharedには共通API、イベント連携、ファイル操作、命名、再生、復元、ツリー出力、共通UIを収録しています。再利用に必要な依存を落とさないため、共通サービスは一式を保持しています。

## 検証範囲

原本コピーのバイト一致、APIコマンドとmodule.jsonの一致、Python構文、組み立て後のローカルimport解決、ZIP整合性を確認。今回の環境にはPySide6がないため、GUI起動・Windows機能の実行は未検証です。元アプリ全体の動作保証を追加するものではありません。

元ソースのライセンスはLICENSE.txtを参照してください。元の統合アプリ・旧版・EXE・ビルド成果物は収録していません。

## 適正化試験

`TEST_REPORT.md` を参照。2026-10-09に同名リネーム安全性と対象検証を修正。GUI実機試験は未実施。

## 追加モジュール 07_tags（0.1.0-test）
`python run_component.py tags` でタグ・メディア整理の試験用UIを起動できます。`07_tags/README.md` と `TAG_TEST_REPORT.md` を参照。統合アプリ本体は変更していません。
