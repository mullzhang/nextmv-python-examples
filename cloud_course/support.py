"""認証と表示だけを共通化する。SDK の操作は各章に直接記述する。"""

import argparse
import json
import os
from pathlib import Path

import nextmv
from nextmv import cloud

ROOT = Path(__file__).resolve().parents[1]


def parser_for(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--execute", action="store_true", help="Nextmv Cloud に実際に接続する")
    parser.add_argument("--app-id", default="YOUR_APP_ID")
    return parser


def connect(app_id):
    if app_id.startswith("YOUR_"):
        raise ValueError("--app-id に実在するアプリ ID を指定してください")
    api_key = os.environ["NEXTMV_API_KEY"]
    if not api_key or api_key.startswith("YOUR_"):
        raise ValueError("NEXTMV_API_KEY に有効な API キーを設定してください")
    # 引数で指定し、CLI の認証設定に依存しない。書き込みの自動再送は避ける。
    client = cloud.Client(
        api_key=api_key,
        url="https://api.cloud.nextmv.io",
        allowed_methods=["GET"],
    )
    return cloud.Application.get(client=client, id=app_id)


def preview(app_id, steps):
    nextmv.write({"mode": "preview", "network": False, "app_id": app_id, "steps": steps})


def load_input():
    return json.loads((ROOT / "data" / "assignment.json").read_text())


def polling_options():
    # 待機終了は実行のキャンセルではない。ID を使って後から結果を取得できる。
    return nextmv.PollingOptions(max_duration=60, max_tries=60, max_delay=5)


def require_ids(**values):
    for name, value in values.items():
        if not value or value.startswith("YOUR_"):
            raise ValueError(f"{name} に実在する ID を指定してください")
