from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.src.core.replay import ReplayEngine, ReplayState, SegmentInfo, SegmentStore

# Initialize store and engine
segments_path = Path(os.getenv("SEGMENTS_PATH", Path(__file__).resolve().parents[1] / "data" / "segments"))
store = SegmentStore(segments_path=segments_path)
engine = ReplayEngine(store=store)

app = FastAPI(title="Gravitational Wave Stream API", version="0.1.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SelectSegmentRequest(BaseModel):
    segment_id: str
    reset: Optional[bool] = True


@app.get("/api/segments", response_model=List[SegmentInfo])
def list_segments() -> List[SegmentInfo]:
    return store.list_segments()


@app.get("/api/stream/next")
def next_chunk():
    return engine.next_chunk()


@app.post("/api/stream/select", response_model=SegmentInfo)
def select_segment(payload: SelectSegmentRequest):
    try:
        return engine.select_segment(payload.segment_id, reset=payload.reset)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/stream/state", response_model=ReplayState)
def stream_state():
    return engine.state()


@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(engine.next_chunk())
    except WebSocketDisconnect:
        return


@app.get("/")
def healthcheck():
    return {"status": "ok"}
