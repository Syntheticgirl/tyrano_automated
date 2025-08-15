from pathlib import Path
import hashlib, json

MANIFEST_PATH = Path("data/.asset_manifest.json")

def _hash_file(fp: Path) -> str:
    h = hashlib.md5()
    with fp.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}

def save_manifest(m: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

def should_process(in_path: Path, key: str, manifest: dict, mode: str) -> bool:
    if mode == "full":
        return True
    sig = _hash_file(in_path)
    return manifest.get(key) != sig

def mark_processed(in_path: Path, key: str, manifest: dict) -> None:
    manifest[key] = _hash_file(in_path)
