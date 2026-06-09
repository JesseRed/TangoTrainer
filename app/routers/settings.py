from pathlib import Path
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import WatchDir
from config import BASE_DIR, VIDEOS_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, db: Session = Depends(get_db)):
    watch_dirs = db.query(WatchDir).order_by(WatchDir.label).all()
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "watch_dirs": watch_dirs,
            "default_dir": str(VIDEOS_DIR),
        },
    )


@router.post("/settings/watch-dirs", response_class=HTMLResponse)
def add_watch_dir(
    request: Request,
    path: str = Form(...),
    label: str = Form(""),
    db: Session = Depends(get_db),
):
    path = path.strip()
    if not Path(path).is_dir():
        watch_dirs = db.query(WatchDir).order_by(WatchDir.label).all()
        return templates.TemplateResponse(
            "settings.html",
            {
                "request": request,
                "watch_dirs": watch_dirs,
                "default_dir": str(VIDEOS_DIR),
                "error": f"Verzeichnis existiert nicht: {path}",
                "form_path": path,
                "form_label": label,
            },
            status_code=422,
        )

    existing = db.query(WatchDir).filter(WatchDir.path == path).first()
    if not existing:
        db.add(WatchDir(path=path, label=label or None))
        db.commit()

    return RedirectResponse(url="/settings", status_code=303)


@router.post("/settings/watch-dirs/{dir_id}/delete")
def delete_watch_dir(dir_id: int, db: Session = Depends(get_db)):
    watch_dir = db.query(WatchDir).filter(WatchDir.id == dir_id).first()
    if not watch_dir:
        raise HTTPException(status_code=404)
    db.delete(watch_dir)
    db.commit()
    return RedirectResponse(url="/settings", status_code=303)


@router.post("/settings/watch-dirs/{dir_id}/toggle")
def toggle_watch_dir(dir_id: int, db: Session = Depends(get_db)):
    watch_dir = db.query(WatchDir).filter(WatchDir.id == dir_id).first()
    if not watch_dir:
        raise HTTPException(status_code=404)
    watch_dir.active = 0 if watch_dir.active else 1
    db.commit()
    return RedirectResponse(url="/settings", status_code=303)
