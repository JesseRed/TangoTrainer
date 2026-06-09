from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
VIDEOS_DIR = DATA_DIR / "videos"
MUSIC_DIR = DATA_DIR / "music"
THUMBNAILS_DIR = DATA_DIR / "thumbnails"
DATABASE_DIR = DATA_DIR / "database"
BACKUPS_DIR = DATA_DIR / "backups"

DATABASE_URL = f"sqlite:///{DATABASE_DIR}/tangotrainer.sqlite"

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm"}
MUSIC_EXTENSIONS = {".mp3", ".flac", ".ogg", ".m4a", ".wav"}
