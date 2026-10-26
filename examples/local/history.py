"""保存された実行を読み、入力と条件を再利用する。"""

import argparse

import nextmv
from nextmv import local

from examples.local.support import APP_DIR, local_environment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", help="詳細を読む実行 ID。省略時は履歴一覧")
    parser.add_argument("--replay", action="store_true", help="指定実行の入力と options で再実行")
    args = parser.parse_args()
    if args.replay and not args.run_id:
        parser.error("--replay には --run-id が必要です")
    with local_environment():
        app = local.Application(src=str(APP_DIR))
        if not args.run_id:
            nextmv.write({"runs": [run.to_dict() for run in app.list_runs()]})
            return 0
        original = app.run_result(args.run_id)
        information = app.run_information(args.run_id)
        saved_input = app.run_input(args.run_id)
        if not args.replay:
            nextmv.write(
                {
                    "information": information.to_dict(),
                    "input": saved_input,
                    "output": original.output,
                    "logs": app.run_logs(args.run_id),
                }
            )
            return 0
        if information.metadata.status_v2 != nextmv.StatusV2.succeeded:
            raise ValueError("この例は成功した実行の再現を扱います")
        # 実行後の options には既定値も含まれる。bool は SDK に渡す前に小文字にする。
        options = {
            key: str(value).lower() if isinstance(value, bool) else str(value)
            for key, value in original.output["options"].items()
        }
        replay = app.new_run_with_result(
            input=saved_input,
            run_options=options,
            polling_options=nextmv.PollingOptions(max_duration=60, max_tries=120),
        )
        succeeded = replay.metadata.status_v2 == nextmv.StatusV2.succeeded
        nextmv.write(
            {
                "original_run_id": args.run_id,
                "replay_run_id": replay.id,
                "status": replay.metadata.status_v2,
                "same_solution": succeeded
                and original.output["solution"] == replay.output["solution"],
            }
        )
        return 0 if succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
