import json
from types import SimpleNamespace
from unittest.mock import create_autospec

import nextmv
import pytest
from nextmv import cloud

from cloud_course import acceptance, batch, deploy, inputs, runs, scenarios, support


@pytest.fixture
def app():
    # 実物の署名で検査する。ネットワークを伴うメソッド本体は実行しない。
    return create_autospec(cloud.Application, instance=True, spec_set=True)


@pytest.mark.parametrize(
    "module,args",
    [
        ("auth", []),
        ("deploy", []),
        ("inputs", []),
        ("batch", []),
        ("scenarios", []),
        ("acceptance", []),
        *[("runs", [action]) for action in ["submit", "status", "results", "logs", "cancel"]],
    ],
)
def test_previews_without_credentials_or_network(run_cli, module, args):
    result = run_cli("-m", f"cloud_course.{module}", *args)
    output = json.loads(result.stdout)
    assert output["mode"] == "preview"
    assert output["network"] is False


def test_no_client_created_in_preview(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Client は作らない")

    monkeypatch.setattr(cloud, "Client", forbidden)
    monkeypatch.setattr("sys.argv", ["auth"])
    from cloud_course import auth

    auth.main()


def test_placeholder_app_rejected_before_auth():
    with pytest.raises(ValueError, match="実在する"):
        support.connect("YOUR_APP_ID")


def test_deploy_signature_and_instance_configuration(app):
    app.new_version.return_value = SimpleNamespace(id="sdk-v1")
    app.new_instance.return_value = SimpleNamespace(id="instance")
    result = deploy.deploy(app, "sdk-v1", "baseline", "candidate")
    assert result["version_id"] == "sdk-v1"
    assert app.push.call_args.kwargs["manifest"].python.pip_requirements == "requirements.cloud.txt"
    assert app.new_instance.call_count == 2
    assert [call.kwargs["configuration"].options for call in app.new_instance.call_args_list] == [
        {"strategy": "greedy"},
        {"strategy": "enumerate"},
    ]


def test_async_submit_and_other_run_operations(app):
    app.new_run.return_value = "run-1"
    assert runs.operate(app, "submit", "baseline", "", "greedy") == {"run_id": "run-1"}
    app.new_run.assert_called_once()
    assert app.new_run.call_args.kwargs["instance_id"] == "baseline"
    for action, method in [
        ("status", "run_information"),
        ("results", "run_result_with_polling"),
        ("logs", "run_logs"),
    ]:
        getattr(app, method).return_value.to_dict.return_value = {"id": "run-1"}
        assert runs.operate(app, action, "", "run-1", "greedy") == {"id": "run-1"}
    assert runs.operate(app, "cancel", "", "run-1", "greedy")["cancellation_requested"]
    app.cancel_run.assert_called_once_with(run_id="run-1")
    assert app.new_run.call_count == 1


def test_input_upload_and_set_creation(app):
    app.upload_url.return_value = SimpleNamespace(upload_id="upload-1")
    managed = cloud.ManagedInput(id="input-1")
    app.new_managed_input.return_value = managed
    app.new_input_set.return_value = SimpleNamespace(id="set-1")
    assert inputs.create_inputs(app) == {"managed_input_id": "input-1", "input_set_id": "set-1"}
    assert app.new_managed_input.call_args.kwargs["format"].format_input.input_type == "json"
    app.new_input_set.assert_called_once_with(name="SDK assignment inputs", inputs=[managed])


def test_batch_models_and_resume_without_resubmit(app):
    spec = batch.definition("input-1", "instance-1")
    assert len(spec["runs"]) == 2
    assert {run.option_set for run in spec["runs"]} == set(spec["option_sets"])
    app.new_batch_experiment.return_value = "batch-1"
    batch.run_batch(app, spec)
    batch.run_batch(app, spec, "batch-1")
    assert app.new_batch_experiment.call_count == 1
    assert app.batch_experiment_with_polling.call_count == 2


def test_scenario_models_and_resume_without_resubmit(app):
    spec = scenarios.definition("instance-1")
    assert spec[0].scenario_input.scenario_input_type == cloud.ScenarioInputType.NEW
    assert spec[0].configuration[0].values == ["greedy", "enumerate"]
    app.new_scenario_test.return_value = "scenario-1"
    scenarios.run_scenarios(app, spec)
    scenarios.run_scenarios(app, spec, "scenario-1")
    assert app.new_scenario_test.call_count == 1
    assert app.new_scenario_test.call_args.kwargs["repetitions"] == 1


def test_acceptance_metric_and_resume_without_resubmit(app):
    metric = acceptance.metrics()[0]
    assert metric.to_dict() == {
        "field": "value",
        "metric_type": "direct-comparison",
        "statistic": "mean",
        "params": {"operator": "le", "tolerance": {"type": "absolute", "value": 0.0}},
    }
    app.new_acceptance_test.return_value = SimpleNamespace(id="test-1")
    acceptance.run_acceptance(app, "baseline", "candidate", "set-1")
    acceptance.run_acceptance(app, "baseline", "candidate", "set-1", "test-1")
    assert app.new_acceptance_test.call_count == 1


def test_manifest_matches_installed_sdk():
    manifest = nextmv.Manifest.from_yaml(str(support.ROOT / "apps/assignment"))
    assert manifest.configuration.content.format == nextmv.ContentFormat.JSON
    assert {option.name for option in manifest.configuration.options.items} == {
        "strategy",
        "cost_scale",
        "details",
    }
    assert not hasattr(nextmv, "Model")
