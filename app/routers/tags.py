from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Tag
from config import BASE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

TAG_COLORS = {
    "Tanztyp": "#dc2626",
    "Bewegung": "#2563eb",
    "Musikalität": "#059669",
    "Qualität": "#0284c7",
    "Schwierigkeit": "#ca8a04",
    "Persönlicher Status": "#8b5cf6",
}


@router.get("/tags", response_class=HTMLResponse)
def tags_list(request: Request, db: Session = Depends(get_db)):
    all_tags = db.query(Tag).order_by(Tag.category, Tag.name).all()
    categories: dict[str, list] = {}
    for tag in all_tags:
        categories.setdefault(tag.category, []).append(tag)
    return templates.TemplateResponse(
        "tags.html", {"request": request, "categories": categories}
    )


@router.post("/tags", response_class=HTMLResponse)
def create_tag(
    request: Request,
    name: str = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db),
):
    color = TAG_COLORS.get(category, "#6b7280")
    tag = Tag(name=name, category=category, color=color)
    db.add(tag)
    db.commit()
    return RedirectResponse(url="/tags", status_code=303)
