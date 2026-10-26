"""解と指標を stdout に、診断を stderr に分ける。"""

import nextmv


def main():
    options = nextmv.Options(
        nextmv.Option("fail", bool, default=False, description="失敗例を実行するか")
    )
    options.parse()
    nextmv.log("入力の検証を開始しました")
    if options.fail:
        nextmv.log("入力エラー: 作業一覧が空です")
        # この終了コードは Python プロセスのもの。最適化の INFEASIBLE とは別。
        return 2
    output = nextmv.Output(
        options=options,
        solution={"assignments": [{"worker": "aki", "task": "pack", "cost": 9}]},
        metrics={"value": 9, "assigned_count": 1, "status": "feasible"},
    )
    nextmv.log("割り当てを1件作成しました")
    nextmv.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
