TangoTrainer

Ein lokales Python-basiertes System zur Verwaltung, Analyse und Wiedergabe von Tango-Übungsvideos mit Clips, Tags, Notizen, Übungsstunden und Trainingsverlauf.

1. Grundidee

Das System soll nicht einfach Videos verwalten, sondern Tango-Lernen strukturieren.

Es soll ermöglichen:

Ich finde eine gute Stelle in einem Video.
Ich markiere sie als Clip.
Ich tagge sie: Tango / Giro / Sacada / sozial tanzbar / schwer.
Ich schreibe eine Notiz dazu.
Ich füge sie einer Übungsstunde hinzu.
Im Tanzraum spielt das System die Clips in sinnvoller Reihenfolge ab.
Danach kommt ein passendes Lied zum freien Üben.
Später erinnert mich das System daran, schwierige Sachen wieder zu üben.

Der Kern ist also:

Video → Clip → Bewegungsidee → Übungsmodul → Übungsstunde → Trainingsverlauf
2. Zielumgebung

Das System soll im Heimnetzwerk laufen.

Zentraler Server

Ein Rechner im Heimnetzwerk hostet die Anwendung, z. B.:

Mini-PC
alter Laptop
NAS mit Docker
Home-Server
Tanzraum-PC

Der Server stellt bereit:

Weboberfläche
Videodatenbank
Tags
Notizen
Übungsstunden
Trainingsverlauf
Videostreaming
Zugriff

Andere Geräte greifen per Browser zu:

Arbeitszimmer-PC: Videos vorbereiten, Clips taggen, Übungsstunden bauen
Tanzraum-PC: Übungsstunde abspielen
Handy/Tablet: Fernbedienung, Notizen, Bewertung nach Übung

Kein Cloud-Zwang. Kein Account-Zwang. Keine Abhängigkeit von MediaMonkey, Plex oder Jellyfin.

3. Kernfunktionen
3.1 Videobibliothek

Das System scannt einen oder mehrere Ordner mit MP4-Dateien.

Beispiel:

D:\TangoVideos
G:\OneDrive\Tango\Videos
\\NAS\TangoVideos

Für jedes Video werden gespeichert:

Dateipfad
Titel
Dateiname
Dauer
Auflösung
Thumbnail
Tänzer
Event
Jahr
Tanztyp
Kommentar
Status

Wichtig: Der Dateipfad sollte serverseitig zentral gelten. Die anderen Geräte müssen die Datei nicht direkt über Laufwerksbuchstaben kennen. Sie bekommen das Video über den Server.

Damit wäre dein altes [Volume]-Problem weg.

3.2 Virtuelle Clips

Ein Clip ist ein Ausschnitt aus einem Video, ohne dass eine neue MP4-Datei erzeugt werden muss.

Beispiel:

Video: Noelia Hurtado y Carlitos Espinoza, Brussels 2015
Clip: 00:34–00:48
Titel: "weicher Giro mit Sacada"
Tags: Tango, Giro, Sacada, Musikalität, schwer
Notiz: "Nicht die Figur kopieren, sondern das Timing und die Rotation ansehen."

Ein Video kann beliebig viele Clips enthalten.

Ein Clip braucht mindestens:

video_id
start_time
end_time
title
notes
tags
difficulty
practice_status

Optional:

loop_count
default_speed
pause_after_clip
mirror_note
focus_for_leader
focus_for_follower
3.3 Tagsystem

Tags sind zentral. Aber sie sollten nicht einfach nur eine flache Liste sein, sondern Kategorien haben.

Tag-Kategorien
Tanztyp
Tango
Milonga
Vals
Neo
Technik
Show
Unterricht
Bewegung
Ocho
Giro
Sacada
Boleo
Barrida
Parada
Sandwich
Calesita
Volcada
Colgada
Enrosque
Planeo
Gancho
Musikalität
Pause
Synkope
Rhythmus
Melodie
Phrasierung
Akzent
Dynamikwechsel
langsam
schnell
Traspie
Qualität
sozial tanzbar
showartig
eng
offen
klein
groß
weich
rhythmisch
dramatisch
elegant
verspielt
Schwierigkeit
leicht
mittel
schwer
sehr schwer
später
Persönlicher Status
wollen wir lernen
haben wir geübt
klappt noch nicht
läuft gut
Lieblingssequenz
für Unterricht
für Milonga ungeeignet

Das Schöne: Du kannst später nach sehr präzisen Kombinationen suchen:

