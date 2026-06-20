"""
Iltasatuja - Web-sovellus iltasatujen tallentamiseen ja TTS-äänitykseen.
"""

import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from db import get_db, init_db
from tts_service import TTSService

app = FastAPI(title="Iltasatuja", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mallit ──────────────────────────────────────────────

class StoryCreate(BaseModel):
    title: str
    content: str

class StoryResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: str
    has_audio: bool
    audio_path: str | None

class StoryListResponse(BaseModel):
    stories: list[StoryResponse]

# ── TTS-palvelu ────────────────────────────────────────

tts = TTSService(
    model_name="AsmoKoskinen/F5-TTS_Finnish_Model",
    cache_dir=Path(__file__).parent.parent / "data" / "models",
)

# ── Tietokanta-alustus ────────────────────────────────

@app.on_event("startup")
async def startup():
    init_db()

# ── API-päätepisteet ──────────────────────────────────

@app.get("/api/stories", response_model=StoryListResponse)
async def list_stories():
    """Listaa kaikki tallennetut iltasatuja."""
    db = get_db()
    rows = db.execute(
        "SELECT id, title, content, created_at, audio_path FROM stories ORDER BY created_at DESC"
    ).fetchall()
    db.close()

    stories = []
    for row in rows:
        stories.append(StoryResponse(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            created_at=row["created_at"],
            has_audio=row["audio_path"] is not None,
            audio_path=row["audio_path"],
        ))

    return StoryListResponse(stories=stories)

@app.post("/api/stories", response_model=StoryResponse)
async def create_story(story: StoryCreate):
    """Luo uusi iltasatu."""
    if not story.title.strip():
        raise HTTPException(status_code=400, detail="Otsikko ei voi olla tyhjä")
    if not story.content.strip():
        raise HTTPException(status_code=400, detail="Sisältö ei voi olla tyhjä")

    created_at = time.strftime("%Y-%m-%d %H:%M:%S")
    db = get_db()
    cursor = db.execute(
        "INSERT INTO stories (title, content, created_at) VALUES (?, ?, ?)",
        (story.title.strip(), story.content.strip(), created_at),
    )
    story_id = cursor.lastrowid
    db.commit()
    db.close()

    return StoryResponse(
        id=story_id,
        title=story.title,
        content=story.content,
        created_at=created_at,
        has_audio=False,
        audio_path=None,
    )

@app.get("/api/stories/{story_id}", response_model=StoryResponse)
async def get_story(story_id: int):
    """Hae yksi iltasatu."""
    db = get_db()
    row = db.execute(
        "SELECT id, title, content, created_at, audio_path FROM stories WHERE id = ?",
        (story_id,),
    ).fetchone()
    db.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Iltasatu ei löydy")

    return StoryResponse(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        created_at=row["created_at"],
        has_audio=row["audio_path"] is not None,
        audio_path=row["audio_path"],
    )

@app.delete("/api/stories/{story_id}")
async def delete_story(story_id: int):
    """Poista iltasatu ja sen äänitiedosto."""
    db = get_db()
    row = db.execute(
        "SELECT audio_path FROM stories WHERE id = ?",
        (story_id,),
    ).fetchone()
    db.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Iltasatu ei löydy")

    # Poista äänitiedosto jos on
    if row["audio_path"]:
        wav_path = Path(__file__).parent.parent / "data" / "wavs" / row["audio_path"]
        if wav_path.exists():
            wav_path.unlink()

    db = get_db()
    db.execute("DELETE FROM stories WHERE id = ?", (story_id,))
    db.commit()
    db.close()

    return {"message": "Iltasatu poistettu"}

@app.post("/api/stories/{story_id}/generate")
async def generate_audio(story_id: int):
    """Generoi .wav-äänitiedosto iltasadusta TTS-mallilla."""
    db = get_db()
    row = db.execute(
        "SELECT id, title, content, audio_path FROM stories WHERE id = ?",
        (story_id,),
    ).fetchone()
    db.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Iltasatu ei löydy")

    # Jos ääni on jo generoitu, palauta se
    if row["audio_path"]:
        wav_path = Path(__file__).parent.parent / "data" / "wavs" / row["audio_path"]
        if wav_path.exists():
            return {"message": "Äänitiedosto on jo olemassa", "audio_path": row["audio_path"]}

    # Generoi uusi ääni
    wav_filename = f"story_{story_id}_{int(time.time())}.wav"
    wav_path = Path(__file__).parent.parent / "data" / "wavs" / wav_filename

    audio_bytes = tts.generate(row["content"])

    # Tallenna .wav-tiedosto
    with open(wav_path, "wb") as f:
        f.write(audio_bytes)

    # Päivitä tietokanta
    db = get_db()
    db.execute(
        "UPDATE stories SET audio_path = ? WHERE id = ?",
        (wav_filename, story_id),
    )
    db.commit()
    db.close()

    return {"message": "Äänitiedosto generoitu", "audio_path": wav_filename}

@app.get("/api/stories/{story_id}/audio")
async def get_audio(story_id: int):
    """Palauta .wav-äänitiedosto iltasadusta."""
    db = get_db()
    row = db.execute(
        "SELECT audio_path FROM stories WHERE id = ?",
        (story_id,),
    ).fetchone()
    db.close()

    if row is None or row["audio_path"] is None:
        raise HTTPException(status_code=404, detail="Äänitiedostoa ei ole")

    wav_path = Path(__file__).parent.parent / "data" / "wavs" / row["audio_path"]
    if not wav_path.exists():
        raise HTTPException(status_code=404, detail="Äänitiedostoa ei löydy")

    return FileResponse(
        path=wav_path,
        media_type="audio/wav",
        filename=row["audio_path"],
    )
