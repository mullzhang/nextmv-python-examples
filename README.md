# Nextmv Python SDK の機能別サンプル

小さな担当者割り当てを題材に、SDK の入出力、オプション、ローカル実行、クラウド操作を個別に試せるリポジトリです。
各サンプルは対象の API を直接呼び出します。
基本編とローカル編には Nextmv アカウントが不要です。
クラウド編は独立したコースで、通常の実行では送信内容の表示だけを行います。

## 最初の実行

リポジトリのルートで次を実行します。
Python 3.12.13 と uv を使用し、依存関係を `.venv` に作成します。
初回の依存取得にはインターネット接続が必要です。

```bash
export UV_CACHE_DIR="$PWD/.uv-cache"
uv sync --locked
uv run --locked python examples/core/01_json_io/main.py --input data/assignment.json
```

標準出力に JSON が表示され、`metrics.worker_count` と `metrics.task_count` はともに `3` になります。
続けて [01 JSON の入出力](examples/core/01_json_io/README.md) を読むと、標準入力から渡す方法とファイルに保存する方法を試せます。

## 読む順番

| 順番 | サンプル | 確認すること |
| --- | --- | --- |
| 1 | [JSON の入出力](examples/core/01_json_io/README.md) | `load`、`Input`、`Output`、`write` |
| 2 | [型付きオプション](examples/core/02_options/README.md) | 型、既定値、必須値、環境変数、優先順位 |
| 3 | [解と指標、ログ、失敗](examples/core/03_outputs_errors/README.md) | `solution`、`metrics`、`log`、終了コード |
| 4 | [CSV と JSON の複数ファイル](examples/core/04_multi_file/README.md) | `DataFile`、`SolutionFile`、`ContentFormat` |
| 5 | [モデルの構造](examples/core/05_model/README.md) | `Input → solve → Output` を分ける |
| 6 | [ローカル実行](examples/local/README.md) | `app.yaml`、`local.Application`、履歴、再実行、条件比較 |
| 7 | [OR-Tools との接続](examples/solver/01_ortools/README.md) | CP-SAT の解と終了状態を SDK 出力へ変換 |
| 別コース | [クラウド編](cloud_course/README.md) | 認証、配備、実行、入力管理、実験、受け入れ試験 |

[機能対応表](docs/coverage.md) には実装した範囲と説明のみの範囲を分けて記載しています。
[上級機能](docs/advanced.md)、[公式資料とバージョンの差異](docs/sources.md)、[検証方法と記録](docs/verification.md) も参照できます。

## 共通の入力

[data/assignment.json](data/assignment.json) の費用行列は、行が担当者、列が作業です。
各作業を1人に割り当て、各担当者が受け持つ作業を最大1件にします。

| 担当者 | pack | ship | check |
| --- | ---: | ---: | ---: |
| aki | 9 | 2 | 7 |
| ben | 6 | 4 | 3 |
| chi | 5 | 8 | 1 |

入力順の割り当ては費用 `14`、作業ごとに最安の空いている担当者を選ぶ貪欲法は `10`、全列挙と OR-Tools の最適解は `9` です。
同じ入力を使うので、アルゴリズムと SDK の役割を分けて読めます。
全列挙は小さい入力専用で、アプリでは最大8件に制限しています。

## 固定した環境

| 項目 | 固定値 |
| --- | --- |
| ローカルの Python | `3.12.13`（`.python-version`） |
| Nextmv SDK | `1.12.0` |
| OR-Tools | `9.15.6755` |
| pytest | `9.1.1` |
| Ruff | `0.17.2` |
| ローカルの依存関係全体 | `uv.lock` |
| クラウド用ランタイムの指定 | `ghcr.io/nextmv-io/runtime/python:3.11` |
| クラウド用依存関係 | `apps/assignment/requirements.cloud.txt`（版とハッシュを固定） |

セットアップには既存の uv `0.11.16` を使用しました。
SDK 自身の依存として uv `0.13.5` も `.venv` 内に入り、SDK のローカル子プロセスが使用します。
クラウドのランタイム指定は SDK の `ManifestRuntime` に合わせています。
ローカルの Python 3.12.13 とクラウドの Python 3.11 は同じ環境ではありません。
クラウド上での実行結果は未確認です。

SDK 1.12.0 には `nextmv.Model` がありません。
モデル編は通常の Python クラスとして構成し、古い API を仮定した互換処理は入れていません。
指標には `Output.metrics` を使用し、非推奨の `statistics` は使用しません。

## まとめて検証する

```bash
uv run --locked python scripts/verify.py
```

Ruff、整形確認、pytest を実行し、結果を `artifacts/verification.json` に保存します。
テストはクラウドの認証情報を要求せず、Python のネットワーク接続を拒否して実行します。
クラウド編について確認するのは送信内容、SDK の型、メソッドの署名、処理の分岐です。
Nextmv Cloud のサービス側の動作確認は含みません。

生成物は `artifacts/`、`apps/assignment/.nextmv/`、`.uv-cache/` に保存され、Git の対象外です。
ローカル登録情報も `artifacts/local-registry/` に隔離します。
詳しくは [ローカル編の環境](examples/local/README.md#保存場所と実行環境) を参照してください。
