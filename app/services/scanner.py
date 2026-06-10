import subprocess
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Video
from config import BASE_DIR, VIDEOS_DIR, THUMBNAILS_DIR, VIDEO_EXTENSIONS


def _probe(filepath: Path) -> dict:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", str(filepath)],
            capture_output=True, text=True, timeout=30,
        )
        data = json.loads(result.stdout)
        return {"duration": float(data["format"].get("duration", 0))}
    except Exception:
        return {"duration": None}


def generate_thumbnail(filepath: Path, video_id: int) -> str | None:
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
    thumb_path = THUMBNAILS_DIR / f"video_{video_id}.jpg"
    try:
        meta = _probe(filepath)
        seek = max(0, (meta.get("duration") or 60) * 0.1)
        subprocess.run(
            ["ffmpeg", "-ss", str(seek), "-i", str(filepath),
             "-vframes", "1", "-q:v", "2", str(thumb_path), "-y"],
            capture_output=True, timeout=30,
        )
        if thumb_path.exists():
            return str(thumb_path.relative_to(BASE_DIR))
        return None
    except Exception:
        return None


def scan_videos(db: Session, scan_dirs: list[Path] | None = None) -> dict:
    if scan_dirs is None:
        from app.models import WatchDir
        extra = [Path(w.path) for w in db.query(WatchDir).filter(WatchDir.active == 1).all()]
        scan_dirs = [VIDEOS_DIR] + extra

    added = 0
    skipped = 0

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for filepath in scan_dir.rglob("*"):
            if filepath.suffix.lower() not in VIDEO_EXTENSIONS:
                continue

            try:
                rel_path = str(filepath.relative_to(BASE_DIR))
            except ValueError:
                rel_path = str(filepath)

            if db.query(Video).filter(Video.filepath == rel_path).first():
                skipped += 1
                continue

            meta = _probe(filepath)
            known_types = {"tango", "milonga", "vals", "workshop", "showdance"}
            dance_type = None
            for part in Path(rel_path).parts[:-1]:
                if part.lower() in known_types:
                    dance_type = part.lower()
                    break
            video = Video(
                filepath=rel_path,
                filename=filepath.name,
                title=filepath.stem.replace("_", " ").replace("-", " ").title(),
                duration=meta.get("duration"),
                dance_type=dance_type,
                status="neu",
            )
            db.add(video)
            db.flush()

            thumb = generate_thumbnail(filepath, video.id)
            if thumb:
                video.thumbnail_path = thumb

            added += 1

    db.commit()
    return {"added": added, "skipped": skipped}
