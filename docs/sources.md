# 公式資料と確認した API

確認日は 2026-10-26 です。
公式ドキュメントだけでなく、公式 PyPI から取得した `nextmv==1.12.0` の実装と `inspect.signature` で実在する API を確認しました。
ドキュメントのページには古い例が残る場合があるため、このリポジトリの実行確認は固定した版に対するものです。

| 対象 | 公式資料 |
| --- | --- |
| 概要と名前空間 | [Python SDK](https://docs.nextmv.io/python-sdk/) |
| 配布版 | [PyPI nextmv 1.12.0](https://pypi.org/project/nextmv/1.12.0/) |
| 実装 | [nextmv-io/nextmv-py](https://github.com/nextmv-io/nextmv-py) |
| オプション | [Options](https://docs.nextmv.io/python-sdk/modeling/options/) |
| 入力 | [Input](https://docs.nextmv.io/python-sdk/modeling/input/) |
| 出力 | [Output](https://docs.nextmv.io/python-sdk/modeling/output/) |
| ローカル実行 | [Run Applications](https://docs.nextmv.io/python-sdk/local/runs/) |
| 配備 | [Deploy](https://docs.nextmv.io/python-sdk/cloud/deploy/) |
| クラウド実行 | [Run Applications](https://docs.nextmv.io/python-sdk/cloud/run-applications/) |
| 入力管理 | [Managed Inputs](https://docs.nextmv.io/python-sdk/cloud/use-managed-inputs/) |
| バッチ実験 | [Batch Experiments](https://docs.nextmv.io/python-sdk/cloud/run-batch-experiments/) |
| シナリオ試験 | [Scenario Tests](https://docs.nextmv.io/python-sdk/cloud/run-scenario-tests/) |
| 受け入れ試験 | [Acceptance Tests](https://docs.nextmv.io/python-sdk/cloud/run-acceptance-tests/) |
| OR-Tools | [Assignment](https://developers.google.com/optimization/assignment/assignment_example) |

## 固定版で確認した差異

| 項目 | このリポジトリでの扱い |
| --- | --- |
| `nextmv.Model` | 1.12.0 の公開モジュールと配布ファイルに存在しないため、通常の Python クラスで構造を示す |
| `Output.statistics` | 実装に非推奨の記載がある。`Output.metrics` を使う |
| `new_run` の条件 | `options=` を使う |
| `new_run_with_result` の条件 | `run_options=` を使う。2つのメソッドで引数名が異なる |
| 状態 | `metadata.status_v2` と `StatusV2` を使う |
| ログ | ローカルの `run_logs` は文字列、クラウドの `run_logs` は `RunLog` |
| ポーリング | `PollingOptions` に待機の上限を明示する |
| 真偽値 | 真とみなす文字列以外は偽に変換される。厳密な入力検証とは異なる |
| 複数ファイルの指標 | `metrics.json` は `{"metrics": {...}}` の形で書き出される |
| ローカル登録情報 | 公開 API で保存先を指定できないため、内部定数を一時的に隔離する |
| SDK の `push` | 版とインスタンスの作成を別途呼ぶ |
| クラウドの「offline tests」 | ネットワーク不要という意味ではない |

## 手元で署名を確認する

以下はインストール済みのコードを確認するだけで、クラウドに接続しません。

```bash
uv run --locked python - <<'PY'
import inspect
from importlib.metadata import version
import nextmv
from nextmv import cloud, local
print(version("nextmv"))
print(inspect.signature(nextmv.Output))
print(inspect.signature(local.Application.new_run))
print(inspect.signature(cloud.Application.new_acceptance_test))
PY
```

依存関係の更新時は `pyproject.toml`、`uv.lock`、クラウド用の `requirements.in` と `requirements.cloud.txt` を整合させてください。
クラウド用の依存関係はローカルの Python 3.12 用とは別に解決しています。
固定しているのは Python パッケージで、クラウド側のランタイムイメージのダイジェストやサービス実装まで固定しているわけではありません。
