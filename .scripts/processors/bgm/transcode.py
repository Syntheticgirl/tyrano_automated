# processors/bgm/transcode.py
import subprocess
from pathlib import Path

# 音声拡張子の候補（最低限）
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma", ".aiff"}

def is_audio_file(in_path: Path) -> bool:
    """拡張子ベースで簡易判定。ffprobe利用ならもっと精密にできる。"""
    return in_path.suffix.lower() in AUDIO_EXTS

def transcode_to_mp3(in_path: Path, dst_dir: Path, base_name: str) -> bool:
    """
    音声ファイルなら mp3 に変換。それ以外は未処理（False）。
    - 出力名は拡張子を .mp3 にしたもの
    - 再実行時は新しければスキップ
    """
    if not is_audio_file(in_path):
        return False  # 音声ファイルでなければスキップ

    out_path = dst_dir / Path(base_name).with_suffix(".mp3").name
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 既に最新ならスキップ
    if out_path.exists() and out_path.stat().st_mtime >= in_path.stat().st_mtime:
        print(f"[SKIP] up-to-date: {out_path.name}")
        return True

    cmd = [
        "ffmpeg", "-y",
        "-i", str(in_path),
        "-vn",                       # 映像ストリーム無効化
        "-codec:a", "libmp3lame",    # mp3 エンコーダ
        "-qscale:a", "2",            # 品質(0=最高, 9=最低; 2は高音質/中サイズ)
        str(out_path)
    ]

    print(f"[FFMPEG] {in_path.name} -> {out_path.name}")
    subprocess.run(cmd, check=True)

    return True