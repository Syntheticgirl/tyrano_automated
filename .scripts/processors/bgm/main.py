from pathlib import Path
from typing import Callable, List
from ..common.pipeline import run_pipeline
from .transcode import transcode_to_mp3

STEPS: List[Callable[[Path, Path, str], bool]] = [
    transcode_to_mp3,
]

def process_bgm(in_path: Path, dst_dir: Path, base_name: str) -> None:
    run_pipeline(STEPS, in_path, dst_dir, base_name)