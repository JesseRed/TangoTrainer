# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Vision

TangoTrainer is a local, Python-based training archive for tango videos. It allows creating virtual clips from long videos, tagging them with tango-specific metadata, building structured practice sessions from clips and music, and tracking training progress over time. It runs in the home network and is accessed via browser on PC, practice-room screen, and phone.

Core workflow: **Video → Clip → Bewegungsidee → Übungsmodul → Übungsstunde → Trainingsverlauf**

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Frontend:** Jinja2 templates + HTMX (no heavy JS framework), HTML5 Video player
- **Media processing:** ffmpeg (thumbnails, metadata extraction)
- **Python:** 3.10.14 via pyenv (venv at `.venv/`)

## Development Commands

```bash
# Activate venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run a single test
pytest tests/test_scanner.py::test_scan_videos -v
```

## Architecture

### Data Model

The central entities and their relationships:

- **Video** — scanned MP4 file; stores relative path (not absolute), metadata, thumbnail
- **Clip** — virtual in/out point on a Video; no new file is created; has notes, difficulty, practice_status, speed/loop defaults
- **Tag** / **ClipTag** — categorized tags (Tanztyp, Bewegung, Musikalität, Qualität, Schwierigkeit, Persönlicher Status); clips get many tags
- **Lesson** / **LessonItem** — a structured practice session; items are ordered blocks (clip, video, audio, text, pause, countdown, free-practice) each with loop/speed/pause settings
- **PracticeLog** — records each time a clip was practiced with a rating; basis for spaced-repetition suggestions
- **MusicTrack** — audio files for warm-up / free-practice blocks in lessons

### File Paths

**All paths in the database are relative to the project root**, not absolute. This allows the archive to be relocated without breaking anything. The scanner converts absolute filesystem paths to relative ones before persisting.

Example stored path: `data/videos/tango/noelia_carlitos_brussels_2015.mp4`

### Data Directory Layout

```
data/
├── videos/{tango,milonga,vals,technique}/
├── music/{tango,milonga,vals}/
├── thumbnails/
├── database/tangotrainer.sqlite
└── backups/
```

### Key Design Constraints

- No cloud dependency, no user accounts — pure local home-network app
- Videos stay as ordinary MP4 files; clips are metadata-only (virtual)
- The phone (`/remote`) controls the practice-room player (`/player`) via WebSockets
- Playback speed (50/75/90/100 %) is a first-class feature — essential for learning movement

### MVP Scope (build in order)

1. **MVP 1** — Video library: scan folder, display, stream, create clips, tag, add notes, search/filter, simple clip playlist
2. **MVP 2** — Lessons: build structured practice sessions, loop/repeat per clip, show notes during playback, fullscreen player
3. **MVP 3** — Phone remote (WebSockets), PracticeLog with ratings, spaced-repetition suggestions, music tracks
4. **MVP 4** — Auto-generated lessons, export/backup, polished UI
