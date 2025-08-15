import os
from pathlib import Path
from processors.common.pipeline import process_tree
from processors.bgm.main import process_bgm
from processors.text.main import process_text
from processors.image.main import process_image

"""
google drive のフォルダを記述
"""

BGM_SRC   = os.getenv("DRIVE_BGM_DIR", "音楽")
TEXT_SRC  = os.getenv("DRIVE_TEXT_DIR", "テキスト")
IMAGE_SRC = os.getenv("DRIVE_IMAGE_DIR", "画像")

ASSET_MAP = {
    BGM_SRC:   {"dst": "assets/bgm",     "handler": process_bgm},
    TEXT_SRC:  {"dst": "assets/scenario","handler": process_text},
    IMAGE_SRC: {"dst": "assets/image",   "handler": process_image},
}

if __name__ == "__main__":
    process_tree(Path("temp_drive"), Path("data"), ASSET_MAP)
