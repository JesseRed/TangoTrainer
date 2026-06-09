from sqlalchemy.orm import Session
from app.models import Tag

SEED_TAGS = [
    # Tanztyp
    ("Tango", "Tanztyp", "#dc2626"),
    ("Milonga", "Tanztyp", "#ea580c"),
    ("Vals", "Tanztyp", "#d97706"),
    ("Neo", "Tanztyp", "#65a30d"),
    ("Technik", "Tanztyp", "#0891b2"),
    ("Show", "Tanztyp", "#7c3aed"),
    ("Unterricht", "Tanztyp", "#db2777"),
    # Bewegung
    ("Ocho", "Bewegung", "#2563eb"),
    ("Vorwärts-Ocho", "Bewegung", "#2563eb"),
    ("Rückwärts-Ocho", "Bewegung", "#2563eb"),
    ("Giro", "Bewegung", "#2563eb"),
    ("Sacada", "Bewegung", "#2563eb"),
    ("Boleo", "Bewegung", "#2563eb"),
    ("Barrida", "Bewegung", "#2563eb"),
    ("Parada", "Bewegung", "#2563eb"),
    ("Sandwich", "Bewegung", "#2563eb"),
    ("Calesita", "Bewegung", "#2563eb"),
    ("Volcada", "Bewegung", "#2563eb"),
    ("Colgada", "Bewegung", "#2563eb"),
    ("Enrosque", "Bewegung", "#2563eb"),
    ("Planeo", "Bewegung", "#2563eb"),
    ("Gancho", "Bewegung", "#2563eb"),
    # Bewegungsphase
    ("Eingang", "Bewegungsphase", "#7c3aed"),
    ("Bewegung selbst", "Bewegungsphase", "#7c3aed"),
    ("Ausgang", "Bewegungsphase", "#7c3aed"),
    # Musikalität
    ("Pause", "Musikalität", "#059669"),
    ("Synkope", "Musikalität", "#059669"),
    ("Rhythmus", "Musikalität", "#059669"),
    ("Melodie", "Musikalität", "#059669"),
    ("Phrasierung", "Musikalität", "#059669"),
    ("Akzent", "Musikalität", "#059669"),
    ("Dynamikwechsel", "Musikalität", "#059669"),
    ("langsam", "Musikalität", "#059669"),
    ("schnell", "Musikalität", "#059669"),
    ("Traspie", "Musikalität", "#059669"),
    # Qualität
    ("sozial tanzbar", "Qualität", "#0284c7"),
    ("showartig", "Qualität", "#0284c7"),
    ("eng", "Qualität", "#0284c7"),
    ("offen", "Qualität", "#0284c7"),
    ("klein", "Qualität", "#0284c7"),
    ("groß", "Qualität", "#0284c7"),
    ("weich", "Qualität", "#0284c7"),
    ("rhythmisch", "Qualität", "#0284c7"),
    ("dramatisch", "Qualität", "#0284c7"),
    ("elegant", "Qualität", "#0284c7"),
    ("verspielt", "Qualität", "#0284c7"),
    # Schwierigkeit
    ("leicht", "Schwierigkeit", "#16a34a"),
    ("mittel", "Schwierigkeit", "#ca8a04"),
    ("schwer", "Schwierigkeit", "#dc2626"),
    ("sehr schwer", "Schwierigkeit", "#991b1b"),
    ("später", "Schwierigkeit", "#6b7280"),
    # Persönlicher Status
    ("wollen wir lernen", "Persönlicher Status", "#8b5cf6"),
    ("haben wir geübt", "Persönlicher Status", "#8b5cf6"),
    ("klappt noch nicht", "Persönlicher Status", "#8b5cf6"),
    ("läuft gut", "Persönlicher Status", "#8b5cf6"),
    ("Lieblingssequenz", "Persönlicher Status", "#8b5cf6"),
    ("für Unterricht", "Persönlicher Status", "#8b5cf6"),
    ("für Milonga ungeeignet", "Persönlicher Status", "#8b5cf6"),
]


def seed_tags(db: Session) -> None:
    existing = {(t.name, t.category) for t in db.query(Tag).all()}
    added = False
    for name, category, color in SEED_TAGS:
        if (name, category) not in existing:
            db.add(Tag(name=name, category=category, color=color))
            added = True
    if added:
        db.commit()
