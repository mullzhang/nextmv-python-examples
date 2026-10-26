# ローカルとクラウドで共用する割り当てアプリ

`main.py` は `nextmv.load()` で `app.yaml` のオプション定義を読み、`nextmv.write()` で結果を出します。
ローカルの管理 API を使う手順は [ローカル編](../../examples/local/README.md)、配備手順は [クラウド編](../../cloud_course/README.md) にあります。

直接実行する場合は、マニフェストを読めるようアプリのディレクトリで起動します。

```bash
cd apps/assignment
../../.venv/bin/python main.py --strategy greedy < ../../data/assignment.json
```

`strategy=greedy` の費用は `10`、`strategy=enumerate` は `9` です。
`cost_scale` を `2` にすると費用が2倍になり、`details=false` で診断ログを省略できます。
`strategy` の不明な値、件数の不一致、9件以上の入力、0以下の倍率はエラーです。
このアプリの全列挙は SDK の実験機能を試す小例で、大規模入力には向きません。

`app.yaml` の `files` は配備やローカル実行に含めるソースを指定します。
入力データは実行時に渡すため、ここには含めていません。
`python.pip-requirements` は SDK の版を固定し、ローカルではリポジトリの `.venv` を使用します。
クラウドの配備スクリプトは、この項目だけを `requirements.cloud.txt` に置き換えて推移的依存も固定します。
マニフェストのファイル自体は書き換えません。

クラウド用依存を更新する場合のコマンドは次です。
更新後にはローカル検証と、別途クラウドでの確認が必要です。

```bash
uv pip compile apps/assignment/requirements.in --python .venv/bin/python --python-version 3.11 --python-platform aarch64-manylinux_2_34 --no-python-downloads --generate-hashes --output-file apps/assignment/requirements.cloud.txt
```
