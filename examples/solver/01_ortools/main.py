"""Nextmv の入出力と OR-Tools CP-SAT の割り当てモデルを接続する。"""

import nextmv
from ortools.sat.python import cp_model


def solve(data: nextmv.Input) -> nextmv.Output:
    workers, tasks, costs = data.data["workers"], data.data["tasks"], data.data["costs"]
    if not workers or not tasks:
        raise ValueError("workers と tasks は空にできません")
    if len(costs) != len(workers) or any(len(row) != len(tasks) for row in costs):
        raise ValueError("costs は workers × tasks の行列にしてください")
    if any(type(value) is not int or value < 0 for row in costs for value in row):
        raise ValueError("CP-SAT の費用は非負の整数にしてください")
    if data.options.duration <= 0:
        raise ValueError("duration は正の秒数にしてください")

    model = cp_model.CpModel()
    x = {
        (w, t): model.new_bool_var(f"assign_{w}_{t}")
        for w in range(len(workers))
        for t in range(len(tasks))
    }
    for t in range(len(tasks)):
        model.add_exactly_one(x[w, t] for w in range(len(workers)))
    for w in range(len(workers)):
        model.add_at_most_one(x[w, t] for t in range(len(tasks)))
    model.minimize(sum(costs[w][t] * variable for (w, t), variable in x.items()))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = data.options.duration
    solver.parameters.random_seed = data.options.seed
    solver.parameters.num_search_workers = 1
    status = solver.solve(model)
    status_name = solver.status_name(status)
    nextmv.log(f"CP-SAT: {status_name}")
    metrics = {"status": status_name, "duration": solver.wall_time, "assigned_count": 0}
    assignments = []
    # INFEASIBLE や UNKNOWN で value() を読むと、存在しない解を扱ってしまう。
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        assignments = [
            {"worker": workers[w], "task": tasks[t], "cost": costs[w][t]}
            for (w, t), variable in x.items()
            if solver.value(variable)
        ]
        metrics.update(value=solver.objective_value, assigned_count=len(assignments))
    return nextmv.Output(
        options=data.options, solution={"assignments": assignments}, metrics=metrics
    )


def main():
    options = nextmv.Options(
        nextmv.Option("duration", float, default=5.0, description="探索時間の上限秒数"),
        nextmv.Option("seed", int, default=0, description="乱数シード"),
    )
    data = nextmv.load(options=options)
    nextmv.write(solve(data))


if __name__ == "__main__":
    main()
