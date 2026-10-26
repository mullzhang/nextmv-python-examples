"""同じ入力に対して戦略と費用倍率を変えて比較する。"""

import hashlib
import itertools
import platform
from importlib.metadata import version

import nextmv
from nextmv import local

from examples.local.support import APP_DIR, INPUT_PATH, ROOT, load_input, local_environment


def main():
    rows = []
    with local_environment():
        app = local.Application(src=str(APP_DIR))
        for strategy, scale in itertools.product(["greedy", "enumerate"], [1, 2]):
            result = app.new_run_with_result(
                input=load_input(),
                run_options={"strategy": strategy, "cost_scale": str(scale)},
                polling_options=nextmv.PollingOptions(max_duration=60, max_tries=120),
            )
            if result.metadata.status_v2 != nextmv.StatusV2.succeeded:
                raise RuntimeError(f"{result.id}: {app.run_logs(result.id)}")
            rows.append(
                {
                    "run_id": result.id,
                    "strategy": strategy,
                    "scale": scale,
                    "value": result.output["metrics"]["value"],
                }
            )
    # 履歴はコードの版を自動固定しないので、再現に必要な情報を併記する。
    hashes = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [INPUT_PATH, APP_DIR / "main.py", APP_DIR / "app.yaml", ROOT / "uv.lock"]
    }
    nextmv.write(
        {
            "runs": rows,
            "sha256": hashes,
            "sdk_version": version("nextmv"),
            "python_version": platform.python_version(),
        }
    )


if __name__ == "__main__":
    main()