Milonga + Traspie + sozial tanzbar + mittel
Vals + Giro + elegant + leicht
Tango + Sacada + schwer + Lieblingssequenz
4. Notizen und Bewegungsanalyse

Das System soll Notizen nicht nur zum ganzen Video speichern, sondern direkt zu Clips und optional zu Zeitpunkten.

Clip-Notizen

Beispiel:

Der eigentliche Trick ist nicht die Sacada, sondern dass er ihre Rotation schon vorher vorbereitet.
Für uns: kleiner tanzen, nicht so stark öffnen.
Zeitcodierte Notizen

Beispiel:

00:03
Er reduziert die Schrittgröße deutlich.

00:06
Sie bleibt länger auf der Achse als erwartet.

00:10
Hier entsteht die Sacada fast aus der Rotation, nicht aus einem großen Schritt.
Getrennte Notizfelder

Sinnvoll wären mehrere Felder:

Was sieht man?
Was ist die technische Idee?
Worauf muss ich achten?
Worauf muss meine Frau achten?
Was ist für uns anzupassen?
Ist das sozial tanzbar?
Welche Fehler machen wir dabei?

Das ist einer der stärksten Eigenbau-Vorteile.

5. Übungsstunden

Das ist der zentrale Killer-Use-Case.

Eine Übungsstunde besteht nicht nur aus einer Playlist, sondern aus Trainingsblöcken.

Beispielstruktur
Übungsstunde: Milonga 30 Minuten

1. Warm-up
   - Lied: Donato - Ella Es Así
   - Dauer: 3 min

2. Technikblock
   - Clip: Traspie Basic 1
   - 5 Wiederholungen
   - Geschwindigkeit: 80 %
   - Pause: 15 Sekunden
   - Notiz anzeigen

3. Inspirationsblock
   - Clip: Carlitos Milonga Phrase
   - 3 Wiederholungen
   - Originalgeschwindigkeit

4. Freies Üben
   - Lied: Milonga Sentimental
   - Dauer: ganzes Lied

5. Wiederholung schwieriger Sequenz
   - Clip: Traspie Wechsel
   - 5 Wiederholungen
   - danach Bewertung: klappt / unsicher / später nochmal
Bestandteile einer Übungsstunde

Eine Übungsstunde kann enthalten:

Videoclip
ganzes Video
Audiodatei / Musikstück
Textanweisung
Pause
Countdown
freies Üben
Bewertungsfrage
Wiederholungsblock

Damit wird aus einer Playlist eine echte Trainingseinheit.

6. Abspielmodus

Der Tanzraum braucht einen sehr einfachen Modus.

Bildschirmansicht

Großer Bildschirm zeigt:

aktueller Clip
Titel
Tags
Notiz
Start/Ende
Wiederholung 2 von 5
nächster Block

Optional:

"Jetzt selbst üben"
Countdown 20 Sekunden
"Danach: Musikstück zum freien Tanzen"
Wiedergabeoptionen

Pro Clip oder Block:

einmal abspielen
x-mal wiederholen
Loop bis manuell weiter
Pause nach Clip
Abspielgeschwindigkeit 50/75/90/100 %
Ton an/aus
Fullscreen

Gerade Geschwindigkeit ist wichtig: manche Bewegungen will man erst in 70 % sehen.

7. Handy als Fernbedienung

Das wäre richtig stark.

Der Tanzraum-PC öffnet:

http://tangotrainer.local/player

Das Handy öffnet:

http://tangotrainer.local/remote

Dann kannst du am Handy steuern:

Start
Pause
Nochmal
Nächster Clip
Vorheriger Clip
Langsamer
Schneller
Loop an/aus
Notiz anzeigen
als schwierig markieren
als verstanden markieren
kurze Notiz diktieren/schreiben

Technisch später ideal über WebSockets.

Das Handy wäre also nicht nur Fernbedienung, sondern auch Trainingstagebuch.

8. Trainingsverlauf und Wiederholungssystem

Das System merkt sich, was ihr geübt habt.

Für jeden Clip:

zuletzt geübt
wie oft geübt
Bewertung
nächste Wiederholung
Kommentar nach dem Üben

Bewertung nach jedem Clip oder Block:

klappt gut
noch unsicher
gar nicht verstanden
später nochmal
Lieblingsclip
nicht mehr relevant

Daraus kann das System automatisch Vorschläge machen:

