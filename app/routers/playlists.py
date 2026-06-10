from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MusicPlaylist, PlaylistTrack, PlaylistPattern, MusicTrack
from config import BASE_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@router.get("/playlists", response_class=HTMLResponse)
def playlists_list(request: Request, db: Session = Depends(get_db)):
    playlists = db.query(MusicPlaylist).order_by(MusicPlaylist.title).all()
    return templates.TemplateResponse("playlists.html", {"request": request, "playlists": playlists})


@router.get("/playlists/new", response_class=HTMLResponse)
def playlist_new_form(request: Request):
    return templates.TemplateResponse("playlist_new.html", {"request": request})


@router.post("/playlists")
def playlist_create(
    title: str = Form(...),
    playlist_type: str = Form(...),
    notes: str = Form(""),
    repeat_count: int = Form(3),
    db: Session = Depends(get_db),
):
    playlist = MusicPlaylist(
        title=title,
        playlist_type=playlist_type,
        notes=notes or None,
        repeat_count=repeat_count,
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return RedirectResponse(url=f"/playlists/{playlist.id}/edit", status_code=303)


@router.get("/playlists/{playlist_id}/edit", response_class=HTMLResponse)
def playlist_edit(playlist_id: int, request: Request, db: Session = Depends(get_db)):
    playlist = db.query(MusicPlaylist).filter(MusicPlaylist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404)
    tracks = db.query(MusicTrack).filter(
        MusicTrack.dance_type != "cortina"
    ).order_by(MusicTrack.dance_type, MusicTrack.title).all()
    return templates.TemplateResponse(
        "playlist_edit.html", {"request": request, "playlist": playlist, "tracks": tracks}
    )


@router.post("/playlists/{playlist_id}/meta")
def playlist_update_meta(
    playlist_id: int,
    title: str = Form(...),
    notes: str = Form(""),
    repeat_count: int = Form(3),
    db: Session = Depends(get_db),
):
    playlist = db.query(MusicPlaylist).filter(MusicPlaylist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404)
    playlist.title = title
    playlist.notes = notes or None
    playlist.repeat_count = repeat_count
    db.commit()
    return RedirectResponse(url=f"/playlists/{playlist_id}/edit", status_code=303)


@router.post("/playlists/{playlist_id}/tracks")
def playlist_add_track(
    playlist_id: int,
    track_id: int = Form(...),
    db: Session = Depends(get_db),
):
    playlist = db.query(MusicPlaylist).filter(MusicPlaylist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404)
    next_order = max((t.order_index for t in playlist.playlist_tracks), default=-1) + 1
    db.add(PlaylistTrack(playlist_id=playlist_id, track_id=track_id, order_index=next_order))
    db.commit()
    return RedirectResponse(url=f"/playlists/{playlist_id}/edit", status_code=303)


def _swap_playlist_track(playlist_id: int, tid: int, direction: int, db: Session):
    items = (
        db.query(PlaylistTrack)
        .filter(PlaylistTrack.playlist_id == playlist_id)
        .order_by(PlaylistTrack.order_index, PlaylistTrack.id)
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


@router.post("/playlists/{playlist_id}/tracks/{tid}/up")
def playlist_track_up(playlist_id: int, tid: int, db: Session = Depends(get_db)):
    _swap_playlist_track(playlist_id, tid, -1, db)
    return RedirectResponse(url=f"/playlists/{playlist_id}/edit", status_code=303)


@router.post("/playlists/{playlist_id}/tracks/{tid}/down")
def playlist_track_down(playlist_id: int, tid: int, db: Session = Depends(get_db)):
    _swap_playlist_track(playlist_id, tid, 1, db)
    return RedirectResponse(url=f"/playlists/{playlist_id}/edit", status_code=303)


@router.post("/playlists/{playlist_id}/tracks/{tid}/remove")
def playlist_track_remove(playlist_id: int, tid: int, db: Session = Depends(get_db)):
    item = db.query(PlaylistTrack).filter(
        PlaylistTrack.id == tid, PlaylistTrack.playlist_id == playlist_id
    ).first()
    if not item:
        raise HTTPException(status_code=404)
    db.delete(item)
    db.commit()
    return RedirectResponse(url=f"/playlists/{playlist_id}/edit", status_code=303)


@router.post("/playlists/{playlist_id}/pattern")
def playlist_add_pattern(
    playlist_id: int,
    dance_type: str = Form(...),
    count: int = Form(1),
    db: Session = Depends(get_db),
):
    playlist = db.query(MusicPlaylist).filter(MusicPlaylist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404)
    next_order = max((p.order_index for p in playlist.pattern), default=-1) + 1
    db.add(PlaylistPattern(
        playlist_id=playlist_id, dance_type=dance_type,
        count=count, order_index=next_order,
    ))
    db.commit()
    return RedirectResponse(url=f"/playlists/{playlist_id}/edit", status_code=303)


def _swap_pattern(playlist_id: int, slot_id: int, direction: int, db: Session):
    items = (
        db.query(PlaylistPattern)
        .filter(PlaylistPattern.playlist_id == playlist_id)
        .order_by(PlaylistPattern.order_index, PlaylistPattern.id)
        .all()
    )
    for idx, it in enumerate(items):
        it.order_index = idx
    ids = [i.id for i in items]
    if slot_id not in ids:
        db.rollback()
        return
    pos = ids.index(slot_id)
    target = pos + direction
    if 0 <= target < len(items):
        items[pos].order_index, items[target].order_index = (
            items[target].order_index, items[pos].order_index
        )
    db.commit()


@router.post("/playlists/{playlist_id}/pattern/{slot_id}/up")
def pattern_up(playlist_id: int, slot_id: int, db: Session = Depends(get_db)):
    _swap_pattern(playlist_id, slot_id, -1, db)
    return RedirectResponse(url=f"/playlists/{playlist_id}/edit", status_code=303)


@router.post("/playlists/{playlist_id}/pattern/{slot_id}/down")
def pattern_down(playlist_id: int, slot_id: int, db: Session = Depends(get_db)):
    _swap_pattern(playlist_id, slot_id, 1, db)
    return RedirectResponse(url=f"/playlists/{playlist_id}/edit", status_code=303)


@router.post("/playlists/{playlist_id}/pattern/{slot_id}/remove")
def pattern_remove(playlist_id: int, slot_id: int, db: Session = Depends(get_db)):
    item = db.query(PlaylistPattern).filter(
        PlaylistPattern.id == slot_id, PlaylistPattern.playlist_id == playlist_id
    ).first()
    if not item:
        raise HTTPException(status_code=404)
    db.delete(item)
    db.commit()
    return RedirectResponse(url=f"/playlists/{playlist_id}/edit", status_code=303)


@router.post("/playlists/{playlist_id}/delete")
def playlist_delete(playlist_id: int, db: Session = Depends(get_db)):
    playlist = db.query(MusicPlaylist).filter(MusicPlaylist.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404)
    db.delete(playlist)
    db.commit()
    return RedirectResponse(url="/playlists", status_code=303)
