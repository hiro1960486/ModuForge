# Windowsローカルstaging比較判定（2026-10-10）
利用者から提供されたPowerShell出力に基づく。こちらから利用者PCへ直接アクセスした検証ではない。
正式作業先 E:\00_GitHub\ModuForge、比較先 E:\00_GitHub\ModuForge_staging。
修正ブランチ292ef0eへfast-forward後に比較。304対152ファイル、バイト一致40、改行正規化後の内容差分19、stagingのみ15、読取エラー0（初回全結果ではリンク0）。

## 19差分のレビュー
- CI2：新ルート試験と旧原本照合へ変更。
- safety/file_operations/naming：Windowsの文字種だけ変更を厳密文字列比較で扱う修正。
- Rename：選択行にフルパスを設定する修正。
- Preview実装/API2：画像表示追加と実装に対応するコマンド/コンテキスト修正。メディア全機能合格の保証とは別。
- Tags/Organizer2：空欄拒否と競合時の既存先保護。
- README、概要、API契約、試験ガイド：新ルートへの更新。
- run_tests、validate_staging、tests/README、Tags/Organizer試験：試験選択・キャッシュ扱い・回帰試験更新。
提示された内容差分ではstaging独自のコードを回収する必要は認められず、ModuForgeを現行作業元とする。

## stagingだけの15ファイル
移行注意書き、別配置の旧資料・サンプル・GUIランナー、BAT.original、test_start.bat。
この一覧は内容一致を証明しない。未照合の資料および除外した環境/ビルドの保持のため、stagingは削除せず保管名へ変更する。
実際の名称変更と新ルートWindows試験は利用者PCの結果を待つ。
main統合・FW33撤去・正式リリースは未完了。FileWorkbench-Nextへは組み込まない。