Heute vorgeschlagen:
- 2 Clips, die ihr letzte Woche als "unsicher" markiert habt
- 1 neuer Clip aus "Vals + leicht"
- 1 Lieblingsclip zum Abschluss

Das ist wie ein leichtes Spaced-Repetition-System für Bewegungen.

9. Intelligenter Übungsstunden-Generator

Später könnte das System automatisch Übungsstunden bauen.

Beispiel:

Erstelle 45 Minuten Tango mit:
- 10 Minuten Warm-up
- Fokus: Giro und Ocho
- Schwierigkeit: mittel
- mindestens ein langsames Lied
- am Ende 10 Minuten freies Üben

Oder:

Heute nur Milonga, maximal 30 Minuten, keine schweren Showfiguren.

Oder:

Zeige uns Sachen, die wir lange nicht geübt haben.

Dafür braucht man anfangs keine KI. Das geht regelbasiert über Tags, Dauer, Schwierigkeit und Trainingsverlauf.

10. Suche und Filter

Die Suche muss sehr stark sein.

Suche nach Text
Carlitos
Noelia
Brussels
Sacada
Ocho cortado
Traspie
Filter
Tanztyp
Tänzer
Event
Jahr
Schwierigkeit
Tags
Status
zuletzt geübt
Dauer
sozial tanzbar ja/nein
Lieblingssequenzen
Gespeicherte Suchen

Beispiele:

Milonga für heute
Vals leicht
Schwierige Sachen wiederholen
Sozial tanzbare Sacadas
Lieblingsclips unter 20 Sekunden
11. Datenmodell grob
Tabelle: Video
id
filepath
filename
title
duration
thumbnail_path
dancer_1
dancer_2
event
year
source_url
description
created_at
updated_at
Tabelle: Clip
id
video_id
title
start_seconds
end_seconds
notes
technical_notes
leader_notes
follower_notes
adaptation_notes
difficulty
practice_status
default_speed
default_loop_count
pause_after_seconds
created_at
updated_at
Tabelle: Tag
id
name
category
color
Tabelle: ClipTag
clip_id
tag_id
Tabelle: Lesson
id
title
description
goal
planned_duration
created_at
updated_at
Tabelle: LessonItem
id
lesson_id
item_type
clip_id
video_id
audio_id
text_instruction
order_index
loop_count
speed
pause_after_seconds
show_notes
duration_override
Tabelle: PracticeLog
id
clip_id
lesson_id
date
rating
comment
practiced_count
next_review_date
Tabelle: MusicTrack
id
filepath
title
orchestra
singer
year
dance_type
duration
bpm
mood
notes

Sehr wichtig: Musik sollte als eigener Objekttyp gedacht werden. Eine Übungsstunde braucht nicht nur Videos, sondern auch passende Lieder.

12. Technische Architektur
Empfehlung
Backend: Python
Webframework: FastAPI oder Flask
Datenbank: SQLite
Frontend: HTML + HTMX oder kleines React/Vue später
Videoplayer: HTML5 Video
Metadaten/Thumbnails: ffmpeg
Deployment: Docker optional

Für den Anfang würde ich es bewusst einfach halten:

FastAPI + SQLite + Jinja2/HTMX + HTML5 Video

Warum?

Python bleibt zentral.
SQLite reicht für 1000 bis 10000 Videos locker.
Kein schweres Frontend am Anfang.
Läuft lokal im Heimnetz.
Sehr gut später erweiterbar.
Komponenten
1. Scanner
   findet Videos und aktualisiert Datenbank

2. Metadata Service
   liest Dauer, Auflösung, Thumbnails

3. Web-App
   Bibliothek, Clips, Tags, Übungsstunden

4. Player
   spielt Clips mit Start/Ende, Loop, Speed

5. Remote Control
   Handy steuert Tanzraum-Player

6. Practice Engine
   merkt sich Bewertungen und schlägt Wiederholungen vor

7. Backup/Export
   exportiert Datenbank als JSON/CSV
13. Dateiorganisation

Die Videos sollten normal im Dateisystem bleiben.

Beispiel:

TangoArchive/
├── videos/
│   ├── tango/
│   ├── milonga/
│   ├── vals/
│   └── technique/
├── music/
│   ├── tango/
│   ├── milonga/
│   └── vals/
├── thumbnails/
├── database/
│   └── tangotrainer.sqlite
└── backups/

Wichtig: Die Datenbank speichert Pfade relativ zum Archiv-Root, nicht hart als G:\....

