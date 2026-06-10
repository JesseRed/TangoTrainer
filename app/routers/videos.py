import os
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, Query
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Video
from app.services.scanner import scan_videos
from config import BASE_DIR, THUMBNAILS_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/", response_class=HTMLResponse)
def library(
    request: Request,
    dance_type: List[str] = Query(default=[]),
    status: List[str] = Query(default=[]),
    q: str = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Video)
    if dance_type:
        query = query.filter(Video.dance_type.in_(dance_type))
    if status:
        query = query.filter(Video.status.in_(status))
    if q:
        like = f"%{q}%"
        query = query.filter(
            Video.song_title.ilike(like)
            | Video.composer.ilike(like)
            | Video.dancer_1.ilike(like)
            | Video.dancer_2.ilike(like)
            | Video.title.ilike(like)
        )
    videos = query.order_by(Video.created_at.desc()).all()
    return templates.TemplateResponse("library.html", {
        "request": request,
        "videos": videos,
        "filter_dance_types": dance_type,
        "filter_statuses": status,
        "search_q": q or "",
    })


@router.get("/videos/{video_id}", response_class=HTMLResponse)
def video_detail(video_id: int, request: Request, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video nicht gefunden")
    return templates.TemplateResponse("video_detail.html", {"request": request, "video": video})


@router.post("/videos/{video_id}/meta")
def video_update_meta(
    video_id: int,
    dance_type: str = Form(""),
    status: str = Form("neu"),
    song_title: str = Form(""),
    composer: str = Form(""),
    dancer_1: str = Form(""),
    dancer_2: str = Form(""),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video nicht gefunden")
    video.dance_type = dance_type.strip() or None
    video.status = status
    video.song_title = song_title.strip() or None
    video.composer = composer.strip() or None
    video.dancer_1 = dancer_1.strip() or None
    video.dancer_2 = dancer_2.strip() or None
    db.commit()
    return RedirectResponse(url=f"/videos/{video_id}", status_code=303)


@router.post("/scan", response_class=HTMLResponse)
def trigger_scan(request: Request, db: Session = Depends(get_db)):
    result = scan_videos(db)
    videos = db.query(Video).order_by(Video.created_at.desc()).all()
    return templates.TemplateResponse(
        "partials/video_grid.html",
        {"request": request, "videos": videos, "scan_result": result},
    )


@router.get("/videos/{video_id}/stream")
def stream_video(video_id: int, request: Request, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video nicht gefunden")

    raw = Path(video.filepath)
    filepath = raw if raw.is_absolute() else BASE_DIR / raw
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Videodatei nicht gefunden")

    file_size = filepath.stat().st_size
    range_header = request.headers.get("range")

    if range_header:
        range_val = range_header.strip().replace("bytes=", "")
        parts = range_val.split("-")
        start = int(parts[0])
        end = int(parts[1]) if parts[1] else file_size - 1
        end = min(end, file_size - 1)
        chunk_size = end - start + 1

        def iter_file():
            with open(filepath, "rb") as f:
                f.seek(start)
                remaining = chunk_size
                while remaining > 0:
                    data = f.read(min(65536, remaining))
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": "video/mp4",
        }
        return StreamingResponse(iter_file(), status_code=206, headers=headers)

    def iter_full():
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                yield chunk

    return StreamingResponse(
        iter_full(),
        headers={"Accept-Ranges": "bytes", "Content-Length": str(file_size)},
        media_type="video/mp4",
    )


@router.post("/videos/{video_id}/thumbnail", response_class=JSONResponse)
async def set_video_thumbnail(
    video_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video nicht gefunden")
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
    thumb_path = THUMBNAILS_DIR / f"video_{video_id}.jpg"
    content = await image.read()
    thumb_path.write_bytes(content)
    video.thumbnail_path = str(thumb_path.relative_to(BASE_DIR))
    db.commit()
    return {"ok": True}


@router.get("/thumbnails/{filename}")
def serve_thumbnail(filename: str):
    from fastapi.responses import FileResponse
    from config import THUMBNAILS_DIR
    path = THUMBNAILS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(str(path))
