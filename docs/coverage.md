# SDK の機能対応表

「実行確認」はこの Mac で SDK を使って実行した範囲です。
「送信前検証」はネットワークを使わず SDK の型と呼び出しを確認した範囲で、クラウドの動作確認を意味しません。
「説明のみ」の機能は実行スクリプトを含みません。

| 機能 | サンプルまたは資料 | 検証範囲 |
| --- | --- | --- |
| JSON、ファイル、標準入力、標準出力 | [core/01_json_io](../examples/core/01_json_io/README.md) | 実行確認 |
| 型、既定値、必須値、環境変数、優先順位 | [core/02_options](../examples/core/02_options/README.md) | 実行確認、変換と失敗のテスト |
| solution、metrics、ログ、終了コード | [core/03_outputs_errors](../examples/core/03_outputs_errors/README.md) | 成功と失敗を実行確認 |
| CSV と JSON の複数ファイル | [core/04_multi_file](../examples/core/04_multi_file/README.md) | 入出力のファイル内容を確認 |
| Model の構造 | [core/05_model](../examples/core/05_model/README.md) | 通常のクラスで実行確認。1.12.0 に `nextmv.Model` はない |
| マニフェストとアプリ内の options | [apps/assignment](../apps/assignment/README.md) | SDK による読込と実行確認 |
| local.Application、非同期実行、ポーリング | [local/run.py](../examples/local/run.py) | 子プロセスを実際に実行 |
| 結果、状態、履歴、入力、ログ | [local/history.py](../examples/local/history.py) | 実際の保存データを再読込 |
| 再現、条件変更、比較 | [local/sweep.py](../examples/local/sweep.py) | 再実行と4条件の費用を確認 |
| OR-Tools CP-SAT | [solver/01_ortools](../examples/solver/01_ortools/README.md) | 最適値、制約、解なし、入力エラー |
| 認証、既存アプリ取得 | [cloud_course/auth.py](../cloud_course/auth.py) | 送信前検証 |
| push、version、instance | [cloud_course/deploy.py](../cloud_course/deploy.py) | 署名とマニフェストを検証。配備未実行 |
| 非同期送信、状態、結果、ログ、取消 | [cloud_course/runs.py](../cloud_course/runs.py) | 送信前検証、呼び出しの分岐 |
| アップロード、managed input、input set | [cloud_course/inputs.py](../cloud_course/inputs.py) | 送信前検証、呼び出し順序と型 |
| バッチ実験 | [cloud_course/batch.py](../cloud_course/batch.py) | 2条件の定義と再開時の非再送 |
| シナリオ試験 | [cloud_course/scenarios.py](../cloud_course/scenarios.py) | 定義と再開時の非再送 |
| 受け入れ試験 | [cloud_course/acceptance.py](../cloud_course/acceptance.py) | 指標条件と再開時の非再送 |
| 外部実行、ローカル結果の同期 | [上級機能](advanced.md) | 説明のみ |
| シャドーテスト、スイッチバック試験 | [上級機能](advanced.md) | 説明のみ |
| 実行クラス、キュー、秘密情報、SSO | [上級機能](advanced.md) | 説明のみ |
| Asset、可視化、独自ファイル読込 | [上級機能](advanced.md) | 説明のみ |
| 実行の複製、比較、アンサンブル | [上級機能](advanced.md) | 説明のみ |

SDK 全メソッドの実装を目指すものではありません。
まず入出力と実行を動かし、その結果を比較するための機能を一巡できる範囲を実装しています。
未実装機能を追加する場合は、[公式資料](sources.md) と固定版の実装で署名を確認してください。
