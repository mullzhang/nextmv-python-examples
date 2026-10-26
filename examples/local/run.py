"""app.yaml を持つアプリを実行し、完了までポーリングする。"""

import nextmv
from nextmv import local

from examples.local.support import APP_DIR, load_input, local_environment


def main():
    with local_environment():
        app = local.Application(src=str(APP_DIR))
        run_id = app.new_run(input=load_input(), options={"strategy": "greedy"})
        nextmv.log(f"run_id={run_id}")
        result = app.run_result_with_polling(
            run_id, polling_options=nextmv.PollingOptions(max_duration=60, max_tries=120)
        )
        nextmv.log(app.run_logs(run_id))
        nextmv.write(result)
        return 0 if result.metadata.status_v2 == nextmv.StatusV2.succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
