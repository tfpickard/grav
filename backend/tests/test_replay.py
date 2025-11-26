from backend.src.core.replay import ReplayConfig, ReplayEngine, SegmentInfo, SegmentStore
import numpy as np


def test_replay_advances_and_loops():
    store = SegmentStore()
    # replace synthetic data with deterministic short sample
    samples = np.arange(10)
    info = SegmentInfo(
        segment_id="test",
        event_name="unit",
        detector="H1",
        sample_rate_hz=10,
        num_samples=len(samples),
        duration_seconds=len(samples) / 10,
        source_path="test",
    )
    store.segments = {"test": {"samples": samples}}
    store.metadata = {"test": info}

    engine = ReplayEngine(store=store, config=ReplayConfig(chunk_duration_seconds=0.2, playback_speed=1.0, loop_segments=True))
    chunk1 = engine.next_chunk()
    chunk2 = engine.next_chunk()
    chunk3 = engine.next_chunk()

    assert chunk1["samples"] == [0, 1]
    assert chunk2["samples"] == [2, 3]
    assert chunk3["samples"] == [4, 5]

    # simulate exhausting and looping
    for _ in range(10):
        engine.next_chunk()
    assert engine.playhead == 1  # after loop resets


def test_state_exposes_metadata():
    store = SegmentStore()
    engine = ReplayEngine(store=store)
    state = engine.state()
    assert state.current_segment is not None
    assert state.total_chunks >= 1
