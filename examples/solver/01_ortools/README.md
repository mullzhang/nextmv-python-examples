# OR-Tools の割り当て問題を Nextmv につなぐ

対象 API は Nextmv の `Options`、`Input`、`Output`、`log` と、OR-Tools の `CpModel`、`CpSolver` です。
Nextmv が入出力と実行条件を扱い、CP-SAT が組み合わせを探索します。

## 最小の実行

```bash
uv run --locked python examples/solver/01_ortools/main.py < data/assignment.json
```

解は `aki→ship`、`ben→pack`、`chi→check` で、`metrics.value` は `9.0`、`metrics.status` は `OPTIMAL` です。
`metrics.duration` は実測時間なので実行ごとに変わります。
テストでは全列挙による最小値とも比較しています。

## 条件を変える

```bash
uv run --locked python examples/solver/01_ortools/main.py --duration 1 --seed 7 < data/assignment.json
```

`duration` は探索時間の上限秒数、`seed` は乱数シードです。
探索スレッドを1つに固定していますが、実行時間や極端に短い制限下の探索結果まで同一になる保証はありません。
各担当者は最大1件、各作業はちょうど1人という制約を `add_at_most_one` と `add_exactly_one` で表現しています。

## よくある失敗

- 費用行列の大きさが担当者数と作業数に合わないと `ValueError` になります。
- CP-SAT に渡す費用は非負の整数です。小数を扱うなら、単位をそろえて整数化する設計が必要です。
- 担当者より作業が多い場合、制約上は `INFEASIBLE` です。これはプロセスの失敗ではなく、空の解と状態を返します。
- `OPTIMAL` と `FEASIBLE` 以外では変数の値を読みません。時間不足による `UNKNOWN` も解が見つかった状態とは分けます。

公式資料：[OR-Tools の割り当て問題](https://developers.google.com/optimization/assignment/assignment_example)。
