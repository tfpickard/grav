"""Download and preprocess LIGO data into replayable segments."""
from __future__ import annotations

import json
import logging
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

import h5py
import numpy as np
import yaml
from scipy.signal import butter, filtfilt, hilbert, resample

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW_DIR = DATA_DIR / "raw"
SEGMENTS_DIR = DATA_DIR / "segments"
CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "defaults.yaml"

logger = logging.getLogger(__name__)


@dataclass
class SegmentMetadata:
    segment_id: str
    event_name: str
    detector: str
    sample_rate_hz: float
    t_start: float
    t_end: float
    num_samples: int


@dataclass
class Segment:
    metadata: SegmentMetadata
    samples: np.ndarray

    def to_npz(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path,
            samples=self.samples,
            metadata=json.dumps(asdict(self.metadata)),
        )


# --- Utility helpers ---

def _bandpass_filter(samples: np.ndarray, sample_rate: float, low_hz: float, high_hz: float) -> np.ndarray:
    nyquist = 0.5 * sample_rate
    b, a = butter(N=4, Wn=[low_hz / nyquist, high_hz / nyquist], btype="band")
    return filtfilt(b, a, samples)


def _extract_strain(dataset: h5py.File) -> Dict[str, np.ndarray]:
    strain_data: Dict[str, np.ndarray] = {}
    for detector in dataset.keys():
        group = dataset[detector]
        if not isinstance(group, h5py.Group):
            continue
        if "Strain" in group:
            strain_data[detector] = np.array(group["Strain"])
        elif "strain" in group:
            strain_data[detector] = np.array(group["strain"])
    return strain_data


def _find_segments(
    samples: np.ndarray,
    sample_rate: float,
    threshold: float,
    min_segment_s: float,
    max_segment_s: float,
) -> List[Segment]:
    analytic = hilbert(samples)
    envelope = np.abs(analytic)
    mean_env = np.mean(envelope)
    active = envelope > (mean_env * threshold)

    segments: List[Segment] = []
    idx = 0
    while idx < len(active):
        if not active[idx]:
            idx += 1
            continue
        start_idx = idx
        while idx < len(active) and active[idx]:
            idx += 1
        end_idx = idx
        duration = (end_idx - start_idx) / sample_rate
        if duration < min_segment_s or duration > max_segment_s:
            continue
        segment_samples = samples[start_idx:end_idx]
        segments.append((start_idx, end_idx, segment_samples))

    parsed_segments: List[Segment] = []
    for seg_num, (start_idx, end_idx, seg_samples) in enumerate(segments, start=1):
        metadata = SegmentMetadata(
            segment_id=f"segment_{seg_num:02d}",
            event_name="unknown",
            detector="",
            sample_rate_hz=sample_rate,
            t_start=start_idx / sample_rate,
            t_end=end_idx / sample_rate,
            num_samples=len(seg_samples),
        )
        parsed_segments.append(Segment(metadata=metadata, samples=seg_samples))
    return parsed_segments


def _resample_if_needed(samples: np.ndarray, current_rate: float, target_rate: float) -> np.ndarray:
    if math.isclose(current_rate, target_rate, rel_tol=1e-3):
        return samples
    num_samples = int(len(samples) * target_rate / current_rate)
    return resample(samples, num_samples)


# --- Pipeline steps ---

def download_data() -> List[Path]:
    from backend.scripts.download_ligo_data import download_from_config  # type: ignore

    return download_from_config(CONFIG_PATH, RAW_DIR)


def preprocess_file(path: Path, config: Dict) -> List[Segment]:
    logger.info("Processing %s", path.name)
    processing_cfg = config.get("processing", {})
    low = float(processing_cfg.get("bandpass_low_hz", 20))
    high = float(processing_cfg.get("bandpass_high_hz", 500))
    resample_rate = float(processing_cfg.get("resample_rate", 4096))
    threshold = float(processing_cfg.get("envelope_threshold", 1.5))
    min_seg = float(processing_cfg.get("min_segment_seconds", 0.25))
    max_seg = float(processing_cfg.get("max_segment_seconds", 4.0))

    segments: List[Segment] = []
    with h5py.File(path, "r") as f:
        strain_by_detector = _extract_strain(f)
        if not strain_by_detector:
            logger.warning("No strain data found in %s", path)
            return []
        for detector, samples in strain_by_detector.items():
            raw_rate = f[detector].attrs.get("SampleRate", resample_rate)
            filtered = _bandpass_filter(samples, raw_rate, low, high)
            conditioned = _resample_if_needed(filtered, raw_rate, resample_rate)
            detected_segments = _find_segments(conditioned, resample_rate, threshold, min_seg, max_seg)
            for seg in detected_segments:
                seg.metadata.event_name = path.name.split("_")[0]
                seg.metadata.detector = detector
                segments.append(seg)
    return segments


def persist_segments(event_segments: List[Segment], output_dir: Path) -> List[Path]:
    saved: List[Path] = []
    for seg in event_segments:
        filename = f"{seg.metadata.event_name}_{seg.metadata.detector}_{seg.metadata.segment_id}.npz"
        destination = output_dir / filename
        seg.to_npz(destination)
        saved.append(destination)
        logger.info("Saved %s", destination)
    return saved


def run_pipeline() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing config file at {CONFIG_PATH}")
    with CONFIG_PATH.open() as f:
        config = yaml.safe_load(f)

    downloaded_files = download_data()
    SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)
    total_segments = 0
    for file_path in downloaded_files:
        segments = preprocess_file(file_path, config)
        persist_segments(segments, SEGMENTS_DIR)
        total_segments += len(segments)

    if total_segments == 0:
        logger.warning("No segments were detected; consider adjusting thresholds.")


def main() -> None:
    run_pipeline()


if __name__ == "__main__":
    main()
