"""Replay engine for quasi-live gravitational wave segments."""
from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from pydantic import BaseModel

DEFAULT_SEGMENTS_PATH = Path(os.getenv("SEGMENTS_PATH", Path(__file__).resolve().parents[1] / "data" / "segments"))


@dataclass
class ReplayConfig:
    chunk_duration_seconds: float = float(os.getenv("CHUNK_DURATION_SECONDS", 0.5))
    playback_speed: float = float(os.getenv("PLAYBACK_SPEED", 1.0))
    loop_segments: bool = os.getenv("LOOP_SEGMENTS", "true").lower() in {"true", "1", "yes"}


class SegmentInfo(BaseModel):
    segment_id: str
    event_name: str
    detector: str
    sample_rate_hz: float
    num_samples: int
    duration_seconds: float
    source_path: str


class ReplayState(BaseModel):
    current_segment: Optional[SegmentInfo]
    playhead_position: int
    total_chunks: int
    config: ReplayConfig


class SegmentStore:
    def __init__(self, segments_path: Path = DEFAULT_SEGMENTS_PATH) -> None:
        self.segments_path = segments_path
        self.segments: Dict[str, Dict[str, np.ndarray]] = {}
        self.metadata: Dict[str, SegmentInfo] = {}
        self._load_segments()

    def _load_segments(self) -> None:
        self.segments.clear()
        self.metadata.clear()
        if not self.segments_path.exists():
            self.segments_path.mkdir(parents=True, exist_ok=True)
        for file in self.segments_path.glob("*.npz"):
            npz = np.load(file, allow_pickle=True)
            samples = npz["samples"]
            metadata = json.loads(npz["metadata"].item())
            segment_id = metadata.get("segment_id")
            info = SegmentInfo(
                segment_id=segment_id,
                event_name=metadata.get("event_name", "unknown"),
                detector=metadata.get("detector", ""),
                sample_rate_hz=float(metadata.get("sample_rate_hz", 4096)),
                num_samples=int(metadata.get("num_samples", len(samples))),
                duration_seconds=float(metadata.get("num_samples", len(samples)) / metadata.get("sample_rate_hz", 1)),
                source_path=str(file),
            )
            self.segments[segment_id] = {"samples": samples}
            self.metadata[segment_id] = info
        if not self.segments:
            self._seed_with_synthetic()

    def _seed_with_synthetic(self) -> None:
        sample_rate = 4096
        t = np.linspace(0, 2, sample_rate * 2)
        samples = 1e-21 * np.sin(2 * np.pi * 100 * t) * np.exp(-t)
        segment_id = "synthetic_ringdown"
        info = SegmentInfo(
            segment_id=segment_id,
            event_name="Synthetic",
            detector="H1",
            sample_rate_hz=sample_rate,
            num_samples=len(samples),
            duration_seconds=len(samples) / sample_rate,
            source_path="synthetic",
        )
        self.segments[segment_id] = {"samples": samples}
        self.metadata[segment_id] = info

    def list_segments(self) -> List[SegmentInfo]:
        return list(self.metadata.values())


class ReplayEngine:
    def __init__(self, store: SegmentStore, config: ReplayConfig | None = None) -> None:
        self.store = store
        self.config = config or ReplayConfig()
        self.current_segment_id: Optional[str] = None
        self.playhead: int = 0
        self._select_initial_segment()

    def _select_initial_segment(self) -> None:
        segments = self.store.list_segments()
        if not segments:
            raise RuntimeError("No segments available for playback")
        self.current_segment_id = random.choice(segments).segment_id
        self.playhead = 0

    def select_segment(self, segment_id: str, reset: bool = True) -> SegmentInfo:
        if segment_id not in self.store.metadata:
            raise KeyError(f"Segment {segment_id} not found")
        self.current_segment_id = segment_id
        if reset:
            self.playhead = 0
        return self.store.metadata[segment_id]

    def _current_samples(self) -> np.ndarray:
        if not self.current_segment_id:
            raise RuntimeError("No segment selected")
        return self.store.segments[self.current_segment_id]["samples"]

    def _chunk_size(self, sample_rate: float) -> int:
        return int(sample_rate * self.config.chunk_duration_seconds * self.config.playback_speed)

    def next_chunk(self) -> Dict:
        samples = self._current_samples()
        meta = self.store.metadata[self.current_segment_id]  # type: ignore[arg-type]
        chunk_size = self._chunk_size(meta.sample_rate_hz)
        start = self.playhead * chunk_size
        end = start + chunk_size
        if start >= len(samples):
            if self.config.loop_segments:
                self.playhead = 0
                start = 0
                end = chunk_size
            else:
                self._advance_segment()
                return self.next_chunk()
        chunk = samples[start:end]
        self.playhead += 1
        total_chunks = max(1, int(np.ceil(len(samples) / chunk_size)))
        return {
            "segment_id": meta.segment_id,
            "sample_rate_hz": meta.sample_rate_hz,
            "t_start": start / meta.sample_rate_hz,
            "t_end": min(end, len(samples)) / meta.sample_rate_hz,
            "samples": chunk.tolist(),
            "metadata": {
                "event_name": meta.event_name,
                "detector": meta.detector,
                "playhead_position": self.playhead,
                "total_chunks": total_chunks,
            },
        }

    def _advance_segment(self) -> None:
        segments = self.store.list_segments()
        if not segments:
            raise RuntimeError("No segments available")
        current_idx = next((i for i, s in enumerate(segments) if s.segment_id == self.current_segment_id), 0)
        next_idx = (current_idx + 1) % len(segments)
        self.current_segment_id = segments[next_idx].segment_id
        self.playhead = 0

    def state(self) -> ReplayState:
        meta = self.store.metadata.get(self.current_segment_id or "")
        chunk_size = self._chunk_size(meta.sample_rate_hz) if meta else 0
        total_chunks = max(1, int(np.ceil(meta.num_samples / chunk_size))) if meta and chunk_size else 0
        return ReplayState(
            current_segment=meta,
            playhead_position=self.playhead,
            total_chunks=total_chunks,
            config=self.config,
        )
