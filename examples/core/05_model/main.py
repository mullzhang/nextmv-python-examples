"""通常の Python クラスで Input → solve → Output を分ける。"""

import nextmv


class AssignmentModel:
    """SDK 1.12.0 に nextmv.Model はないため、SDK の基底クラスは継承しない。"""

    def solve(self, data: nextmv.Input) -> nextmv.Output:
        workers, tasks, costs = data.data["workers"], data.data["tasks"], data.data["costs"]
        # この例は順番どおりの割り当て。最小費用の探索は solver 編で扱う。
        assignments = [
            {"worker": worker, "task": task, "cost": costs[i][i]}
            for i, (worker, task) in enumerate(zip(workers, tasks, strict=True))
        ]
        return nextmv.Output(
            solution={"assignments": assignments},
            metrics={"value": sum(row["cost"] for row in assignments)},
        )


def main():
    data = nextmv.load()
    result = AssignmentModel().solve(data)
    nextmv.write(result)


if __name__ == "__main__":
    main()
