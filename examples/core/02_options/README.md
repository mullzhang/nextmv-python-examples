# 02 型付きオプション

対象 API は `Option`、`Options`、`Options.parse`、`Options.to_dict` です。
入力ファイルは不要で、オプション自体を JSON に出力します。

## 最小の実行

```bash
uv run --locked python examples/core/02_options/main.py --label first
```

`output.options` は次の形になります。

```json
{"label": "first", "limit": 3, "cost_scale": 1.0, "details": false}
```

## 値と優先順位を変える

| 引数 | 型 | 既定値 | 環境変数 |
| --- | --- | --- | --- |
| `--label` | `str` | なし、必須 | `LABEL` |
| `--limit` | `int` | `3` | `LIMIT` |
| `--cost_scale` | `float` | `1.0` | `COST_SCALE` |
| `--details` | `bool` | `false` | `DETAILS` |

```bash
LABEL=environment LIMIT=8 COST_SCALE=1.5 uv run --locked python examples/core/02_options/main.py --limit 2 --details true
uv run --locked python examples/core/02_options/main.py --help
```

この場合は `label=environment`、`limit=2`、`cost_scale=1.5` です。
優先順位はコマンドライン、環境変数、既定値の順です。
`details=true` では標準エラー出力に診断を書きます。

## よくある失敗と注意点

`label` を渡さないと必須オプションの `ValueError`、`--limit abc` は整数変換のエラーになります。
型の指定だけでは正の値という制約までは検証しないため、コード側で `limit > 0` と `cost_scale > 0` を確認しています。

真偽値は値を伴う引数なので、`--details true` と指定します。
SDK 1.12.0 は `true`、`1`、`t`、`y`、`yes` を真、それ以外の文字列を偽に変換します。
たとえば `--details maybe` はエラーにならず偽です。
不明な文字列の拒否が必要なアプリでは、別途入力を検証してください。
`Options` は未知の引数を無視するため、オプション名の打ち間違いにも注意が必要です。

公式資料：[Options](https://docs.nextmv.io/python-sdk/modeling/options/)。
