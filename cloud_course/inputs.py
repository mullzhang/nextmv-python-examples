"""入力をアップロードし、managed input と input set を作る。"""

import nextmv

from cloud_course.support import connect, load_input, parser_for, preview


def create_inputs(app):
    upload = app.upload_url()
    app.upload_data(upload_url=upload, data=load_input())
    managed = app.new_managed_input(
        name="SDK assignment input",
        upload_id=upload.upload_id,
        format=nextmv.Format(format_input=nextmv.FormatInput(input_type=nextmv.ContentFormat.JSON)),
    )
    nextmv.log(f"managed_input_id={managed.id}")
    input_set = app.new_input_set(name="SDK assignment inputs", inputs=[managed])
    return {"managed_input_id": managed.id, "input_set_id": input_set.id}


def main():
    args = parser_for(__doc__).parse_args()
    if not args.execute:
        preview(
            args.app_id,
            [
                {"api": name}
                for name in [
                    "Application.upload_url",
                    "Application.upload_data",
                    "Application.new_managed_input",
                    "Application.new_input_set",
                ]
            ],
        )
        return
    nextmv.write(create_inputs(connect(args.app_id)))


if __name__ == "__main__":
    main()
