import csv
import itertools
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CORE = "examples/core"


def test_json_stdin_file_and_stdout_file(run_cli, assignment, tmp_path):
    stdin = run_cli(f"{CORE}/01_json_io/main.py", data=assignment)
    from_file = run_cli(f"{CORE}/01_json_io/main.py", "--input", "data/assignment.json")
    destination = tmp_path / "out.json"
    to_file = run_cli(f"{CORE}/01_json_io/main.py", "--output", str(destination), data=assignment)
    assert (
        json.loads(stdin.stdout)
        == json.loads(from_file.stdout)
        == json.loads(destination.read_text())
    )
    assert json.loads(stdin.stdout)["metrics"] == {"worker_count": 3, "task_count": 3}
    assert to_file.stdout == ""


def test_invalid_json(run_cli):
    result = run_cli(f"{CORE}/01_json_io/main.py", data="{", expected=None)
    assert result.returncode != 0
    assert "JSONDecodeError" in result.stderr
    assert not result.stdout


def test_options_defaults(run_cli):
    result = run_cli(f"{CORE}/02_options/main.py", "--label", "first")
    assert json.loads(result.stdout)["options"] == {
        "label": "first",
        "limit": 3,
        "cost_scale": 1.0,
        "details": False,
    }


def test_options_env_and_cli_priority(run_cli):
    result = run_cli(
        f"{CORE}/02_options/main.py",
        "--limit",
        "2",
        "--details",
        "false",
        env={"LABEL": "environment", "LIMIT": "8", "COST_SCALE": "1.5", "DETAILS": "true"},
    )
    assert json.loads(result.stdout)["options"] == {
        "label": "environment",
        "limit": 2,
        "cost_scale": 1.5,
        "details": False,
    }
    assert not result.stderr


def test_sdk_unknown_boolean_string_is_false(run_cli):
    result = run_cli(f"{CORE}/02_options/main.py", "--label", "test", "--details", "maybe")
    assert json.loads(result.stdout)["options"]["details"] is False


@pytest.mark.parametrize(
    "args, fragment",
    [
        ([], "required"),
        (["--label", "test", "--limit", "x"], "invalid int value"),
        (["--label", "test", "--cost_scale", "0"], "正の値"),
    ],
)
def test_options_failures(run_cli, args, fragment):
    result = run_cli(f"{CORE}/02_options/main.py", *args, expected=None)
    assert result.returncode != 0
    assert fragment in result.stderr


def test_solution_metrics_and_logs_are_separate(run_cli):
    result = run_cli(f"{CORE}/03_outputs_errors/main.py")
    output = json.loads(result.stdout)
    assert output["metrics"]["value"] == 9
    assert "statistics" not in output
    assert "検証を開始" in result.stderr
    assert "検証を開始" not in result.stdout


def test_explicit_failure_has_no_solution(run_cli):
    result = run_cli(f"{CORE}/03_outputs_errors/main.py", "--fail", "true", expected=2)
    assert not result.stdout
    assert "入力エラー" in result.stderr


def test_multifile_csv_json(run_cli, tmp_path):
    result = run_cli(f"{CORE}/04_multi_file/main.py", "--output-dir", str(tmp_path))
    assert not result.stdout
    with (tmp_path / "solutions/assignments.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3
    assert sum(float(row["cost"]) for row in rows) == 9
    assert json.loads((tmp_path / "solutions/summary.json").read_text())["total_cost"] == 9
    assert json.loads((tmp_path / "metrics.json").read_text())["metrics"]["value"] == 9


def test_multifile_missing_input(run_cli, tmp_path):
    result = run_cli(f"{CORE}/04_multi_file/main.py", "--input-dir", str(tmp_path), expected=None)
    assert result.returncode != 0
    assert "costs.csv" in result.stderr


def test_model_structure(run_cli, assignment):
    output = json.loads(run_cli(f"{CORE}/05_model/main.py", data=assignment).stdout)
    assert output["metrics"]["value"] == 14
    assert len(output["solution"]["assignments"]) == 3


def test_ortools_matches_exhaustive_optimum(run_cli, assignment):
    output = json.loads(run_cli("examples/solver/01_ortools/main.py", data=assignment).stdout)
    optimum = min(
        sum(assignment["costs"][w][t] for t, w in enumerate(order))
        for order in itertools.permutations(range(3))
    )
    assert output["metrics"]["status"] == "OPTIMAL"
    assert output["metrics"]["value"] == optimum == 9
    rows = output["solution"]["assignments"]
    assert len({row["worker"] for row in rows}) == len({row["task"] for row in rows}) == 3
    assert sum(row["cost"] for row in rows) == optimum


def test_ortools_infeasible_is_not_a_process_error(run_cli):
    data = {"workers": ["aki"], "tasks": ["pack", "ship"], "costs": [[1, 2]]}
    output = json.loads(run_cli("examples/solver/01_ortools/main.py", data=data).stdout)
    assert output["metrics"]["status"] == "INFEASIBLE"
    assert "value" not in output["metrics"]
    assert output["solution"]["assignments"] == []


@pytest.mark.parametrize("costs", [[[1]], [[1.5, 2, 3]] * 3])
def test_ortools_rejects_bad_costs(run_cli, assignment, costs):
    assignment["costs"] = costs
    result = run_cli("examples/solver/01_ortools/main.py", data=assignment, expected=None)
    assert result.returncode != 0
    assert "ValueError" in result.stderr


@pytest.mark.parametrize("strategy,value", [("greedy", 10), ("enumerate", 9)])
def test_manifest_options_in_app(run_cli, assignment, strategy, value):
    result = run_cli(
        "main.py", "--strategy", strategy, data=assignment, cwd=ROOT / "apps/assignment"
    )
    output = json.loads(result.stdout)
    assert output["metrics"]["value"] == value
    assert output["options"]["details"] is True
