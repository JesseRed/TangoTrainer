from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Clip, Video, Tag, Lesson
from config import BASE_DIR, THUMBNAILS_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/clips", response_class=HTMLResponse)
def clips_list(
    request: Request,
    db: Session = Depends(get_db),
    q: str = "",
    tag: Optional[int] = None,
    difficulty: str = "",
    dance_type: str = "",
):
    query = db.query(Clip)

    if q:
        query = query.filter(
            Clip.title.ilike(f"%{q}%") | Clip.notes.ilike(f"%{q}%")
        )
    if difficulty:
        query = query.filter(Clip.difficulty == difficulty)
    if tag:
        query = query.filter(Clip.tags.any(Tag.id == tag))

    clips = query.order_by(Clip.created_at.desc()).all()
    all_tags = db.query(Tag).order_by(Tag.category, Tag.name).all()
    lessons = db.query(Lesson).order_by(Lesson.updated_at.desc()).all()

    return templates.TemplateResponse(
        "clips.html",
        {
            "request": request,
            "clips": clips,
            "all_tags": all_tags,
            "lessons": lessons,
            "q": q,
            "selected_tag": tag,
            "selected_difficulty": difficulty,
        },
    )


@router.post("/clips", response_class=HTMLResponse)
def create_clip(
    request: Request,
    video_id: int = Form(...),
    title: str = Form(...),
    start_seconds: float = Form(...),
    end_seconds: float = Form(...),
    notes: str = Form(""),
    technical_notes: str = Form(""),
    leader_notes: str = Form(""),
    follower_notes: str = Form(""),
    adaptation_notes: str = Form(""),
    difficulty: str = Form(""),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video nicht gefunden")

    clip = Clip(
        video_id=video_id,
        title=title,
        start_seconds=start_seconds,
        end_seconds=end_seconds,
        notes=notes or None,
        technical_notes=technical_notes or None,
        leader_notes=leader_notes or None,
        follower_notes=follower_notes or None,
        adaptation_notes=adaptation_notes or None,
        difficulty=difficulty or None,
    )
    db.add(clip)
    db.commit()
    db.refresh(clip)
    return RedirectResponse(url=f"/clips/{clip.id}/tags", status_code=303)


@router.get("/clips/{clip_id}", response_class=HTMLResponse)
def clip_detail(clip_id: int, request: Request, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip nicht gefunden")
    return templates.TemplateResponse("clip_detail.html", {"request": request, "clip": clip})


@router.get("/clips/{clip_id}/tags", response_class=HTMLResponse)
def clip_tags_form(clip_id: int, request: Request, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip nicht gefunden")
    all_tags = db.query(Tag).order_by(Tag.category, Tag.name).all()
    current_tag_ids = {t.id for t in clip.tags}

    # Group tags by category
    categories: dict[str, list] = {}
    for tag in all_tags:
        categories.setdefault(tag.category, []).append(tag)

    return templates.TemplateResponse(
        "clip_tags.html",
        {
            "request": request,
            "clip": clip,
            "categories": categories,
            "current_tag_ids": current_tag_ids,
        },
    )


@router.post("/clips/{clip_id}/tags", response_class=HTMLResponse)
async def update_clip_tags(clip_id: int, request: Request, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip nicht gefunden")

    form = await request.form()
    tag_ids = [int(v) for k, v in form.multi_items() if k == "tag_ids"]
    tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
    clip.tags = tags
    db.commit()
    return RedirectResponse(url=f"/clips/{clip_id}", status_code=303)


@router.post("/clips/{clip_id}/thumbnail", response_class=JSONResponse)
async def set_clip_thumbnail(
    clip_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip nicht gefunden")
    THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
    thumb_path = THUMBNAILS_DIR / f"clip_{clip_id}.jpg"
    content = await image.read()
    thumb_path.write_bytes(content)
    clip.thumbnail_path = str(thumb_path.relative_to(BASE_DIR))
    db.commit()
    return {"ok": True}


@router.post("/clips/{clip_id}/delete")
def delete_clip(clip_id: int, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip nicht gefunden")
    db.delete(clip)
    db.commit()
    return RedirectResponse(url="/clips", status_code=303)


@router.post("/clips/{clip_id}/rename")
def rename_clip(clip_id: int, title: str = Form(...), db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.id == clip_id).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip nicht gefunden")
    clip.title = title.strip()
    db.commit()
    return RedirectResponse(url=f"/clips/{clip_id}", status_code=303)
