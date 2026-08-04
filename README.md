# MemeSyncMusic

MemeSyncMusic creates beat-synced meme slideshow videos from:

- A YouTube music URL
- Or an uploaded MP3/WAV file

## Current workflow

1. User enters a YouTube URL (or uploads a song) in the frontend.
2. Backend creates a `job_id` and processes the source audio.
3. Frontend calls `/analyze/{job_id}` to get beat timing.
4. Frontend reads transcript/lyrics (YouTube flow) and calls `/meme/search` per lyric line.
5. Frontend builds a beat-aligned slideshow timeline.
6. Result page plays the slideshow with audio and supports **Download Generated Video**.

## API endpoints used

- `POST /youtube/process`
- `POST /upload`
- `GET /analyze/{job_id}`
- `POST /meme/search`
- `GET /uploads/{job_id}/transcript.json` (YouTube transcript file)

## Run locally

### Backend

```bash
cd Backend
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in frontend environment to your backend URL (example: `http://localhost:8000`).

## Notes

- Downloaded videos are currently exported in browser as **WebM** (`.webm`).
- If remote images block cross-origin rendering in your browser, export may fail for those slides.
