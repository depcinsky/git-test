from fastapi import FastAPI, HTTPException
from typing import List, Optional
import csv
from pathlib import Path
import os

app = FastAPI(title="Movies API (FastAPI)")

#Model danych
class Movie:
    def __init__(self, movieId: int, title: str, genres: str):
        self.movieId = int(movieId)
        self.title = title
        self.genres = genres

class Link:
    def __init__(self, movieId: int, imdbId: str, tmdbId: str):
        self.movieId = int(movieId)
        self.imdbId = imdbId
        self.tmdbId = tmdbId

class Rating:
    def __init__(self, userId: int, movieId: int, rating: float, timestamp: int):
        self.userId = int(userId)
        self.movieId = int(movieId)
        self.rating = float(rating)
        self.timestamp = int(timestamp)

class Tag:
    def __init__(self, userId: int, movieId: int, tag: str, timestamp: int):
        self.userId = int(userId)
        self.movieId = int(movieId)
        self.tag = tag
        self.timestamp = int(timestamp)

#Ścieżki do danych
DATA_DIR = Path(os.getenv("DATA_DIR", "data")).resolve()
MOVIES_CSV = DATA_DIR / "movies.csv"
LINKS_CSV  = DATA_DIR / "links.csv"
RATINGS_CSV = DATA_DIR / "ratings.csv"
TAGS_CSV   = DATA_DIR / "tags.csv"

#Bufory
_movies: List[Movie] = []
_links: List[Link] = []
_ratings: List[Rating] = []
_tags: List[Tag] = []

def _require_file_exists(p: Path):
    if not p.exists():
        raise FileNotFoundError(f"Brak pliku: {p}. Wypakuj CSV do folderu 'data/' lub ustaw DATA_DIR.")

def load_movies():
    _require_file_exists(MOVIES_CSV)
    with MOVIES_CSV.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [Movie(row['movieId'], row['title'], row['genres']) for row in reader]

def load_links():
    _require_file_exists(LINKS_CSV)
    with LINKS_CSV.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [Link(row['movieId'], row.get('imdbId', ''), row.get('tmdbId', '')) for row in reader]

def load_ratings():
    _require_file_exists(RATINGS_CSV)
    with RATINGS_CSV.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [Rating(row['userId'], row['movieId'], row['rating'], row['timestamp']) for row in reader]

def load_tags():
    _require_file_exists(TAGS_CSV)
    with TAGS_CSV.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [Tag(row['userId'], row['movieId'], row['tag'], row['timestamp']) for row in reader]

@app.on_event("startup")
async def startup_event():
    global _movies, _links, _ratings, _tags
    try:
        _movies = load_movies()
    except FileNotFoundError:
        _movies = []
    try:
        _links = load_links()
    except FileNotFoundError:
        _links = []
    try:
        _ratings = load_ratings()
    except FileNotFoundError:
        _ratings = []
    try:
        _tags = load_tags()
    except FileNotFoundError:
        _tags = []

@app.get("/hello")
async def hello():
    return {"hello": "world"}

#Paginacja
def paginate(items: List, limit: Optional[int], offset: Optional[int]):
    if limit is None and offset is None:
        return items
    off = max(0, offset or 0)
    if limit is None:
        return items[off:]
    return items[off: off + max(0, limit)]

#Endpointy danych
@app.get("/movies")
async def get_movies(limit: int | None = None, offset: int | None = None):
    if not _movies:
        raise HTTPException(status_code=503, detail="movies.csv nie został wczytany / brak pliku")
    return [m.__dict__ for m in paginate(_movies, limit, offset)]

@app.get("/links")
async def get_links(limit: int | None = None, offset: int | None = None):
    if not _links:
        raise HTTPException(status_code=503, detail="links.csv nie został wczytany / brak pliku")
    return [l.__dict__ for l in paginate(_links, limit, offset)]

@app.get("/ratings")
async def get_ratings(limit: int | None = 1000, offset: int | None = None):
    if not _ratings:
        raise HTTPException(status_code=503, detail="ratings.csv nie został wczytany / brak pliku")
    return [r.__dict__ for r in paginate(_ratings, limit, offset)]

@app.get("/tags")
async def get_tags(limit: int | None = None, offset: int | None = None):
    if not _tags:
        raise HTTPException(status_code=503, detail="tags.csv nie został wczytany / brak pliku")
    return [t.__dict__ for t in paginate(_tags, limit, offset)]

@app.get("/stats")
async def stats():
    return {
        "movies": len(_movies),
        "links": len(_links),
        "ratings": len(_ratings),
        "tags": len(_tags),
    }