Also besser:

videos/tango/noelia_carlitos_brussels_2015.mp4

statt:

G:\OneDrive\Tango\Videos\...

Dann kann das Archiv später umziehen, ohne kaputtzugehen.

14. MVP — erste sinnvolle Version

Die erste Version sollte nicht alles können. Aber sie muss sofort echten Nutzen haben.

MVP 1
Videos aus Ordner scannen
Videos im Browser anzeigen
Video abspielen
Clip mit Start- und Endzeit anlegen
Clip benennen
Tags vergeben
Notiz speichern
Clips suchen/filtern
einfache Clip-Playlist abspielen

Das wäre schon ein echter Durchbruch.

MVP 2
Übungsstunden erstellen
Clips in Reihenfolge sortieren
Loop/Wiederholungen pro Clip
Pause nach Clip
Notizen beim Abspielen anzeigen
Tanzraum-Player im Vollbild
MVP 3
Handy-Fernbedienung
Trainingsbewertung
PracticeLog
Vorschläge für Wiederholung
Musikstücke einbinden
MVP 4
automatische Übungsstunden
Spaced Repetition
BPM/Mood für Musik
Export/Import
Backup
schöne Oberfläche
15. Beispiel-Workflow
Vorbereitung am Arbeitszimmer-PC
1. Neues Video wird automatisch erkannt.
2. Du öffnest es im Browser.
3. Du springst zu einer interessanten Stelle.
4. Du drückst "Clip Start".
5. Du drückst "Clip Ende".
6. Du gibst Titel und Tags ein.
7. Du schreibst eine Notiz:
   "Gute kleine Sacada, sozial tanzbar, für uns langsamer üben."
8. Du fügst den Clip zur Übungsstunde "Tango Sonntag" hinzu.
Im Tanzraum
1. Tanzraum-PC öffnet Übungsstunde.
2. Handy verbindet sich als Fernbedienung.
3. System spielt Warm-up-Lied.
4. Danach Clip 1 dreimal langsam.
5. Dann 20 Sekunden Pause.
6. Dann Clip 1 in Originalgeschwindigkeit.
7. Dann passende Musik zum freien Üben.
8. Danach fragt das System:
   "Wie lief es?"
9. Du markierst: "noch unsicher".
10. Der Clip wird für nächste Woche vorgeschlagen.

Genau das wäre der Unterschied zwischen Mediaplayer und Trainingssystem.

16. Nicht-funktionale Anforderungen
Muss
läuft komplett lokal im Heimnetzwerk
funktioniert im Browser
keine Cloud-Abhängigkeit
Videos bleiben als normale MP4-Dateien erhalten
Datenbank exportierbar
robuste Backups
relative Pfade
schnelles Suchen und Filtern
einfache Bedienung im Tanzraum
Sollte
Handy-Fernbedienung
Vollbildmodus
gute Thumbnail-Ansicht
Tags schnell vergebbar
Tastenkürzel zum Clip-Markieren
mehrere Übungsstunden
Trainingsverlauf
Kann später
KI-gestützte automatische Tag-Vorschläge
Pose-Erkennung
automatische Szenenerkennung
BPM-Erkennung bei Musik
YouTube-Link-Verwaltung
Export von echten MP4-Clips
Anki-artige Wiederholungslogik
mehrere Benutzerprofile
17. Was explizit nicht Ziel der ersten Version ist

Wichtig, damit das Projekt nicht explodiert:

kein perfekter Plex-Ersatz
keine komplexe Benutzerverwaltung
kein Internet-Streaming
keine Smartphone-App
keine automatische Bewegungserkennung am Anfang
kein schönes Netflix-Design als Priorität

Erst Funktion, dann Schönheit.

18. Meine empfohlene Projektvision

Ich würde das Ziel so formulieren:

TangoTrainer ist ein lokales, Python-basiertes Trainingsarchiv für Tango-Videos. Es ermöglicht, aus langen Videos kurze virtuelle Clips zu erstellen, diese mit Tango-spezifischen Tags und Notizen zu versehen, daraus strukturierte Übungsstunden mit Video- und Musikblöcken zu bauen und den Trainingsfortschritt über die Zeit zu verfolgen. Die Anwendung läuft im Heimnetzwerk und wird über Browser auf PC, Tanzraum-Bildschirm und Handy bedient.

Das ist stark.
Das ist klar.
Und das ist sehr gut schrittweise baubar.