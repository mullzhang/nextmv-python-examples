"""非同期の実行開始、状態、結果、ログ、キャンセルを個別に操作する。"""

import nextmv

from cloud_course.support import (
    connect,
    load_input,
    parser_for,
    polling_options,
    preview,
    require_ids,
)


def operate(app, action, instance_id, run_id, strategy):
    if action == "submit":
        new_id = app.new_run(
            input=load_input(), instance_id=instance_id, options={"strategy": strategy}
        )
        return {"run_id": new_id}
    if action == "status":
        return app.run_information(run_id=run_id).to_dict()
    if action == "results":
        result = app.run_result_with_polling(run_id=run_id, polling_options=polling_options())
        return result.to_dict()
    if action == "logs":
        return app.run_logs(run_id=run_id).to_dict()
    if action == "cancel":
        app.cancel_run(run_id=run_id)
        return {"run_id": run_id, "cancellation_requested": True}
    raise ValueError(f"未対応の操作: {action}")


def main():
    parser = parser_for(__doc__)
    parser.add_argument("action", choices=["submit", "status", "results", "logs", "cancel"])
    parser.add_argument("--instance-id", default="YOUR_INSTANCE_ID")
    parser.add_argument("--run-id", default="YOUR_RUN_ID")
    parser.add_argument("--strategy", choices=["greedy", "enumerate"], default="greedy")
    args = parser.parse_args()
    if not args.execute:
        preview(
            args.app_id,
            [
                {
                    "action": args.action,
                    "instance_id": args.instance_id,
                    "run_id": args.run_id,
                    "strategy": args.strategy,
                }
            ],
        )
        return
    if args.action == "submit":
        require_ids(instance_id=args.instance_id)
    else:
        require_ids(run_id=args.run_id)
    result = operate(
        connect(args.app_id), args.action, args.instance_id, args.run_id, args.strategy
    )
    nextmv.write(result)
    if args.action == "results" and result["metadata"]["status_v2"] != "succeeded":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
