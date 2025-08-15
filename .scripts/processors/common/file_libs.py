from pathlib import Path
import shutil

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def copy_as_is(src: Path, dst: Path) -> None:
    ensure_dir(dst.parent)
    if src.is_file():
        shutil.copy2(src, dst)

# 指定したディレクトリ以下のすべてのファイルパスを返す
def iter_files(root: Path):
    yield from (p for p in root.rglob("*") if p.is_file())
