# 04 CSV と JSON の複数ファイル

対象 API は `ContentFormat.MULTI_FILE`、`csv_data_file`、`json_data_file`、`csv_solution_file`、`json_solution_file` です。
担当者ごとの費用を CSV から、費用倍率を JSON から読みます。

## 最小の実行

```bash
uv run --locked python examples/core/04_multi_file/main.py
```

次のファイルができます。

```text
artifacts/multi-file/
  metrics.json
  solutions/
    assignments.csv
    summary.json
```

`assignments.csv` は3行の割り当て、`summary.json` は `{"total_cost": 9.0}` です。
`metrics.json` は `{"metrics": {"value": 9.0, "assigned_count": 3}}` という構造です。
標準出力は空で、保存先の案内は標準エラー出力に出ます。

## 変更する値

```bash
uv run --locked python examples/core/04_multi_file/main.py --input-dir examples/core/04_multi_file/inputs --output-dir artifacts/another-output
```

`inputs/settings.json` の `cost_scale` を `2` にすると合計費用は `18` になります。
`input_data_key` により `data.data["costs"]` と `data.data["settings"]` の名前でアクセスします。
CSV の値は文字列なので、サンプルでは `float(row["cost"])` で変換しています。

## よくある失敗

- `--input-dir` はファイル名ではなくディレクトリ名です。
- `costs.csv` がないとファイル読み込みに失敗します。
- CSV の `cost` 列に数値でない文字列があると、変換時に `ValueError` になります。
- `--output-dir` 直下に CSV があるとは限りません。既定では `solutions/` の下に入ります。

公式資料：[Input](https://docs.nextmv.io/python-sdk/modeling/input/)、[Output](https://docs.nextmv.io/python-sdk/modeling/output/)。
