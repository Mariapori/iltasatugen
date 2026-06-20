# Iltasatuja

Web-sovellus iltasatujen tallentamiseen ja TTS-äänitykseen (tekstistä puheeksi).

Projekti on generoitu 100% https://huggingface.co/Jackrong/Qwopus3.6-27B-Coder-MTP-GGUF käyttäen:
llama.cpp
RTX 5060 Ti 16GB


## Teknologiat

- **Backend:** Python (FastAPI + uvicorn)
- **TTS:** F5-TTS suomenkielinen malli (HuggingFace Hub)
- **Frontend:** Vite + React
- **Tietokanta:** SQLite

## Asennus

### 1. Python-riippuvuudet

```bash
pip install -r requirements.txt
```

### 2. Frontend-riippuvuudet

```bash
cd frontend
npm install
```

### 3. HuggingFace-token (jos tarvitaan)

Jos TTS-malli on "gated" (vaatii kirjautumisen), aseta `HF_TOKEN`-ympäristömuuttuja ennen ensimmäistä käynnistystä:

```bash
export HF_TOKEN=hf_...
```

Tokenin saa [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) -sivulta.

## Käynnistys

### Backend

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend (kehityskäyttö)

```bash
cd frontend
npm run dev
```

## Ensimmäinen käynnistys — mallin lataus

Kun backend käynnistetään ensimmäistä kertaa, se lataa TTS-mallin automaattisesti HuggingFace Hubista. Tämä voi kestää hetken (malli on satoja megatavuja).

Ladattavat tiedostot:
- Mallipainot: `model_last_20250323.safetensors`
- Sanakirja: `vocab.txt`
- Viiteääni: `AsmoKoskinenRef_v1.wav`
- Viiteteksti: `AsmoKoskinenRef_v1.txt`
- Vocoder: `vocos`
- Konfiguraatio: `F5TTS_v1_Base.yaml` (GitHubista)

Tiedostot tallennetaan `data/models/` -hakemistoon ja ladataan vain kerran.

## API-päätepisteet

| Päätepiste | Kuvaus |
|---|---|
| `GET /api/stories` | Listaa kaikki iltasatuja |
| `POST /api/stories` | Luo uusi iltasatu |
| `GET /api/stories/{id}` | Hae yksi iltasatu |
| `DELETE /api/stories/{id}` | Poista iltasatu ja sen äänitiedosto |
| `POST /api/stories/{id}/generate` | Generoi äänitiedosto TTS:llä |
| `GET /api/stories/{id}/audio` | Palauta äänitiedosto |
