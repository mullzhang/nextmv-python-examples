"""生の入力とオプションの組み合わせからシナリオ試験を作る。"""

import nextmv
from nextmv import cloud

from cloud_course.support import (
    connect,
    load_input,
    parser_for,
    polling_options,
    preview,
    require_ids,
)


def definition(instance_id):
    return [
        cloud.Scenario(
            scenario_id="strategies",
            instance_id=instance_id,
            scenario_input=cloud.ScenarioInput(
                scenario_input_type=cloud.ScenarioInputType.NEW,
                scenario_input_data=[load_input()],
            ),
            configuration=[
                cloud.ScenarioConfiguration(name="strategy", values=["greedy", "enumerate"])
            ],
        )
    ]


def run_scenarios(app, scenarios, scenario_id=None):
    if scenario_id is None:
        scenario_id = app.new_scenario_test(
            scenarios=scenarios, repetitions=1, name="SDK strategy scenarios"
        )
    nextmv.log(f"scenario_test_id={scenario_id}")
    return app.scenario_test_with_polling(
        scenario_test_id=scenario_id, polling_options=polling_options()
    )


def main():
    parser = parser_for(__doc__)
    parser.add_argument("--instance-id", default="YOUR_INSTANCE_ID")
    parser.add_argument("--scenario-id", help="既存の試験を待つ。新規実行は作らない")
    args = parser.parse_args()
    scenarios = definition(args.instance_id)
    if not args.execute:
        preview(
            args.app_id,
            [
                {
                    "api": "Application.new_scenario_test",
                    "repetitions": 1,
                    "scenarios": [item.to_dict() for item in scenarios],
                    "resume_id": args.scenario_id,
                }
            ],
        )
        return
    require_ids(
        **(
            {"scenario_id": args.scenario_id}
            if args.scenario_id
            else {"instance_id": args.instance_id}
        )
    )
    nextmv.write(run_scenarios(connect(args.app_id), scenarios, args.scenario_id))


if __name__ == "__main__":
    main()
