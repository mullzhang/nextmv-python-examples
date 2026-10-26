"""ローカル編とクラウド編で共用する、小さい割り当てアプリ。"""

import itertools

import nextmv


def solve(data: nextmv.Input) -> nextmv.Output:
    workers, tasks, costs = data.data["workers"], data.data["tasks"], data.data["costs"]
    n = len(tasks)
    if not 1 <= n <= 8 or len(workers) != n:
        raise ValueError("この小例では作業と担当者を同数の1〜8件にしてください")
    if len(costs) != n or any(len(row) != n for row in costs):
        raise ValueError("costs は担当者 × 作業の正方行列にしてください")
    if data.options.cost_scale <= 0:
        raise ValueError("cost_scale は正の値にしてください")

    if data.options.strategy == "greedy":
        remaining = list(range(n))
        chosen = []
        for t in range(n):
            w = min(remaining, key=lambda w: costs[w][t])
            remaining.remove(w)
            chosen.append(w)
    elif data.options.strategy == "enumerate":
        chosen = min(
            itertools.permutations(range(n)),
            key=lambda order: sum(costs[w][t] for t, w in enumerate(order)),
        )
    else:
        raise ValueError("strategy は greedy または enumerate にしてください")

    assignments = [
        {"worker": workers[w], "task": tasks[t], "cost": costs[w][t] * data.options.cost_scale}
        for t, w in enumerate(chosen)
    ]
    if data.options.details:
        nextmv.log(f"strategy={data.options.strategy}, assigned={n}")
    return nextmv.Output(
        options=data.options,
        solution={"assignments": assignments},
        metrics={"value": sum(row["cost"] for row in assignments), "assigned_count": n},
    )


def main():
    # app.yaml の options 定義を読み取る。
    nextmv.write(solve(nextmv.load()))


if __name__ == "__main__":
    main()
