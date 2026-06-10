from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Table
from sqlalchemy.orm import relationship
from app.database import Base

clip_tags = Table(
    "clip_tags",
    Base.metadata,
    Column("clip_id", Integer, ForeignKey("clips.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filepath = Column(String, unique=True, nullable=False)  # relative to project root
    filename = Column(String, nullable=False)
    title = Column(String, nullable=False)
    duration = Column(Float)
    thumbnail_path = Column(String)
    dancer_1 = Column(String)
    dancer_2 = Column(String)
    event = Column(String)
    year = Column(Integer)
    source_url = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    clips = relationship("Clip", back_populates="video", cascade="all, delete-orphan")


class Clip(Base):
    __tablename__ = "clips"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    title = Column(String, nullable=False)
    start_seconds = Column(Float, nullable=False)
    end_seconds = Column(Float, nullable=False)
    notes = Column(Text)
    technical_notes = Column(Text)
    leader_notes = Column(Text)
    follower_notes = Column(Text)
    adaptation_notes = Column(Text)
    difficulty = Column(String)
    practice_status = Column(String)
    thumbnail_path = Column(String)
    default_speed = Column(Float, default=1.0)
    default_loop_count = Column(Integer, default=1)
    pause_after_seconds = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    video = relationship("Video", back_populates="clips")
    tags = relationship("Tag", secondary=clip_tags, back_populates="clips")
    practice_logs = relationship("PracticeLog", back_populates="clip")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    color = Column(String, default="#6b7280")

    clips = relationship("Clip", secondary=clip_tags, back_populates="tags")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    goal = Column(Text)
    planned_duration = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship(
        "LessonItem",
        back_populates="lesson",
        order_by="LessonItem.order_index",
        cascade="all, delete-orphan",
    )


class LessonItem(Base):
    __tablename__ = "lesson_items"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    item_type = Column(String, nullable=False)
    clip_id = Column(Integer, ForeignKey("clips.id"), nullable=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=True)
    audio_id = Column(Integer, ForeignKey("music_tracks.id"), nullable=True)
    text_instruction = Column(Text)
    order_index = Column(Integer, nullable=False)
    loop_count = Column(Integer, default=1)
    speed = Column(Float, default=1.0)
    pause_after_seconds = Column(Integer, default=0)
    show_notes = Column(Integer, default=1)
    duration_override = Column(Integer)

    lesson = relationship("Lesson", back_populates="items")
    clip = relationship("Clip")
    video = relationship("Video")
    audio = relationship("MusicTrack")


class PracticeLog(Base):
    __tablename__ = "practice_logs"

    id = Column(Integer, primary_key=True, index=True)
    clip_id = Column(Integer, ForeignKey("clips.id"), nullable=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    rating = Column(String)
    comment = Column(Text)
    practiced_count = Column(Integer, default=1)
    next_review_date = Column(DateTime)

    clip = relationship("Clip", back_populates="practice_logs")


class MusicTrack(Base):
    __tablename__ = "music_tracks"

    id = Column(Integer, primary_key=True, index=True)
    filepath = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    orchestra = Column(String)
    singer = Column(String)
    year = Column(Integer)
    dance_type = Column(String)
    duration = Column(Float)
    bpm = Column(Integer)
    mood = Column(String)
    notes = Column(Text)


class WatchDir(Base):
    __tablename__ = "watch_dirs"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, nullable=False)
    label = Column(String)
    active = Column(Integer, default=1)  # 1 = aktiv, 0 = deaktiviert


class Tanda(Base):
    __tablename__ = "tandas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    dance_type = Column(String, nullable=False)  # tango, milonga, vals
    notes = Column(Text)

    tracks = relationship(
        "TandaTrack",
        back_populates="tanda",
        order_by="TandaTrack.order_index",
        cascade="all, delete-orphan",
    )


class TandaTrack(Base):
    __tablename__ = "tanda_tracks"

    id = Column(Integer, primary_key=True, index=True)
    tanda_id = Column(Integer, ForeignKey("tandas.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("music_tracks.id"), nullable=False)
    order_index = Column(Integer, nullable=False)

    tanda = relationship("Tanda", back_populates="tracks")
    track = relationship("MusicTrack")


class MusicPlaylist(Base):
    __tablename__ = "music_playlists"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    playlist_type = Column(String, nullable=False)  # "fixed" | "tanda"
    notes = Column(Text)
    repeat_count = Column(Integer, default=3)

    playlist_tracks = relationship(
        "PlaylistTrack",
        back_populates="playlist",
        order_by="PlaylistTrack.order_index",
        cascade="all, delete-orphan",
    )
    pattern = relationship(
        "PlaylistPattern",
        back_populates="playlist",
        order_by="PlaylistPattern.order_index",
        cascade="all, delete-orphan",
    )


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("music_playlists.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("music_tracks.id"), nullable=False)
    order_index = Column(Integer, nullable=False)

    playlist = relationship("MusicPlaylist", back_populates="playlist_tracks")
    track = relationship("MusicTrack")


class PlaylistPattern(Base):
    __tablename__ = "playlist_patterns"

    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("music_playlists.id"), nullable=False)
    dance_type = Column(String, nullable=False)  # tango, milonga, vals
    count = Column(Integer, nullable=False, default=1)
    order_index = Column(Integer, nullable=False)

    playlist = relationship("MusicPlaylist", back_populates="pattern")
