"""型、既定値、必須値、環境変数、コマンドラインの優先順位。"""

import nextmv


def main():
    options = nextmv.Options(
        nextmv.Option("label", str, required=True, description="実験の識別名"),
        nextmv.Option("limit", int, default=3, description="対象にする作業数"),
        nextmv.Option("cost_scale", float, default=1.0, description="費用の倍率"),
        nextmv.Option("details", bool, default=False, description="ログを出すか"),
    )
    options.parse()
    if options.limit < 1 or options.cost_scale <= 0:
        raise ValueError("limit と cost_scale は正の値にしてください")
    if options.details:
        nextmv.log(f"label={options.label}, limit={options.limit}")
    nextmv.write(nextmv.Output(options=options, solution={"label": options.label}))


if __name__ == "__main__":
    main()
