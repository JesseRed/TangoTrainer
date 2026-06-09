from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from app.seed import seed_tags
from app.database import SessionLocal
from app.routers import videos, clips, tags, player, settings, lessons
from config import BASE_DIR

app = FastAPI(title="TangoTrainer")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")

app.include_router(videos.router)
app.include_router(clips.router)
app.include_router(tags.router)
app.include_router(player.router)
app.include_router(settings.router)
app.include_router(lessons.router)


@app.on_event("startup")
def startup():
    init_db()
    db = SessionLocal()
    try:
        seed_tags(db)
    finally:
        db.close()
