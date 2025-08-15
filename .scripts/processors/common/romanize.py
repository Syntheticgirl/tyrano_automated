import os, re, unicodedata
from pathlib import Path
import pykakasi

_kakasi = pykakasi.kakasi()
_kakasi.setMode('H', 'a')
_kakasi.setMode('K', 'a')
_kakasi.setMode('J', 'a')
_converter = _kakasi.getConverter()

_jp_re = re.compile(r"[ぁ-んァ-ヴー一-龠]")

def romanize_filename(name: str) -> str:
    stem, ext = os.path.splitext(name)
    if _jp_re.search(stem):
        stem = unicodedata.normalize("NFC", stem)
        stem = _converter.do(stem)
    # stem = _safe_re.sub('-', stem).strip('-')
    # stem = re.sub(r"-+", "-", stem)
    # stem = stem.strip('.') or "untitled"
    return f"{stem}{ext}"