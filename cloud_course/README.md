# クラウド編

このコースは基本編を先に実行しなくても使えます。
リポジトリのルートで `uv sync --locked` を済ませ、各章のモジュールを実行してください。
共通の入力は `data/assignment.json`、配備するアプリは `apps/assignment/` です。

**このリポジトリの作成時にはクラウドを実行していません。**
各コマンドは既定で送信予定を表示するだけで、API キーも読みません。
実際に接続するのは `--execute` を付けた場合です。
その場合は Nextmv のアカウント、権限、既存のアプリが必要で、実行枠や利用料金の対象になり得ます。
自動テストはこのフラグを使いません。

Nextmv の文書で試験を「offline tests」と呼ぶ場合は、本番の意思決定から離れた評価という意味です。
クラウドのシナリオ試験や受け入れ試験には、ネットワーク接続とクラウドでの実行が必要です。
ここでいう「ネットワークなしの検証」とは区別してください。

## 1. 認証とアプリ情報の取得

対象 API は `cloud.Client` と `cloud.Application.get` です。
最小の実行は次です。

```bash
uv run --locked python -m cloud_course.auth
```

`mode=preview`、`network=false`、認証用の環境変数名が表示されます。
キーそのものは出力しません。
実際に接続する準備として、[Nextmv Console](https://cloud.nextmv.io/) で使う既存アプリと API キーを用意します。
アプリ作成をこのスクリプトが代行することはありません。

```bash
# 実行する場合のみ、手元でプレースホルダーを置き換える。
export NEXTMV_API_KEY='YOUR_API_KEY'
uv run --locked python -m cloud_course.auth --app-id YOUR_APP_ID --execute
```

`YOUR_...` のままではエラーになります。
`.env.example` は説明用で、自動読み込みは行いません。
成功時には `app_id` と `connected=true` が返る想定です。
`--app-id` で参照するアプリを変更できます。
キー未設定はローカルで失敗し、無効なキー、権限不足、存在しないアプリは API からエラーになります。

## 2. 配備、バージョン、インスタンス

対象 API は `Manifest.from_yaml`、`Application.push`、`new_version`、`new_instance`、`InstanceConfiguration` です。

```bash
uv run --locked python -m cloud_course.deploy
```

送信予定にはソースディレクトリ、版 `sdk-v1`、インスタンス `sdk-greedy` と `sdk-enumerate` が表示されます。
`push` はコードを配備しますが、SDK のこのメソッド自体は版やインスタンスを作りません。
そのためサンプルではそれぞれ明示して呼び出します。
基準側のインスタンスには `strategy=greedy`、候補側には `strategy=enumerate` を設定します。

```bash
uv run --locked python -m cloud_course.deploy --app-id YOUR_APP_ID --version-id sdk-v1 --baseline-id sdk-greedy --candidate-id sdk-enumerate --execute
```

実際に成功した場合は `version_id`、`baseline_id`、`candidate_id` を返します。
変更できる条件は各 ID と `apps/assignment/main.py` の計算処理です。
サンプルは既存アプリのコードを push するため、この用途に用意したアプリ ID を指定してください。
既存の版やインスタンスと同じ ID を再使用すると失敗します。
途中まで成功してから失敗することもあるため、ログに出た ID と Console の状態を確認してから続行します。

クラウド用の `requirements.cloud.txt` は Python 3.11 と Linux ARM64 向けに解決した依存関係です。
配備時にマニフェストのメモリ上の指定を切り替えます。
クラウドへのパッケージ送信とランタイム上での起動は未検証です。
この段階は依存取得とビルドの時間も必要です。

## 3. 非同期実行、状態、結果、ログ、キャンセル

対象 API は `new_run`、`run_information`、`run_result_with_polling`、`run_logs`、`cancel_run` です。
最小の確認は送信予定の表示です。

```bash
uv run --locked python -m cloud_course.runs submit
```

実行を開始する操作は `submit` だけです。
実際の送信には配備済みのインスタンス ID を指定します。

```bash
uv run --locked python -m cloud_course.runs submit --app-id YOUR_APP_ID --instance-id sdk-greedy --strategy greedy --execute
```

戻り値の `run_id` は結果の ID で、処理の完了を意味しません。
以後の操作には返された ID を使います。
各コマンドは `--execute` を外せば送信予定だけ確認できます。

```bash
uv run --locked python -m cloud_course.runs status --app-id YOUR_APP_ID --run-id YOUR_RUN_ID --execute
uv run --locked python -m cloud_course.runs results --app-id YOUR_APP_ID --run-id YOUR_RUN_ID --execute
uv run --locked python -m cloud_course.runs logs --app-id YOUR_APP_ID --run-id YOUR_RUN_ID --execute
uv run --locked python -m cloud_course.runs cancel --app-id YOUR_APP_ID --run-id YOUR_RUN_ID --execute
```

`status` は `metadata.status_v2` を含む情報、`results` は `output` を含む結果、`logs` は SDK の `RunLog` の JSON を返す想定です。
`results` は最大60秒を目安に SDK のポーリングを行い、実行が成功していなければ結果を表示して終了コード `1` で終わります。
待機が終わっても実行そのものは継続する場合があります。
同じ ID で `results` を再実行してください。
HTTP 通信1回ごとの時間や再試行もあるため、待機秒数はプロセス全体の厳密な上限ではありません。

`cancel` の出力は要求を受け付けたことを示し、完了状態の保証ではありません。
このアプリは短時間で終わるため、取り消し前に成功することがあります。
キャンセル後も `status` で確認します。
`--strategy` で計算方法を変えられます。
このオプションは実行時に渡すため、インスタンスの既定戦略より優先されます。
`sdk-enumerate` に送る場合も、全列挙を望むなら `--strategy enumerate` を指定します。

よくある失敗は、他のアプリの実行 ID を使うこと、失敗した実行の `output` を成功時と同じ形で読もうとすること、待機のタイムアウトを新規送信でやり直してしまうことです。

## 4. 管理済み入力と入力集合

対象 API は `upload_url`、`upload_data`、`new_managed_input`、`new_input_set`、`Format`、`FormatInput` です。

```bash
uv run --locked python -m cloud_course.inputs
uv run --locked python -m cloud_course.inputs --app-id YOUR_APP_ID --execute
```

1行目は4段階の送信予定を表示します。
2行目を実行した場合は入力をアップロードし、`managed_input_id` と `input_set_id` を返す想定です。
入力自体を再利用するのが管理済み入力、複数の入力をまとめて試験へ渡すのが入力集合です。
次のバッチ編には `managed_input_id` を、受け入れ試験には `input_set_id` を渡します。

`data/assignment.json` を変えると保存する入力が変わります。
スクリプトは毎回新しい入力と集合を作るので、比較に再利用する場合は返された ID を保存してください。
アップロードだけ成功し、その後の登録が失敗する可能性もあります。
取得した ID と Console の状態を確認し、完了した操作をむやみに繰り返さないようにします。
既存の実行を参照する `new_managed_input(run_id=...)` も SDK にありますが、この例は元のファイルをアップロードする流れを示しています。

## 5. バッチ実験

対象 API は `BatchExperimentRun`、`new_batch_experiment`、`batch_experiment_with_polling` です。

```bash
uv run --locked python -m cloud_course.batch
uv run --locked python -m cloud_course.batch --app-id YOUR_APP_ID --input-id YOUR_INPUT_ID --instance-id sdk-greedy --execute
```

送信予定には2件の実行と、`greedy` と `enumerate` のオプション集合が含まれます。
同じ管理済み入力に対して実行条件を変え、費用 `10` と `9` の比較を期待します。
クラウドからは実験状態、実行一覧、集計を含む `BatchExperiment` が返る想定です。

`definition()` 内の `option_sets` と `runs` を変えると比較対象を増やせます。
実行件数も増えるので、送信前の表示で確認してください。
管理済み入力の ID と、入力集合内の入力 ID を混同しないようにします。
この例の `--input-id` は管理済み入力の ID です。

標準エラー出力に `batch_id` が出た後にタイムアウトしたら、追加送信せず続きから取得できます。

```bash
uv run --locked python -m cloud_course.batch --app-id YOUR_APP_ID --batch-id YOUR_BATCH_ID --execute
```

## 6. シナリオ試験

対象 API は `Scenario`、`ScenarioInput`、`ScenarioInputType.NEW`、`ScenarioConfiguration`、`new_scenario_test`、`scenario_test_with_polling` です。

```bash
uv run --locked python -m cloud_course.scenarios
uv run --locked python -m cloud_course.scenarios --app-id YOUR_APP_ID --instance-id sdk-greedy --execute
```

生の入力1件に2つの戦略を組み合わせる定義が表示されます。
繰り返し数は `1` です。
実際には各条件の費用 `10` と `9` を比較する想定です。
入力をコード内で直接渡すので、管理済み入力の章を先に実行する必要はありません。

`configuration` の値のリストや `repetitions` を変えられます。
値の組み合わせと繰り返し数を増やすと実行数が増えます。
`ScenarioInputType.INPUT` を使う場合は管理済み入力の ID のリスト、`INPUT_SET` を使う場合は入力集合の ID が必要です。
指定した種類とデータの形が異なると作成時に失敗します。

```bash
uv run --locked python -m cloud_course.scenarios --app-id YOUR_APP_ID --scenario-id YOUR_SCENARIO_ID --execute
```

この再開用コマンドは新しい試験を作りません。

## 7. 受け入れ試験

対象 API は `Metric`、`MetricParams`、`MetricTolerance`、`new_acceptance_test`、`acceptance_test_with_polling` です。

```bash
uv run --locked python -m cloud_course.acceptance
uv run --locked python -m cloud_course.acceptance --app-id YOUR_APP_ID --input-set-id YOUR_INPUT_SET_ID --baseline-id sdk-greedy --candidate-id sdk-enumerate --execute
```

比較条件は「候補の `value` の平均が基準以下」で、許容差は絶対値 `0` です。
指標定義の `field` は `value` であり、このアプリの `Output.metrics["value"]` に対応します。
サンプルの入力とインスタンス設定では候補 `9`、基準 `10` なので、`results.passed=true` を期待します。
これは計算結果からの予想で、クラウドで実測した結果ではありません。

`--baseline-id` と `--candidate-id` を入れ替えると、同じ判定条件には不合格となる想定です。
許容差は `metrics()` 内の `MetricTolerance` で変更できます。
2つのインスタンスが同じ戦略を使っていないか、両方が `value` を出しているかを確認してください。
試験の完了と条件への合格は別で、このコマンドは不合格でも終了コード `1` を返します。

```bash
uv run --locked python -m cloud_course.acceptance --app-id YOUR_APP_ID --test-id YOUR_TEST_ID --execute
```

この再開用コマンドは既存の試験結果だけを取得します。

## 共通の失敗の読み方

API の例外はサンプル内で隠さず、そのまま終了させます。
認証や権限のエラー、存在しない ID、利用上限、アプリの失敗、待機のタイムアウトを分けて確認してください。
特に作成要求が通信途中で失敗したときは、サーバー側で作成済みの可能性があります。
Console と返された ID を確認してから再送します。
サンプルの Client は HTTP の書き込み操作を自動再試行する対象にしていません。

作成した版、インスタンス、入力、実験はクラウドに残ります。
不要になった資源は ID を確認して Console などから整理してください。
このコースに一括削除処理は含めていません。
外部実行の同期やシャドーテストは [上級機能](../docs/advanced.md) に説明があります。

参照先：[公式資料一覧](../docs/sources.md)。
