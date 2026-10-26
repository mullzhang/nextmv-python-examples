"""同じ管理済み入力を2つのオプション集合で実行する。"""

import nextmv
from nextmv import cloud

from cloud_course.support import connect, parser_for, polling_options, preview, require_ids


def definition(input_id, instance_id):
    return {
        "runs": [
            cloud.BatchExperimentRun(
                input_id=input_id, instance_id=instance_id, option_set=strategy
            )
            for strategy in ["greedy", "enumerate"]
        ],
        "option_sets": {strategy: {"strategy": strategy} for strategy in ["greedy", "enumerate"]},
    }


def run_batch(app, spec, batch_id=None):
    if batch_id is None:
        batch_id = app.new_batch_experiment(name="SDK strategy comparison", **spec)
    # 待機がタイムアウトしても、ここで出た ID から再開できる。
    nextmv.log(f"batch_id={batch_id}")
    return app.batch_experiment_with_polling(batch_id=batch_id, polling_options=polling_options())


def main():
    parser = parser_for(__doc__)
    parser.add_argument("--input-id", default="YOUR_INPUT_ID")
    parser.add_argument("--instance-id", default="YOUR_INSTANCE_ID")
    parser.add_argument("--batch-id", help="既存の実験を待つ。新規実行は作らない")
    args = parser.parse_args()
    spec = definition(args.input_id, args.instance_id)
    if not args.execute:
        preview(
            args.app_id,
            [
                {
                    "api": "Application.new_batch_experiment",
                    "runs": [run.to_dict() for run in spec["runs"]],
                    "option_sets": spec["option_sets"],
                    "resume_id": args.batch_id,
                }
            ],
        )
        return
    if args.batch_id:
        require_ids(batch_id=args.batch_id)
    else:
        require_ids(input_id=args.input_id, instance_id=args.instance_id)
    nextmv.write(run_batch(connect(args.app_id), spec, args.batch_id))


if __name__ == "__main__":
    main()
