from pathlib import Path
from typing import Callable, List
from ..common.pipeline import run_pipeline
from .convert_heic import convert_heic_to_jpg

STEPS: List[Callable[[Path, Path, str], bool]] = [
    convert_heic_to_jpg
]

def process_image(in_path: Path, dst_dir: Path, base_name: str) -> None:
    run_pipeline(STEPS, in_path, dst_dir, base_name)