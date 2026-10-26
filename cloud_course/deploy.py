"""アプリを push し、版と比較用の2つのインスタンスを作る。"""

import nextmv
from nextmv import cloud

from cloud_course.support import ROOT, connect, parser_for, preview, require_ids


def deploy(app, version_id, baseline_id, candidate_id):
    app_dir = ROOT / "apps" / "assignment"
    manifest = nextmv.Manifest.from_yaml(str(app_dir))
    # クラウドの Python 3.11 用に解決した依存関係を使用する。
    manifest.python.pip_requirements = "requirements.cloud.txt"
    app.push(app_dir=str(app_dir), manifest=manifest, verbose=True)
    version = app.new_version(id=version_id, description="SDK feature examples")
    nextmv.log(f"version_id={version.id}")
    for instance_id, strategy in [(baseline_id, "greedy"), (candidate_id, "enumerate")]:
        instance = app.new_instance(
            version_id=version.id,
            id=instance_id,
            configuration=cloud.InstanceConfiguration(options={"strategy": strategy}),
        )
        nextmv.log(f"instance_id={instance.id}")
    return {"version_id": version.id, "baseline_id": baseline_id, "candidate_id": candidate_id}


def main():
    parser = parser_for(__doc__)
    parser.add_argument("--version-id", default="sdk-v1")
    parser.add_argument("--baseline-id", default="sdk-greedy")
    parser.add_argument("--candidate-id", default="sdk-enumerate")
    args = parser.parse_args()
    if not args.execute:
        preview(
            args.app_id,
            [
                {"api": "Application.push", "source": "apps/assignment"},
                {"api": "Application.new_version", "id": args.version_id},
                {"api": "Application.new_instance", "id": args.baseline_id, "strategy": "greedy"},
                {
                    "api": "Application.new_instance",
                    "id": args.candidate_id,
                    "strategy": "enumerate",
                },
            ],
        )
        return
    require_ids(
        version_id=args.version_id, baseline_id=args.baseline_id, candidate_id=args.candidate_id
    )
    if args.baseline_id == args.candidate_id:
        parser.error("2つのインスタンスには異なる ID を指定してください")
    nextmv.write(deploy(connect(args.app_id), args.version_id, args.baseline_id, args.candidate_id))


if __name__ == "__main__":
    main()
