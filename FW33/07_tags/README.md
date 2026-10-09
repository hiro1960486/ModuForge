# タグ・メディア整理モジュール（追加試験版）

`python run_component.py tags` で単独起動します。外部DB `~/.fileworkbench_next/tags.sqlite3` にパスとタグを格納し、元ファイルを変更しません。タグの検索は完全一致です。画像プレビュー、動画・音声再生（対応コーデックに依存）、ファイルの基本情報表示、移動先のフォルダー選択、移動前の確認を備えます。

移動は同名衝突を拒否し、ファイルを上書きしません。タグを保存したファイルを本モジュールから移動するとDB内の参照も更新します。外部でファイルを移動した場合は追跡しません。タグはファイルそのものに埋め込まず、このDB内だけで管理するため、元ファイルを別PCへコピーしてもタグは付きません。

APIコマンド: `set_files {paths:[]}`, `set_tags {path,tags}`, `list_tags {path}`, `search_tags {tag}`, `inspect {path}`, `plan_move {path,destination}`, `move {path,destination,confirm:true}`, `refresh`。

**制限**: 再生時間やEXIFなどの詳細メタデータ抽出は未搭載。移動のクロスドライブ中断時のロールバック・同時操作の競合対策・元のNEXTプレビュー画面への直接組み込みは未実装。実ファイルの移動は試験用コピーだけで行ってください。
