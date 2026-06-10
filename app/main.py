from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from app.seed import seed_tags
from app.database import SessionLocal
from app.routers import videos, clips, tags, player, settings, lessons, practice, music, remote, tandas, playlists
from config import BASE_DIR, THUMBNAILS_DIR

app = FastAPI(title="TangoTrainer")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")

THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/data/thumbnails", StaticFiles(directory=str(THUMBNAILS_DIR)), name="thumbnails")

app.include_router(videos.router)
app.include_router(clips.router)
app.include_router(tags.router)
app.include_router(player.router)
app.include_router(settings.router)
app.include_router(lessons.router)
app.include_router(practice.router)
app.include_router(music.router)
app.include_router(remote.router)
app.include_router(tandas.router)
app.include_router(playlists.router)


@app.on_event("startup")
def startup():
    from app.database import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        for col, default in [
            ("dance_type", "NULL"),
            ("status", "'neu'"),
            ("song_title", "NULL"),
            ("composer", "NULL"),
        ]:
            try:
                conn.execute(text(f"ALTER TABLE videos ADD COLUMN {col} TEXT DEFAULT {default}"))
            except Exception:
                pass
        conn.execute(text("UPDATE videos SET status = 'neu' WHERE status IS NULL"))
        conn.commit()
    init_db()
    db = SessionLocal()
    try:
        seed_tags(db)
    finally:
        db.close()
