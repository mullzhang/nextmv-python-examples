import json

import nextmv
from nextmv import local

from examples.local.support import APP_DIR, local_environment


def test_run_history_detail_replay_and_sweep(run_cli):
    result = json.loads(run_cli("-m", "examples.local.run").stdout)
    run_id = result["id"]
    assert result["metadata"]["status_v2"] == "succeeded"
    assert result["output"]["metrics"]["value"] == 10
    history = json.loads(run_cli("-m", "examples.local.history").stdout)
    assert run_id in {run["id"] for run in history["runs"]}
    detail = json.loads(run_cli("-m", "examples.local.history", "--run-id", run_id).stdout)
    assert detail["input"]["tasks"] == ["pack", "ship", "check"]
    assert "strategy=greedy" in detail["logs"]
    replay = json.loads(
        run_cli("-m", "examples.local.history", "--run-id", run_id, "--replay").stdout
    )
    assert replay["same_solution"] is True
    assert replay["replay_run_id"] != run_id
    sweep = json.loads(run_cli("-m", "examples.local.sweep").stdout)
    assert [(run["strategy"], run["scale"], run["value"]) for run in sweep["runs"]] == [
        ("greedy", 1, 10),
        ("greedy", 2, 20),
        ("enumerate", 1, 9),
        ("enumerate", 2, 18),
    ]
    assert all(len(value) == 64 for value in sweep["sha256"].values())


def test_local_failure_has_status_and_logs(assignment):
    with local_environment():
        app = local.Application(src=str(APP_DIR))
        result = app.new_run_with_result(
            input=assignment,
            run_options={"strategy": "invalid"},
            polling_options=nextmv.PollingOptions(max_duration=60, max_tries=120),
        )
        assert result.metadata.status_v2 == nextmv.StatusV2.failed
        assert "strategy" in app.run_logs(result.id)


def test_history_replay_requires_id(run_cli):
    result = run_cli("-m", "examples.local.history", "--replay", expected=2)
    assert "--run-id" in result.stderr
