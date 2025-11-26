# Cosmic Stream - Quasi-live LIGO data faucet

This project restreams archival gravitational-wave data from the [LIGO Open Science Center](https://www.gw-openscience.org/) as if it were a live quasi-periodic feed. A Python/FastAPI backend downloads and preprocesses open HDF5 files, slices interesting oscillatory segments, and replays them through HTTP/WebSocket endpoints. A Next.js frontend renders the stream in real time with a space-themed UI.

## Project layout

- `backend/` – FastAPI service, preprocessing pipeline, and replay engine.
- `frontend/` – Next.js 14 app with real-time visualization.
- `docker-compose.yml` – local orchestration for the backend (frontend runs with `npm run dev`).
- `backend/config/defaults.yaml` – tunable parameters for playback and filtering.
- `backend/data/` – storage for raw downloads and processed segments.

## Quickstart

1. Copy environment defaults and install dependencies:
   ```bash
   cp backend/.env.example backend/.env
   python -m venv backend/.venv && source backend/.venv/bin/activate
   pip install -r backend/requirements.txt
   cd frontend && npm install
   ```

2. Preprocess LIGO data (downloads sample GW150914 files and extracts segments):
   ```bash
   docker compose run backend python -m src.processing.preprocess_ligo
   ```

3. Start services:
   ```bash
   docker compose up
   # Frontend in another shell
   cd frontend && npm run dev
   ```

4. Open http://localhost:3000 to view the stream console. The backend API lives at http://localhost:8000.

## Backend API

- `GET /api/segments` – list available segments.
- `GET /api/stream/next` – fetch next chunk of strain samples.
- `POST /api/stream/select` – `{ "segment_id": "..." }` to switch segments.
- `GET /api/stream/state` – current segment, playhead, and playback config.
- `WS /ws/stream` – optional push-based stream delivering JSON chunks.

Example curl:
```bash
curl http://localhost:8000/api/stream/next
```

## Data pipeline

- **Download**: `backend/scripts/download_ligo_data.py` pulls files defined in `config/defaults.yaml` into `backend/data/raw`.
- **Preprocess**: `backend/src/processing/preprocess_ligo.py` filters, normalizes, detects oscillatory windows via amplitude envelopes, and saves compact `.npz` segments with metadata to `backend/data/segments`.
- **Replay**: `backend/src/core/replay.py` loads saved segments (or a synthetic fallback), maintains a playhead, and returns chunked samples with configurable duration, speed, and looping.

Run the full pipeline via:
```bash
cd backend
python -m src.processing.preprocess_ligo
```

## Frontend

- Next.js app router with TypeScript components for the landing page, console view, and developer guide.
- Real-time chart built with Recharts and polling-based chunk retrieval (WebSocket ready on backend).
- Configure the API base URL through `frontend/.env.example` (`NEXT_PUBLIC_API_BASE`).

## Testing

Minimal unit tests cover replay stepping and state reporting:
```bash
cd backend
pytest
```

## Deployment notes

- Backend ships with a Dockerfile suitable for generic cloud hosting (`uvicorn app.main:app`).
- Frontend is optimized for Vercel; set `NEXT_PUBLIC_API_BASE` to point at your backend URL.
- Adjust filter thresholds and playback behavior in `backend/config/defaults.yaml` without changing code.
