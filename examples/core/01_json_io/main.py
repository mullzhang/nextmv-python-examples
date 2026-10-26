"""JSON をファイルまたは標準入力から読み、標準出力またはファイルへ返す。"""

import argparse

import nextmv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="省略すると stdin")
    parser.add_argument("--output", help="省略すると stdout")
    args = parser.parse_args()
    data = nextmv.load(input_format=nextmv.ContentFormat.JSON, path=args.input)
    output = nextmv.Output(
        solution={"workers": data.data["workers"], "tasks": data.data["tasks"]},
        metrics={"worker_count": len(data.data["workers"]), "task_count": len(data.data["tasks"])},
    )
    nextmv.write(output, path=args.output)


if __name__ == "__main__":
    main()
