"""全検証をネットワークなしで実行し、結果を artifacts/verification.json に保存する。"""

import json
import os
import platform
import subprocess
import sys
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    env = {key: os.environ[key] for key in ["PATH", "TMPDIR"] if key in os.environ}
    env.update(
        UV_OFFLINE="1",
        UV_CACHE_DIR=str(ROOT / ".uv-cache"),
        PYTHONPATH=str(ROOT / "tests/offline_guard") + os.pathsep + str(ROOT),
    )
    commands = [
        [sys.executable, "-m", "ruff", "check", "."],
        [sys.executable, "-m", "ruff", "format", "--check", "."],
        [sys.executable, "-m", "pytest", "-q"],
    ]
    results = []
    for command in commands:
        print("Running:", " ".join(command), flush=True)
        result = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        results.append(
            {
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
    report = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "python": platform.python_version(),
        "packages": {name: version(name) for name in ["nextmv", "ortools", "pytest", "ruff"]},
        "cloud_executed": False,
        "checks": results,
    }
    target = ROOT / "artifacts/verification.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return 1 if any(result["exit_code"] for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
