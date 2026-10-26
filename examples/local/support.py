"""ローカル実行の保存場所をリポジトリ内にそろえる補助処理。"""

import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
APP_DIR = ROOT / "apps" / "assignment"
INPUT_PATH = ROOT / "data" / "assignment.json"


def load_input():
    return json.loads(INPUT_PATH.read_text())


@contextmanager
def local_environment():
    """SDK の登録ファイルだけを隔離し、実行 API 自体は差し替えない。"""
    registry_dir = ROOT / "artifacts" / "local-registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    # SDK 1.12.0 は公開 API に登録先の指定がない。バージョン依存箇所をここに限定する。
    # HOME は変更しない。既存の ~/.nextmv の設定も読み取らない。
    with (
        patch("nextmv.local.registry.NEXTMV_DIR", str(registry_dir)),
        patch.dict(
            os.environ,
            {
                "UV_CACHE_DIR": str(ROOT / ".uv-cache"),
                "UV_OFFLINE": "1",
                "UV_NO_PROJECT": "1",
                "UV_PYTHON": sys.executable,
                "VIRTUAL_ENV": str(Path(sys.executable).parent.parent),
            },
        ),
    ):
        yield
