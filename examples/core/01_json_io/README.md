# 01 JSON の入出力

対象 API は `nextmv.load`、`ContentFormat.JSON`、`Input.data`、`Output`、`nextmv.write` です。
最適化を行わず、入力から担当者と作業を取り出して返します。
以下のコマンドはリポジトリのルートで実行します。

## 最小の実行

```bash
uv run --locked python examples/core/01_json_io/main.py --input data/assignment.json
```

結果の主要部分は次のとおりです。
SDK は空の `options` と `assets` も付けます。

```json
{
  "solution": {"workers": ["aki", "ben", "chi"], "tasks": ["pack", "ship", "check"]},
  "metrics": {"worker_count": 3, "task_count": 3}
}
```

## 入出力先を変える

```bash
uv run --locked python examples/core/01_json_io/main.py < data/assignment.json
mkdir -p artifacts
uv run --locked python examples/core/01_json_io/main.py --input data/assignment.json --output artifacts/io.json
```

`--input` を省略すると標準入力から読み、`--output` を省略すると標準出力へ書きます。
この2つはファイル名を扱うための `argparse` の引数です。
SDK の `Options` は次の例で扱います。
JSON の `workers` または `tasks` に項目を追加すると、返される件数が変わります。

## よくある失敗

- 標準入力も `--input` も渡さないと、入力待ちになります。
- JSON の末尾のカンマや閉じ括弧不足は `JSONDecodeError` になります。
- `workers` または `tasks` がない入力は `KeyError` になります。この例の入力形式は上記の形です。
- 出力ファイルとログを混ぜないため、診断用の文字列を `print` で標準出力に書かないようにします。

公式資料：[Input](https://docs.nextmv.io/python-sdk/modeling/input/)、[Output](https://docs.nextmv.io/python-sdk/modeling/output/)。
