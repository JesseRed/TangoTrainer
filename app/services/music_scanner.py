import subprocess
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import MusicTrack
from config import BASE_DIR, MUSIC_DIR, MUSIC_EXTENSIONS


def _probe_audio(filepath: Path) -> dict:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", str(filepath)],
            capture_output=True, text=True, timeout=30,
        )
        data = json.loads(result.stdout)
        fmt = data.get("format", {})
        tags = {k.lower(): v for k, v in fmt.get("tags", {}).items()}
        return {
            "duration": float(fmt.get("duration", 0)) or None,
            "title": tags.get("title"),
            "orchestra": tags.get("artist") or tags.get("album_artist"),
            "singer": tags.get("composer"),
        }
    except Exception:
        return {}


def scan_music(db: Session) -> dict:
    scan_dirs = [MUSIC_DIR]
    added = 0
    skipped = 0

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for filepath in scan_dir.rglob("*"):
            if filepath.suffix.lower() not in MUSIC_EXTENSIONS:
                continue

            try:
                rel_path = str(filepath.relative_to(BASE_DIR))
            except ValueError:
                rel_path = str(filepath)

            if db.query(MusicTrack).filter(MusicTrack.filepath == rel_path).first():
                skipped += 1
                continue

            meta = _probe_audio(filepath)
            parent = filepath.parent.name.lower()
            dance_type = next((t for t in ("tango", "milonga", "vals", "cortina") if t in parent), None)

            track = MusicTrack(
                filepath=rel_path,
                title=meta.get("title") or filepath.stem.replace("_", " ").replace("-", " ").title(),
                orchestra=meta.get("orchestra"),
                singer=meta.get("singer"),
                duration=meta.get("duration"),
                dance_type=dance_type,
            )
            db.add(track)
            added += 1

    db.commit()
    return {"added": added, "skipped": skipped}
