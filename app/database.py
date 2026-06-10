from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import DATABASE_DIR, DATABASE_URL

DATABASE_DIR.mkdir(parents=True, exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app import models  # noqa: F401
    from sqlalchemy import text
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        for stmt in [
            "ALTER TABLE clips ADD COLUMN thumbnail_path VARCHAR",
            "ALTER TABLE lesson_items ADD COLUMN audio_id INTEGER REFERENCES music_tracks(id)",
        ]:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                pass
