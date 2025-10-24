from __future__ import annotations
from fastapi import FastAPI, HTTPException, Depends
from typing import Iterator, Optional, List
from pathlib import Path
import os, csv

from sqlalchemy import create_engine, Integer, String, Float
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import Session

# Konfiguracja bazy
DB_URL = os.getenv("DB_URL", "sqlite:///./app.db")  # zmień przez env jeśli chcesz
engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

# Modele ORM (SQLite)
class Movie(Base):
    __tablename__ = "movies"
    movieId: Mapped[int] = mapped_column(Integer, primary_key=True)
    title:   Mapped[str] = mapped_column(String)
    genres:  Mapped[str] = mapped_column(String)

class Link(Base):
    __tablename__ = "links"
    movieId: Mapped[int] = mapped_column(Integer, primary_key=True)
    imdbId:  Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tmdbId:  Mapped[Optional[str]] = mapped_column(String, nullable=True)

class Rating(Base):
    __tablename__ = "ratings"
    userId:    Mapped[int] = mapped_column(Integer, primary_key=True)
    movieId:   Mapped[int] = mapped_column(Integer, primary_key=True)
    rating:    Mapped[float] = mapped_column(Float)
    timestamp: Mapped[int] = mapped_column(Integer)

class Tag(Base):
    __tablename__ = "tags"
    userId:    Mapped[int] = mapped_column(Integer, primary_key=True)
    movieId:   Mapped[int] = mapped_column(Integer, primary_key=True)
    tag:       Mapped[str] = mapped_column(String)
    timestamp: Mapped[int] = mapped_column(Integer)

# FastAPI
app = FastAPI(title="Movies API (FastAPI + SQLAlchemy + SQLite)")

#Dependency do sesji DB

def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Tworzenie tabel przy starcie
@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)
    # opcjonalny auto-import CSV, jeśli puste tabele i istnieją pliki w ./data
    data_dir = Path(os.getenv("DATA_DIR", "data")).resolve()
    try:
        with SessionLocal() as db:
            # jeśli któraś tabela jest pusta i mamy CSV, załaduj
            is_empty = (db.query(Movie).count() == 0
                        and db.query(Link).count() == 0
                        and db.query(Rating).count() == 0
                        and db.query(Tag).count() == 0)
            if is_empty and (data_dir / "movies.csv").exists():
                _load_all_csvs(db, data_dir)
    except Exception:
        # nie blokuj startu jeśli import się nie uda; użytkownik może użyć /load
        pass

@app.get("/hello")
async def hello():
    return {"hello": "world"}

#Import CSV -> SQLite


def _load_all_csvs(db: Session, data_dir: Path) -> None:
    # Movies
    with (data_dir / "movies.csv").open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [Movie(movieId=int(r['movieId']), title=r['title'], genres=r['genres']) for r in reader]
    db.query(Movie).delete()
    db.bulk_save_objects(rows)

    #Links
    with (data_dir / "links.csv").open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [Link(movieId=int(r['movieId']), imdbId=r.get('imdbId') or None, tmdbId=r.get('tmdbId') or None) for r in reader]
    db.query(Link).delete()
    db.bulk_save_objects(rows)

    #Ratings
    with (data_dir / "ratings.csv").open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [Rating(userId=int(r['userId']), movieId=int(r['movieId']), rating=float(r['rating']), timestamp=int(r['timestamp'])) for r in reader]
    db.query(Rating).delete()
    # batch insert w porcjach, bo ratings bywa duże
    BATCH = 100_000
    for i in range(0, len(rows), BATCH):
        db.bulk_save_objects(rows[i:i+BATCH])

    #Tags
    with (data_dir / "tags.csv").open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [Tag(userId=int(r['userId']), movieId=int(r['movieId']), tag=r['tag'], timestamp=int(r['timestamp'])) for r in reader]
    db.query(Tag).delete()
    db.bulk_save_objects(rows)

    db.commit()

@app.post("/load")
async def load_data(db: Session = Depends(get_db)):
    data_dir = Path(os.getenv("DATA_DIR", "data")).resolve()
    required = [data_dir / "movies.csv", data_dir / "links.csv", data_dir / "ratings.csv", data_dir / "tags.csv"]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise HTTPException(status_code=400, detail={"error": "Brak plików CSV", "missing": missing})
    _load_all_csvs(db, data_dir)
    return {"status": "ok", "message": "Załadowano CSV do SQLite"}

# serializacja i paginacja

def to_dict(obj) -> dict:
    if isinstance(obj, Movie):
        return {"movieId": obj.movieId, "title": obj.title, "genres": obj.genres}
    if isinstance(obj, Link):
        return {"movieId": obj.movieId, "imdbId": obj.imdbId, "tmdbId": obj.tmdbId}
    if isinstance(obj, Rating):
        return {"userId": obj.userId, "movieId": obj.movieId, "rating": obj.rating, "timestamp": obj.timestamp}
    if isinstance(obj, Tag):
        return {"userId": obj.userId, "movieId": obj.movieId, "tag": obj.tag, "timestamp": obj.timestamp}
    return {}

def paginate(query, limit: Optional[int], offset: Optional[int]):
    off = max(0, offset or 0)
    if limit is None:
        return query.offset(off).all()
    return query.offset(off).limit(max(0, limit)).all()

#Endpointy danych (SQLAlchemy)

@app.get("/movies")
async def get_movies(limit: int | None = None, offset: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Movie).order_by(Movie.movieId)
    return [to_dict(m) for m in paginate(q, limit, offset)]

@app.get("/links")
async def get_links(limit: int | None = None, offset: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Link).order_by(Link.movieId)
    return [to_dict(x) for x in paginate(q, limit, offset)]

@app.get("/ratings")
async def get_ratings(limit: int | None = 1000, offset: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Rating).order_by(Rating.userId, Rating.movieId)
    return [to_dict(x) for x in paginate(q, limit, offset)]

@app.get("/tags")
async def get_tags(limit: int | None = None, offset: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Tag).order_by(Tag.userId, Tag.movieId)
    return [to_dict(x) for x in paginate(q, limit, offset)]

@app.get("/stats")
async def stats(db: Session = Depends(get_db)):
    return {
        "movies": db.query(Movie).count(),
        "links": db.query(Link).count(),
        "ratings": db.query(Rating).count(),
        "tags": db.query(Tag).count(),
        "db_url": DB_URL,
    }
