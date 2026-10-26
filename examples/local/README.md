# ローカルのアプリ実行と履歴

`apps/assignment/` の `app.yaml` を使って実行します。
すべてのコマンドをリポジトリのルートで起動してください。
依存関係はルートの `uv sync --locked` で事前に用意します。

## 1. アプリを実行する

対象 API は `local.Application`、`new_run`、`run_result_with_polling`、`PollingOptions`、`run_logs` です。

```bash
mkdir -p artifacts
uv run --locked python -m examples.local.run > artifacts/local-run.json
```

まず実行 ID が標準エラー出力に出て、その後に結果が `local-run.json` に保存されます。
`metadata.status_v2` が `succeeded`、`output.metrics.value` が `10` になります。
`output` の中身はアプリの出力で、外側の `metadata` は SDK が記録した実行情報です。

`run.py` の `options={"strategy": "greedy"}` を `enumerate` に変えると費用は `9` になります。
待機条件は `PollingOptions(max_duration=60, max_tries=120)` で指定しています。
タイムアウトは待機の終了であり、実行のキャンセルを意味しません。

よくある失敗は `app.yaml` の不足、`files` に必要な Python ファイルを含め忘れること、依存関係が未導入であることです。
`metadata.status_v2=failed` の場合は、実行 ID を使って `run_logs` を読みます。
このサンプルも失敗時は終了コード `1` を返します。

## 2. 履歴を読み、同じ条件で再実行する

対象 API は `list_runs`、`run_information`、`run_input`、`run_result`、`run_logs`、`new_run_with_result` です。

```bash
uv run --locked python -m examples.local.history
uv run --locked python -m examples.local.history --run-id local-実際のID
uv run --locked python -m examples.local.history --run-id local-実際のID --replay
```

最初のコマンドは `runs` 配列を返します。
履歴がなければ空配列なので、先に1番のコマンドを実行してください。
詳細取得では入力、出力、実行情報、ログをまとめて確認できます。
`--replay` では保存した入力と、既定値を含む確定済みのオプションを使って新しい実行を作ります。
同じコードなら `same_solution: true` になることを確認できます。

`--run-id` で参照先を変えられます。
存在しない ID はエラーになります。
`--replay` だけを指定すると、必要な ID がないため終了コード `2` になります。
この例は成功した実行を再現するもので、失敗した実行には使えません。

履歴はアプリのソースを版として固定する機能ではありません。
コード、入力、依存関係、オプション、乱数条件もそろえて比較してください。
時刻、実行 ID、経過時間は再実行ごとに変わります。

## 3. 条件を変えて比較する

対象 API は `new_run_with_result(run_options=...)` と `RunResult.output` です。

```bash
uv run --locked python -m examples.local.sweep > artifacts/sweep.json
```

| strategy | cost_scale | 期待する value |
| --- | ---: | ---: |
| greedy | 1 | 10 |
| greedy | 2 | 20 |
| enumerate | 1 | 9 |
| enumerate | 2 | 18 |

`sweep.py` の2つのリストを変えると比較条件を増やせます。
実行結果には入力、コード、マニフェスト、`uv.lock` の SHA-256 と SDK、Python の版も付けます。
失敗した実行は費用を無理に読み取らず、その ID とログを含む例外で停止します。
`run_options` の値は文字列で渡し、アプリ内の `Options` が指定された型に変換します。

## 保存場所と実行環境

履歴は `apps/assignment/.nextmv/runs/<run_id>/`、登録情報は `artifacts/local-registry/registry.yaml` に保存されます。
SDK 1.12.0 は `Application` の初期化時にホームの登録情報を読み書きしますが、登録先を変更する公開 API がありません。
このリポジトリでは `support.local_environment()` で登録先の内部定数だけを一時的に差し替えます。
ホームの設定や認証情報は使用せず、`HOME` も変更しません。
`Application` と実行、履歴、結果取得のメソッドは SDK の実装をそのまま使用します。
この隔離箇所は固定バージョンに依存するため、SDK 更新時に再確認が必要です。

SDK の子プロセスは uv を使って Python アプリを起動します。
補助処理は既存の `.venv` を指定し、`UV_OFFLINE=1` で実行時の追加ダウンロードを止めます。
`--no-project` に関する uv の警告がログに出る場合がありますが、実行状態と出力で成功を判断してください。

公式資料：[Run Applications](https://docs.nextmv.io/python-sdk/local/runs/)。
