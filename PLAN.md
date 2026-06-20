# Iltasatuja — Act Mode Plan

## Context
- Repo: /var/home/mariapori/Projektit/iltasatugen
- Backend: Python (FastAPI + uvicorn) with F5-TTS Finnish model
- Frontend: Vite + React + Node.js
- Data: SQLite DB, generated WAVs, downloaded ML models
- Git repo already initialized, .gitignore already committed

## Key Finding: Auto-downloads at runtime
The TTS service downloads from HuggingFace Hub on first use:
- Model weights (~hundreds of MB): model_last_20250323.safetensors
- Vocabulary file: vocab.txt
- Reference audio: AsmoKoskinenRef_v1.wav
- Reference text: AsmoKoskinenRef_v1.txt
- Vocoder: vocos
- Config YAML: downloaded from GitHub (raw.githubusercontent.com)

These are cached under data/models/ (HuggingFace Hub cache).
SQLite DB (data/iltasatuja.db) is created on startup.
WAV files (data/wavs/) are generated at runtime.

## Action Items for Act Mode

### 1. Fix .gitignore — track package-lock.json
- Remove `package-lock.json` from .gitignore
- Reason: Node.js projects should track lock files for reproducible builds
- Command: edit .gitignore, then `git add frontend/package-lock.json && git commit -m "track package-lock.json for reproducible builds"`

### 2. Add .gitignore for frontend subdirectory
- frontend/ already has its own .gitignore (node_modules/, dist/)
- Verify it doesn't conflict with root .gitignore
- If needed, remove redundant entries from root .gitignore

### 3. Consider .env file
- If the project uses environment variables (e.g., HF_TOKEN for HuggingFace), add `.env` to .gitignore
- Check if any env vars are used in the codebase

### 4. Consider Git LFS for large files
- If any large files (e.g., reference audio, model weights) need to be tracked, set up Git LFS
- For now, data/models/ and data/wavs/ are ignored — this is correct
- Only track if someone needs to share pre-downloaded models

### 5. Add README.md at project root
- Create a root README.md with setup instructions
- Include: `pip install -r requirements.txt`, `cd frontend && npm install`
- Include: first run will auto-download TTS model from HuggingFace
- Include: HF_TOKEN env var if needed for gated models

### 6. Stage remaining untracked files
- `git add backend/ frontend/ requirements.txt`
- `git commit -m "add project source code"`

## Notes
- The TTS model download can take a long time (hundreds of MB)
- First run will be slow due to model download
- Consider adding a startup check that verifies model is cached before starting the server
- Consider adding a pre-download script for CI/CD
