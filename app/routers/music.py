from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Optional
from app.database import get_db
from app.models import MusicTrack, Lesson, LessonItem
from app.services.music_scanner import scan_music
from config import BASE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

_MEDIA_TYPES = {
    ".mp3": "audio/mpeg", ".flac": "audio/flac", ".ogg": "audio/ogg",
    ".m4a": "audio/mp4", ".wav": "audio/wav",
}


def _music_context(db: Session) -> dict:
    return {
        "tracks": db.query(MusicTrack).order_by(MusicTrack.dance_type, MusicTrack.title).all(),
        "lessons": db.query(Lesson).order_by(Lesson.updated_at.desc()).all(),
    }


@router.get("/music", response_class=HTMLResponse)
def music_library(request: Request, db: Session = Depends(get_db)):
    ctx = _music_context(db)
    return templates.TemplateResponse("music.html", {"request": request, **ctx})


@router.post("/scan-music", response_class=HTMLResponse)
def trigger_scan(request: Request, db: Session = Depends(get_db)):
    result = scan_music(db)
    ctx = _music_context(db)
    return templates.TemplateResponse(
        "music.html", {"request": request, "scan_result": result, **ctx}
    )


@router.post("/music/{track_id}/add-to-lesson")
def add_to_lesson(
    track_id: int,
    lesson_id: int = Form(...),
    db: Session = Depends(get_db),
):
    track = db.query(MusicTrack).filter(MusicTrack.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404)
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404)
    from app.routers.lessons import _next_order
    db.add(LessonItem(
        lesson_id=lesson_id,
        item_type="audio",
        audio_id=track_id,
        order_index=_next_order(lesson),
        loop_count=1,
        speed=1.0,
        pause_after_seconds=0,
    ))
    db.commit()
    return RedirectResponse(url=f"/lessons/{lesson_id}/edit", status_code=303)


@router.get("/music/{track_id}/stream")
def stream_music(track_id: int, request: Request, db: Session = Depends(get_db)):
    track = db.query(MusicTrack).filter(MusicTrack.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404)
    raw = Path(track.filepath)
    filepath = raw if raw.is_absolute() else BASE_DIR / raw
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Musikdatei nicht gefunden")

    file_size = filepath.stat().st_size
    media_type = _MEDIA_TYPES.get(filepath.suffix.lower(), "audio/mpeg")
    range_header = request.headers.get("range")

    if range_header:
        parts = range_header.strip().replace("bytes=", "").split("-")
        start = int(parts[0])
        end = int(parts[1]) if parts[1] else file_size - 1
        end = min(end, file_size - 1)
        chunk_size = end - start + 1

        def iter_range():
            with open(filepath, "rb") as f:
                f.seek(start)
                remaining = chunk_size
                while remaining > 0:
                    data = f.read(min(65536, remaining))
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        return StreamingResponse(iter_range(), status_code=206, media_type=media_type, headers={
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
        })

    def iter_full():
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                yield chunk

    return StreamingResponse(iter_full(), media_type=media_type, headers={
        "Accept-Ranges": "bytes", "Content-Length": str(file_size),
    })
