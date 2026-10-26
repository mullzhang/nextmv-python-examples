"""CSV と JSON を同時に読み、解を複数ファイルに出す。"""

import argparse

import nextmv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default="examples/core/04_multi_file/inputs")
    parser.add_argument("--output-dir", default="artifacts/multi-file")
    args = parser.parse_args()
    data = nextmv.load(
        input_format=nextmv.ContentFormat.MULTI_FILE,
        path=args.input_dir,
        data_files=[
            nextmv.csv_data_file("costs.csv", input_data_key="costs"),
            nextmv.json_data_file("settings.json", input_data_key="settings"),
        ],
    )
    # CSV のセルは文字列。数値への変換はアプリ側で行う。
    scale = data.data["settings"]["cost_scale"]
    rows = [dict(row, cost=float(row["cost"]) * scale) for row in data.data["costs"]]
    total = sum(row["cost"] for row in rows)
    output = nextmv.Output(
        output_format=nextmv.ContentFormat.MULTI_FILE,
        solution_files=[
            nextmv.csv_solution_file("assignments.csv", rows),
            nextmv.json_solution_file("summary.json", {"total_cost": total}),
        ],
        metrics={"value": total, "assigned_count": len(rows)},
    )
    nextmv.write(output, path=args.output_dir)
    nextmv.log(f"出力先: {args.output_dir}")


if __name__ == "__main__":
    main()
