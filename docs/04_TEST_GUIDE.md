# ModuForge 現行試験ガイド
対象：refactor/safe-root-layoutのリポジトリ直下。main統合前の開発版です。
FileWorkbench-Nextとは独立して試験します。

## Windowsで開く
正式作業フォルダー E:\00_GitHub\ModuForge で修正ブランチを使用します。
1. python -m pip install -r requirements.txt
2. python run_tests.py（または scripts/test_all.bat）
3. python run_component.py tree（rename/preview/compare/hash/recycle/tags/organizerも指定可）

FW33からの起動は旧版です。修正版の試験には使用しないでください。
GUI表示だけではスキャン、出力、メディア、移動、復元の機能合格とは扱いません。

## 自動検証
- python run_tests.py：今回の確認では44件合格。将来追加で件数は変わります。
- python scripts/audit_flat_layout.py：旧133ファイルの対応先・許容差分を照合。
- python scripts/test_staged_acceptance.py：2件。API宣言/構文と試験用データの確認であり、実スキャン・比較アルゴリズムの動作保証ではありません。
- python scripts/smoke_root_gui.py：Qt offscreenの生成/終了。Windows実操作とは別。
- FW33/run_tests.py：旧版21件の保存確認専用。

## 手元のstagingを照合
python scripts/compare_local_staging.py --staging E:\00_GitHub\ModuForge_staging

比較は読み取り専用。SHA256一致件数、同じパスの差分、片側のみのパス、読み取りエラー、除外対象をJSONで表示します。
ファイル本文を表示せず、コピー・削除・マージを行いません。
異なるファイルはどちらが最新か自動判定しません。stagingにしかないDBや設定をソースとして公開しないでください。
.git/venv/build/dist等は除外するため、結果だけでフォルダー全体の削除可否は決まりません。リンク/ジャンクションや読取失敗があれば終了コード2で停止します。

## Windows受入と記録
移動・リネームは複製した試験データで、元/先・確認拒否・同名衝突・本文保持を確認します。
実ごみ箱の復元試験は隔離したテストユーザー/VMを用意して実施します。
最新の範囲はFINAL_ACCEPTANCE_STATUS_20261010.mdと各安全性報告を参照。
44件合格だけでは正式リリース・FW33撤去完了と扱いません。
