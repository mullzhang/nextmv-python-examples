# 05 モデルの構造

対象 API は `Input` と `Output` です。
`AssignmentModel.solve(data)` に計算をまとめ、`main()` は読み込みと書き出しを担当します。
`solve` はファイルや標準入力に触れず、受け取った入力から結果を返します。

## 最小の実行

```bash
uv run --locked python examples/core/05_model/main.py < data/assignment.json
```

入力順に `aki→pack`、`ben→ship`、`chi→check` と割り当て、`metrics.value` は `14` になります。
最適性を主張する例ではありません。
費用行列を変えると、対角要素の和が出力されます。

## 計算部分を変える

`solve` の割り当て処理だけを置き換えれば、入出力を保ったまま別の探索方法を使えます。
[OR-Tools 編](../../solver/01_ortools/README.md) は同じ `Input → Output` の境界に CP-SAT を接続します。

## よくある失敗

古い資料にある `nextmv.Model` は、固定した SDK 1.12.0 の公開モジュールに存在しません。
`class AssignmentModel(nextmv.Model)` と書くと `AttributeError` になります。
この例のクラスはリポジトリ側で定義した通常の Python クラスです。

この例は担当者と作業が同数の入力を想定し、件数が異なると `zip(..., strict=True)` が失敗します。
行列の形や費用の型まで検証したい場合は、OR-Tools 編の入力検証も参照してください。

確認資料：[SDK ソース](https://github.com/nextmv-io/nextmv-py/tree/develop/nextmv/nextmv)、[バージョンの差異](../../../docs/sources.md)。
