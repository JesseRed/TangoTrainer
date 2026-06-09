# TangoTrainer

Lokales, Python-basiertes Trainingsarchiv für Tango-Videos. Läuft im Heimnetzwerk, wird über den Browser bedient — auf PC, Tanzraum-Bildschirm und Handy.

**Kernidee:** Aus langen Videos kurze virtuelle Clips erstellen, mit Tango-spezifischen Tags und Notizen versehen, daraus strukturierte Übungsstunden bauen und den Trainingsfortschritt verfolgen.

---

## Voraussetzungen

- Python 3.10+ (empfohlen via [pyenv](https://github.com/pyenv/pyenv))
- `ffmpeg` und `ffprobe` im System-PATH (für Thumbnails und Metadaten)

---

## Installation

```bash
# Repository klonen oder entpacken, dann ins Verzeichnis wechseln
cd TangoTrainer

# Virtuelle Umgebung anlegen (Python 3.10)
~/.pyenv/versions/3.10.14/bin/python3 -m venv .venv

# Aktivieren
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt
```

---

## Server starten

```bash
source .venv/bin/activate
python run.py
```

Der Server läuft dann auf **http://localhost:8000** und ist im Heimnetzwerk unter **http://\<server-ip\>:8000** erreichbar.

Beim ersten Start werden automatisch:
- die SQLite-Datenbank unter `data/database/tangotrainer.sqlite` angelegt
- ~50 vordefinierte Tags (Tanztyp, Bewegung, Musikalität, Qualität, Schwierigkeit, Persönlicher Status) eingespielt

---

## Videos einrichten

### Option A — Videos in den Projektordner legen

```
data/videos/tango/
data/videos/milonga/
data/videos/vals/
data/videos/technique/
```

Unterstützte Formate: `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`

### Option B — Externe Ordner einbinden (NAS, andere Festplatten)

1. Unter **Einstellungen** → Ordner-Pfad eintragen (z. B. `/mnt/nas/TangoArchive`)
2. Netzlaufwerke vorher per OS einbinden (SMB/NFS-Mount), dann den lokalen Mount-Pfad eintragen

Nach dem Einrichten: In der **Bibliothek** auf **„Jetzt scannen"** klicken.

---

## Bedienung

### Bibliothek (`/`)

Alle gescannten Videos als Thumbnail-Raster. „Jetzt scannen" findet neue Dateien.

### Clip anlegen (`/videos/{id}`)

1. Video öffnen
2. An die gewünschte Stelle springen
3. **„Start setzen"** drücken (oder Taste `S`)
4. Clip weiterlaufen lassen
5. **„Ende setzen"** drücken (oder Taste `E`)
6. Titel, Schwierigkeit und Notizen ausfüllen
7. Speichern → danach direkt Tags vergeben

### Clips-Übersicht (`/clips`)

- Volltextsuche über Titel und Notizen
- Filter nach Schwierigkeit und Tag
- Clips für eine Übungsstunde markieren: **Checkboxen** anklicken → floating Leiste erscheint → Stunde wählen oder neu anlegen

### Übungsstunden (`/lessons`)

1. **„Neue Stunde"** anlegen (Titel, Ziel, Dauer)
2. Auf der Clips-Seite Clips markieren → zur Stunde hinzufügen
3. Im Editor:
   - **↑ / ↓** zum Umsortieren
   - Pro Block: Wiederholungen, Geschwindigkeit (%), Pause danach (s), Notizen ein/aus
   - **„Textanweisung hinzufügen"** für Blöcke ohne Video (z. B. „Jetzt selbst üben")
4. **„▶ Starten"** öffnet den Tanzraum-Player

### Player (`/player/lesson/{id}`)

| Taste | Funktion |
|---|---|
| `Space` | Play / Pause |
| `→` | Nächster Block |
| `←` | Vorheriger Block |
| `R` | Aktuellen Block nochmal abspielen |
| `F` | Vollbild ein/aus |

- Clip spielt automatisch N-mal (Wiederholungen), danach Pause-Countdown, dann weiter
- Loop-Counter zeigt „Wiederholung 2 von 3"
- Notizen klappen auf wenn „Notiz anzeigen" aktiv
- Geschwindigkeit über Dropdown (50 / 75 / 90 / 100 %)

---

## Projektstruktur

```
TangoTrainer/
├── app/
│   ├── main.py              # FastAPI-App, Startup
│   ├── models.py            # Datenbankmodelle
│   ├── database.py          # SQLAlchemy-Setup
│   ├── seed.py              # Vordefiniete Tags
│   ├── routers/
│   │   ├── videos.py        # Bibliothek, Streaming
│   │   ├── clips.py         # Clip-CRUD, Suche
│   │   ├── lessons.py       # Übungsstunden-CRUD
│   │   ├── player.py        # Player-Routen
│   │   ├── tags.py          # Tag-Verwaltung
│   │   └── settings.py      # Scan-Ordner
│   ├── services/
│   │   └── scanner.py       # ffprobe, Thumbnails, Scan
│   ├── templates/           # Jinja2-HTML-Templates
│   └── static/
│       ├── css/style.css
│       └── js/
│           ├── clip_editor.js   # Start/Ende-Marking
│           ├── clip_select.js   # Checkbox-Auswahl
│           └── player.js        # Player-Logik
├── data/
│   ├── videos/              # Videodateien (oder per Einstellungen konfiguriert)
│   ├── music/               # Musikdateien (MVP 3)
│   ├── thumbnails/          # Auto-generierte Thumbnails
│   ├── database/            # tangotrainer.sqlite
│   └── backups/
├── config.py                # Pfade, Dateiendungen
├── run.py                   # Einstiegspunkt
└── requirements.txt
```

---

## Tech Stack

| Komponente | Technologie |
|---|---|
| Backend | Python, FastAPI |
| Datenbank | SQLite via SQLAlchemy |
| Frontend | Jinja2-Templates, HTMX, Vanilla JS |
| Videoplayer | HTML5 `<video>` mit HTTP Range Requests |
| Thumbnails | ffmpeg / ffprobe |

---

## MVP-Fahrplan

- **MVP 1** ✅ — Bibliothek, Clips, Tags, Notizen, Suche, einfache Playlist
- **MVP 2** ✅ — Übungsstunden, Loop/Pause/Speed, Vollbild-Player, Textanweisungen
- **MVP 3** — Handy-Fernbedienung (WebSockets), PracticeLog mit Bewertungen, Musikstücke
- **MVP 4** — Automatische Stunden-Generierung, Spaced Repetition, Export/Backup
