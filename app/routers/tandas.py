from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Tanda, TandaTrack, MusicTrack
from config import BASE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/tandas", response_class=HTMLResponse)
def tandas_list(request: Request, db: Session = Depends(get_db)):
    tandas = db.query(Tanda).order_by(Tanda.dance_type, Tanda.title).all()
    return templates.TemplateResponse("tandas.html", {"request": request, "tandas": tandas})


@router.get("/tandas/new", response_class=HTMLResponse)
def tanda_new_form(request: Request):
    return templates.TemplateResponse("tanda_new.html", {"request": request})


@router.post("/tandas")
def tanda_create(
    title: str = Form(...),
    dance_type: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    tanda = Tanda(title=title, dance_type=dance_type, notes=notes or None)
    db.add(tanda)
    db.commit()
    db.refresh(tanda)
    return RedirectResponse(url=f"/tandas/{tanda.id}/edit", status_code=303)


@router.get("/tandas/{tanda_id}/edit", response_class=HTMLResponse)
def tanda_edit(tanda_id: int, request: Request, db: Session = Depends(get_db)):
    tanda = db.query(Tanda).filter(Tanda.id == tanda_id).first()
    if not tanda:
        raise HTTPException(status_code=404)
    tracks = db.query(MusicTrack).filter(
        MusicTrack.dance_type == tanda.dance_type
    ).order_by(MusicTrack.title).all()
    return templates.TemplateResponse(
        "tanda_edit.html", {"request": request, "tanda": tanda, "tracks": tracks}
    )


@router.post("/tandas/{tanda_id}/tracks")
def tanda_add_track(
    tanda_id: int,
    track_id: int = Form(...),
    db: Session = Depends(get_db),
):
    tanda = db.query(Tanda).filter(Tanda.id == tanda_id).first()
    if not tanda:
        raise HTTPException(status_code=404)
    next_order = max((t.order_index for t in tanda.tracks), default=-1) + 1
    db.add(TandaTrack(tanda_id=tanda_id, track_id=track_id, order_index=next_order))
    db.commit()
    return RedirectResponse(url=f"/tandas/{tanda_id}/edit", status_code=303)


def _swap_tanda_track(tanda_id: int, tid: int, direction: int, db: Session):
    items = (
        db.query(TandaTrack)
        .filter(TandaTrack.tanda_id == tanda_id)
        .order_by(TandaTrack.order_index, TandaTrack.id)
        .all()
    )
    for idx, it in enumerate(items):
        it.order_index = idx
    ids = [i.id for i in items]
    if tid not in ids:
        db.rollback()
        return
    pos = ids.index(tid)
    target = pos + direction
    if 0 <= target < len(items):
        items[pos].order_index, items[target].order_index = (
            items[target].order_index, items[pos].order_index
        )
    db.commit()


@router.post("/tandas/{tanda_id}/tracks/{tid}/up")
def tanda_track_up(tanda_id: int, tid: int, db: Session = Depends(get_db)):
    _swap_tanda_track(tanda_id, tid, -1, db)
    return RedirectResponse(url=f"/tandas/{tanda_id}/edit", status_code=303)


@router.post("/tandas/{tanda_id}/tracks/{tid}/down")
def tanda_track_down(tanda_id: int, tid: int, db: Session = Depends(get_db)):
    _swap_tanda_track(tanda_id, tid, 1, db)
    return RedirectResponse(url=f"/tandas/{tanda_id}/edit", status_code=303)


@router.post("/tandas/{tanda_id}/tracks/{tid}/remove")
def tanda_track_remove(tanda_id: int, tid: int, db: Session = Depends(get_db)):
    item = db.query(TandaTrack).filter(
        TandaTrack.id == tid, TandaTrack.tanda_id == tanda_id
    ).first()
    if not item:
        raise HTTPException(status_code=404)
    db.delete(item)
    db.commit()
    return RedirectResponse(url=f"/tandas/{tanda_id}/edit", status_code=303)


@router.post("/tandas/{tanda_id}/delete")
def tanda_delete(tanda_id: int, db: Session = Depends(get_db)):
    tanda = db.query(Tanda).filter(Tanda.id == tanda_id).first()
    if not tanda:
        raise HTTPException(status_code=404)
    db.delete(tanda)
    db.commit()
    return RedirectResponse(url="/tandas", status_code=303)
