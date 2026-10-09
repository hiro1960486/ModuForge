# API接続仕様・設計原則

ModuForgeの「API」は主にPythonプロセス内のモジュール接続インターフェースであり、HTTP APIではありません。

- 公開宣言: `FW33/<番号>_<モジュール>/api/module.json`
- 接続実装: `api/interface.py`
- 処理と画面: `module/module.py` と必要なサービス
- 共通契約: `FW33/00_shared/src/fileworkbench/interfaces/contracts.py`
- 共通アダプター: `FW33/00_shared/src/fileworkbench/interfaces/adapter.py`

## 設計指針
- 接続部は命令・入力・結果・エラーを正しく伝え、アプリ固有の判断を持ち込み過ぎない
- 利用先ごとの差分は接続アダプターで吸収する
- コピー・移動等の破壊的操作は、UI表示だけでなく操作側でも安全条件を確認する
- モジュール単体の合格とアプリ統合時の合格を明確に区別する
- APIの互換性が変わるときはバージョンと試験を更新する
