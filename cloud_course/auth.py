"""明示した API キーで、既存アプリの情報を1回取得する。"""

import nextmv

from cloud_course.support import connect, parser_for, preview


def main():
    args = parser_for(__doc__).parse_args()
    if not args.execute:
        preview(args.app_id, [{"api": "Application.get", "auth_env": "NEXTMV_API_KEY"}])
        return
    app = connect(args.app_id)
    # Client や認証情報を含む Application 全体を表示しない。
    nextmv.write({"app_id": app.id, "connected": True})


if __name__ == "__main__":
    main()
