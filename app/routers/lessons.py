from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Lesson, LessonItem, Clip, MusicTrack
from config import BASE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


# ── Lessons CRUD ────────────────────────────────────────────────────────────

@router.get("/lessons", response_class=HTMLResponse)
def lessons_list(request: Request, db: Session = Depends(get_db)):
    lessons = db.query(Lesson).order_by(Lesson.updated_at.desc()).all()
    return templates.TemplateResponse("lessons.html", {"request": request, "lessons": lessons})


@router.get("/lessons/new", response_class=HTMLResponse)
def lesson_new_form(request: Request, clip_ids: Optional[str] = Query(None)):
    return templates.TemplateResponse(
        "lesson_new.html", {"request": request, "clip_ids": clip_ids or ""}
    )


@router.post("/lessons", response_class=HTMLResponse)
def lesson_create(
    title: str = Form(...),
    description: str = Form(""),
    goal: str = Form(""),
    planned_duration: Optional[int] = Form(None),
    clip_ids: str = Form(""),
    db: Session = Depends(get_db),
):
    lesson = Lesson(
        title=title,
        description=description or None,
        goal=goal or None,
        planned_duration=planned_duration,
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    if clip_ids:
        ids = [int(i) for i in clip_ids.split(",") if i.strip().isdigit()]
        next_index = 0
        for clip_id in ids:
            clip = db.query(Clip).filter(Clip.id == clip_id).first()
            if clip:
                db.add(LessonItem(
                    lesson_id=lesson.id,
                    item_type="clip",
                    clip_id=clip_id,
                    order_index=next_index,
                    loop_count=clip.default_loop_count,
                    speed=clip.default_speed,
                    pause_after_seconds=clip.pause_after_seconds,
                ))
                next_index += 1
        db.commit()

    return RedirectResponse(url=f"/lessons/{lesson.id}/edit", status_code=303)


@router.get("/lessons/{lesson_id}/edit", response_class=HTMLResponse)
def lesson_edit(lesson_id: int, request: Request, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Übungsstunde nicht gefunden")
    music_tracks = db.query(MusicTrack).order_by(MusicTrack.dance_type, MusicTrack.title).all()
    return templates.TemplateResponse(
        "lesson_edit.html", {"request": request, "lesson": lesson, "music_tracks": music_tracks}
    )


@router.post("/lessons/{lesson_id}/meta", response_class=HTMLResponse)
def lesson_update_meta(
    lesson_id: int,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    goal: str = Form(""),
    planned_duration: Optional[int] = Form(None),
    db: Session = Depends(get_db),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Übungsstunde nicht gefunden")
    lesson.title = title
    lesson.description = description or None
    lesson.goal = goal or None
    lesson.planned_duration = planned_duration
    db.commit()
    return RedirectResponse(url=f"/lessons/{lesson_id}/edit", status_code=303)


@router.post("/lessons/{lesson_id}/delete")
def lesson_delete(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Übungsstunde nicht gefunden")
    db.delete(lesson)
    db.commit()
    return RedirectResponse(url="/lessons", status_code=303)


# ── Item Management ─────────────────────────────────────────────────────────

def _next_order(lesson: Lesson) -> int:
    if not lesson.items:
        return 0
    return max(i.order_index for i in lesson.items) + 1


@router.post("/lessons/{lesson_id}/items/bulk", response_class=HTMLResponse)
async def items_bulk_add(lesson_id: int, request: Request, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404)
    form = await request.form()
    clip_ids = [int(v) for k, v in form.multi_items() if k == "clip_ids"]
    next_index = _next_order(lesson)
    for clip_id in clip_ids:
        clip = db.query(Clip).filter(Clip.id == clip_id).first()
        if clip:
            db.add(LessonItem(
                lesson_id=lesson_id,
                item_type="clip",
                clip_id=clip_id,
                order_index=next_index,
                loop_count=clip.default_loop_count,
                speed=clip.default_speed,
                pause_after_seconds=clip.pause_after_seconds,
            ))
            next_index += 1
    db.commit()
    return RedirectResponse(url=f"/lessons/{lesson_id}/edit", status_code=303)


@router.post("/lessons/{lesson_id}/items/text", response_class=HTMLResponse)
def item_add_text(
    lesson_id: int,
    title: str = Form(...),
    text_instruction: str = Form(""),
    db: Session = Depends(get_db),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404)
    db.add(LessonItem(
        lesson_id=lesson_id,
        item_type="text",
        text_instruction=f"{title}\n\n{text_instruction}".strip() if text_instruction else title,
        order_index=_next_order(lesson),
    ))
    db.commit()
    return RedirectResponse(url=f"/lessons/{lesson_id}/edit", status_code=303)


@router.post("/lessons/{lesson_id}/items/music", response_class=HTMLResponse)
def item_add_music(
    lesson_id: int,
    track_id: int = Form(...),
    db: Session = Depends(get_db),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404)
    track = db.query(MusicTrack).filter(MusicTrack.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Musikstück nicht gefunden")
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


@router.post("/lessons/{lesson_id}/items/{item_id}/duplicate", response_class=HTMLResponse)
def item_duplicate(lesson_id: int, item_id: int, db: Session = Depends(get_db)):
    item = db.query(LessonItem).filter(
        LessonItem.id == item_id, LessonItem.lesson_id == lesson_id
    ).first()
    if not item or item.item_type != "clip":
        raise HTTPException(status_code=404)
    # Shift all items after this one up by 1
    db.query(LessonItem).filter(
        LessonItem.lesson_id == lesson_id,
        LessonItem.order_index > item.order_index,
    ).update({"order_index": LessonItem.order_index + 1})
    db.add(LessonItem(
        lesson_id=lesson_id,
        item_type="clip",
        clip_id=item.clip_id,
        order_index=item.order_index + 1,
        loop_count=item.loop_count,
        speed=0.5,
        pause_after_seconds=item.pause_after_seconds,
        show_notes=item.show_notes,
    ))
    db.commit()
    return RedirectResponse(url=f"/lessons/{lesson_id}/edit", status_code=303)


@router.post("/lessons/{lesson_id}/items/{item_id}/update", response_class=HTMLResponse)
def item_update(
    lesson_id: int,
    item_id: int,
    loop_count: int = Form(1),
    speed: float = Form(1.0),
    pause_after_seconds: int = Form(0),
    show_notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    item = db.query(LessonItem).filter(
        LessonItem.id == item_id, LessonItem.lesson_id == lesson_id
    ).first()
    if not item:
        raise HTTPException(status_code=404)
    item.loop_count = max(1, loop_count)
    item.speed = max(0.25, min(2.0, speed / 100))
    item.pause_after_seconds = max(0, pause_after_seconds)
    item.show_notes = 1 if show_notes else 0
    db.commit()
    return RedirectResponse(url=f"/lessons/{lesson_id}/edit", status_code=303)


@router.post("/lessons/{lesson_id}/items/{item_id}/delete", response_class=HTMLResponse)
def item_delete(lesson_id: int, item_id: int, db: Session = Depends(get_db)):
    item = db.query(LessonItem).filter(
        LessonItem.id == item_id, LessonItem.lesson_id == lesson_id
    ).first()
    if not item:
        raise HTTPException(status_code=404)
    db.delete(item)
    # Reindex remaining items
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    db.flush()
    for idx, remaining in enumerate(sorted(lesson.items, key=lambda x: x.order_index)):
        remaining.order_index = idx
    db.commit()
    return RedirectResponse(url=f"/lessons/{lesson_id}/edit", status_code=303)


@router.post("/lessons/{lesson_id}/items/{item_id}/up", response_class=HTMLResponse)
def item_move_up(lesson_id: int, item_id: int, db: Session = Depends(get_db)):
    _swap_item(lesson_id, item_id, direction=-1, db=db)
    return RedirectResponse(url=f"/lessons/{lesson_id}/edit", status_code=303)


@router.post("/lessons/{lesson_id}/items/{item_id}/down", response_class=HTMLResponse)
def item_move_down(lesson_id: int, item_id: int, db: Session = Depends(get_db)):
    _swap_item(lesson_id, item_id, direction=1, db=db)
    return RedirectResponse(url=f"/lessons/{lesson_id}/edit", status_code=303)


def _swap_item(lesson_id: int, item_id: int, direction: int, db: Session):
    # Direct query with stable sort (id as tiebreaker for equal order_index values)
    items = (
        db.query(LessonItem)
        .filter(LessonItem.lesson_id == lesson_id)
        .order_by(LessonItem.order_index, LessonItem.id)
        .all()
    )
    # Normalize order_indexes to 0,1,2,... first (fixes any duplicate/gap state)
    for idx, it in enumerate(items):
        it.order_index = idx
    ids = [i.id for i in items]
    if item_id not in ids:
        db.rollback()
        return
    pos = ids.index(item_id)
    target = pos + direction
    if 0 <= target < len(items):
        items[pos].order_index, items[target].order_index = (
            items[target].order_index, items[pos].order_index
        )
    db.commit()
