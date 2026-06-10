from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from app.database import get_db
from app.models import PracticeLog, Lesson
from config import BASE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

REVIEW_DAYS = {
    "klappt gut": 7,
    "noch unsicher": 3,
    "nicht verstanden": 1,
}


@router.post("/practice-log", response_class=JSONResponse)
async def create_practice_log(
    clip_id: int = Form(...),
    lesson_id: Optional[int] = Form(None),
    rating: str = Form(...),
    comment: str = Form(""),
    db: Session = Depends(get_db),
):
    days = REVIEW_DAYS.get(rating)
    next_review = datetime.utcnow() + timedelta(days=days) if days else None
    log = PracticeLog(
        clip_id=clip_id,
        lesson_id=lesson_id or None,
        rating=rating,
        comment=comment or None,
        next_review_date=next_review,
    )
    db.add(log)
    db.commit()
    return {"ok": True}


@router.get("/suggestions", response_class=HTMLResponse)
def suggestions(request: Request, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    all_logs = (
        db.query(PracticeLog)
        .filter(PracticeLog.clip_id.isnot(None))
        .order_by(PracticeLog.clip_id, PracticeLog.date.desc())
        .all()
    )
    seen: set[int] = set()
    clips_with_log = []
    for log in all_logs:
        if log.clip_id not in seen:
            seen.add(log.clip_id)
            is_due = log.next_review_date and log.next_review_date <= now
            is_weak = log.rating in ("noch unsicher", "nicht verstanden")
            if (is_due or is_weak) and log.clip:
                clips_with_log.append((log.clip, log))

    lessons = db.query(Lesson).order_by(Lesson.updated_at.desc()).all()
    return templates.TemplateResponse(
        "suggestions.html",
        {"request": request, "clips_with_log": clips_with_log, "lessons": lessons},
    )
