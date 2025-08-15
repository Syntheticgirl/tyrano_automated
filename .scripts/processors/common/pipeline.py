# pipeline.py
from pathlib import Path
from typing import Callable, Dict, List, Tuple
from .file_libs import ensure_dir, copy_as_is, iter_files
from .romanize import romanize_filename
from .manifest_libs import load_manifest, save_manifest, should_process, mark_processed

# 共通のパイプライン処理を実行する関数
def run_pipeline(steps: List[Callable[[Path, Path, str], bool]],
                 in_path: Path, dst_dir: Path, base_name: str) -> None:
    for step in steps:
        if step(in_path, dst_dir, base_name):
            return
    copy_as_is(in_path, dst_dir / base_name)

# 各ディレクトリに対して特定の処理を行う
def process_tree(src_root: Path,
                 dst_root: Path,
                 asset_map: Dict[str, Dict[str, Callable]],
                 mode: str = "diff") -> Tuple[int, int]:
    
    manifest = load_manifest()
    processed = 0
    skipped = 0
    touched = False
    
    for drive_src_dir_name, conf in asset_map.items():
        src_dir = src_root / drive_src_dir_name
        dst_rel = Path(conf["dst"])
        dst_dir_root = dst_rel if dst_rel.is_absolute() else (dst_root / dst_rel)

        handler = conf["handler"]

        if not src_dir.exists():
            print(f"[SKIP] {src_dir} not found")
            continue

        # 出力先ディレクトリを確保
        ensure_dir(dst_dir_root)
        print(f"[PROC] drive_src_dir_name={drive_src_dir_name} src={src_dir} -> dst={dst_dir_root}")

        for in_path in iter_files(src_dir):
            # 出力側にも同じサブフォルダ階層を再現
            rel_parent = in_path.relative_to(src_dir).parent  # '.' もあり得る
            dst_dir = (dst_dir_root / rel_parent)
            ensure_dir(dst_dir)

            # マニフェストキーは Drive 相対で安定化
            drive_rel_key = str(in_path.relative_to(src_root)).replace("\\", "/")

            # 差分判定
            if not should_process(in_path, drive_rel_key, manifest, mode):
                skipped += 1
                continue

            # ファイル名のローマ字化
            romanized_filename = romanize_filename(in_path.name)

            # 実処理
            handler(in_path, dst_dir, romanized_filename)

            # 記録
            mark_processed(in_path, drive_rel_key, manifest)
            processed += 1
            touched = True

    if touched:
        save_manifest(manifest)

    print(f"[DONE] processed={processed}, skipped={skipped}, mode={mode}")
    return processed, skipped