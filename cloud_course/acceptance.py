"""候補インスタンスの平均費用が基準以下か受け入れ試験で比較する。"""

import nextmv
from nextmv import cloud

from cloud_course.support import connect, parser_for, polling_options, preview, require_ids


def metrics():
    return [
        cloud.Metric(
            field="value",
            metric_type=cloud.MetricType.direct_comparison,
            statistic=cloud.StatisticType.mean,
            params=cloud.MetricParams(
                operator=cloud.Comparison.less_than_or_equal_to,
                tolerance=cloud.MetricTolerance(type=cloud.MetricToleranceType.absolute, value=0.0),
            ),
        )
    ]


def run_acceptance(app, baseline_id, candidate_id, input_set_id, test_id=None):
    if test_id is None:
        test = app.new_acceptance_test(
            baseline_instance_id=baseline_id,
            candidate_instance_id=candidate_id,
            input_set_id=input_set_id,
            metrics=metrics(),
            name="SDK cost must not increase",
        )
        test_id = test.id
    nextmv.log(f"acceptance_test_id={test_id}")
    return app.acceptance_test_with_polling(
        acceptance_test_id=test_id, polling_options=polling_options()
    )


def main():
    parser = parser_for(__doc__)
    parser.add_argument("--baseline-id", default="sdk-greedy")
    parser.add_argument("--candidate-id", default="sdk-enumerate")
    parser.add_argument("--input-set-id", default="YOUR_INPUT_SET_ID")
    parser.add_argument("--test-id", help="既存の試験を待つ。新規実行は作らない")
    args = parser.parse_args()
    if not args.execute:
        preview(
            args.app_id,
            [
                {
                    "api": "Application.new_acceptance_test",
                    "baseline_id": args.baseline_id,
                    "candidate_id": args.candidate_id,
                    "input_set_id": args.input_set_id,
                    "metrics": [metric.to_dict() for metric in metrics()],
                    "resume_id": args.test_id,
                }
            ],
        )
        return
    if args.test_id:
        require_ids(test_id=args.test_id)
    else:
        require_ids(
            baseline_id=args.baseline_id,
            candidate_id=args.candidate_id,
            input_set_id=args.input_set_id,
        )
    result = run_acceptance(
        connect(args.app_id), args.baseline_id, args.candidate_id, args.input_set_id, args.test_id
    )
    nextmv.write(result)
    # 試験が完了したことと、比較条件に合格したことを区別する。
    if result.results is None or not result.results.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
