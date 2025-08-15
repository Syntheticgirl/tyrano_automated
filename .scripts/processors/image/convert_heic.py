from pathlib import Path
from PIL import Image
import pillow_heif

def convert_heic_to_jpg(in_path: Path, dst_dir: Path, base_name: str) -> bool:
    """
    HEIC 画像を JPEG に変換する。
    - 対象が HEIC (.heic/.HEIC) 以外なら False を返す
    - 出力は同名の .jpg ファイル
    """
    if in_path.suffix.lower() != ".heic":
        return False  # HEICでなければ処理しない

    out_path = dst_dir / Path(base_name).with_suffix(".jpg").name
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # HEIC 読み込み
    heif_file = pillow_heif.read_heif(str(in_path))
    for img in heif_file:
        image = Image.frombytes(
            img.mode,
            img.size,
            img.data.tobytes(),
            'raw',
            img.mode,
            img.stride,
        )
        image.save(str(out_path), "JPEG", quality=95)

    print(f"[HEIC->JPG] {in_path.name} -> {out_path.name}")
    return True