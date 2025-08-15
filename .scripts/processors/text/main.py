from pathlib import Path
from typing import Callable, List
from ..common.pipeline import run_pipeline
from .convert_to_ks import convert_to_ks

STEPS: List[Callable[[Path, Path, str], bool]] = [
    # ここに適用したい関数を追加
    convert_to_ks
]

def process_text(in_path: Path, dst_dir: Path, base_name: str) -> None:
    run_pipeline(STEPS, in_path, dst_dir, base_name)