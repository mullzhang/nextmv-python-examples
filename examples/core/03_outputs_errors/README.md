# 03 解と指標、ログ、失敗

対象 API は `Output.solution`、`Output.metrics`、`nextmv.log`、`nextmv.write` です。
解の詳細は `solution`、比較に使う値は `metrics` に置きます。

## 最小の実行

```bash
mkdir -p artifacts
uv run --locked python examples/core/03_outputs_errors/main.py > artifacts/output.json 2> artifacts/output.log
```

`output.json` は JSON として読め、`solution.assignments` が1件、`metrics.value` が `9`、`metrics.status` が `feasible` になります。
`output.log` には開始と完了の日本語メッセージが入ります。
`metrics.status` はこのアプリが定義した指標で、クラウドの実行状態を示す `metadata.status_v2` とは別物です。

## 失敗を起こす

```bash
uv run --locked python examples/core/03_outputs_errors/main.py --fail true
```

`--fail` を切り替えると、標準エラー出力に入力エラーを書き、終了コード `2` で終わります。
この経路では解の JSON を出しません。
コード内の割り当てや `metrics` を変更すると、出力構造を確認できます。

## よくある失敗

- 標準出力にログを混ぜると、出力全体が JSON でなくなります。診断には `nextmv.log` を使います。
- `statistics` は現行 SDK では非推奨です。この例では `metrics` だけを使います。
- プロセスの異常終了と、最適化問題に実行可能解がない状態は異なります。[OR-Tools 編](../../solver/01_ortools/README.md) では `INFEASIBLE` を通常の出力として返します。

公式資料：[Output](https://docs.nextmv.io/python-sdk/modeling/output/)、[Logging](https://docs.nextmv.io/python-sdk/modeling/logging/)。
