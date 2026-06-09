from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Clip, Lesson, LessonItem
from config import BASE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


def _clip_to_item(clip: Clip, item: LessonItem | None = None) -> dict:
    """Convert a Clip (+ optional LessonItem settings) to the player item dict."""
    loop_count = item.loop_count if item else clip.default_loop_count
    speed = item.speed if item else clip.default_speed
    pause_after = item.pause_after_seconds if item else clip.pause_after_seconds
    show_notes = bool(item.show_notes) if item else True
    return {
        "id": clip.id,
        "title": clip.title,
        "start": clip.start_seconds,
        "end": clip.end_seconds,
        "videoId": clip.video_id,
        "notes": clip.notes or "",
        "technicalNotes": clip.technical_notes or "",
        "adaptationNotes": clip.adaptation_notes or "",
        "tags": [{"name": t.name, "color": t.color} for t in clip.tags],
        "loopCount": loop_count,
        "speed": speed,
        "pauseAfter": pause_after,
        "showNotes": show_notes,
        "itemType": "clip",
        "textInstruction": "",
        "difficulty": clip.difficulty or "",
    }


@router.get("/player", response_class=HTMLResponse)
def player(
    request: Request,
    clip_ids: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    if clip_ids:
        ids = [int(i) for i in clip_ids.split(",") if i.strip().isdigit()]
        clips = db.query(Clip).filter(Clip.id.in_(ids)).all()
        clip_map = {c.id: c for c in clips}
        items = [_clip_to_item(clip_map[i]) for i in ids if i in clip_map]
    else:
        clips = db.query(Clip).order_by(Clip.created_at.desc()).limit(20).all()
        items = [_clip_to_item(c) for c in clips]

    return templates.TemplateResponse(
        "player.html",
        {"request": request, "items": items, "lesson": None},
    )


@router.get("/player/lesson/{lesson_id}", response_class=HTMLResponse)
def player_lesson(lesson_id: int, request: Request, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Übungsstunde nicht gefunden")

    items = []
    for lesson_item in sorted(lesson.items, key=lambda x: x.order_index):
        if lesson_item.item_type == "clip" and lesson_item.clip:
            items.append(_clip_to_item(lesson_item.clip, lesson_item))
        elif lesson_item.item_type == "text":
            parts = (lesson_item.text_instruction or "").split("\n\n", 1)
            items.append({
                "id": None,
                "title": parts[0] if parts else "Anweisung",
                "start": 0, "end": 0, "videoId": None,
                "notes": parts[1] if len(parts) > 1 else "",
                "technicalNotes": "", "adaptationNotes": "",
                "tags": [],
                "loopCount": 1, "speed": 1.0, "pauseAfter": 0,
                "showNotes": True,
                "itemType": "text",
                "textInstruction": lesson_item.text_instruction or "",
                "difficulty": "",
            })

    return templates.TemplateResponse(
        "player.html",
        {"request": request, "items": items, "lesson": lesson},
    )
