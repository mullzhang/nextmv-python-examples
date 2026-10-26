import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("ネットワーク接続を伴うテストは許可していません")

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket.socket, "connect_ex", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(requests.Session, "request", denied)


@pytest.fixture
def assignment():
    return json.loads((ROOT / "data/assignment.json").read_text())


@pytest.fixture
def run_cli():
    def run(*args, data=None, env=None, cwd=ROOT, expected=0):
        # 認証関連の環境変数を子プロセスに引き継がない。
        process_env = {key: os.environ[key] for key in ["PATH", "TMPDIR"] if key in os.environ}
        process_env.update(
            UV_OFFLINE="1",
            UV_CACHE_DIR=str(ROOT / ".uv-cache"),
            PYTHONPATH=str(ROOT / "tests/offline_guard") + os.pathsep + str(ROOT),
        )
        if env:
            process_env.update(env)
        process = subprocess.run(
            [sys.executable, *args],
            input=json.dumps(data) if isinstance(data, dict) else data,
            text=True,
            capture_output=True,
            timeout=120,
            cwd=cwd,
            env=process_env,
        )
        if expected is not None:
            assert process.returncode == expected, process.stdout + process.stderr
        return process

    return run
