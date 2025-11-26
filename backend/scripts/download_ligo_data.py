"""Utility to download sample LIGO open data files defined in a YAML config."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Iterable, List

import requests
import yaml

logger = logging.getLogger(__name__)


def _hash_url(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]


def download_file(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading %s -> %s", url, dest)
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    with dest.open("wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return dest


def download_from_config(config_path: Path, raw_data_dir: Path) -> List[Path]:
    with config_path.open() as f:
        config = yaml.safe_load(f)
    datasets = config.get("datasets", [])
    downloaded: List[Path] = []
    for dataset in datasets:
        urls: Iterable[str] = dataset.get("urls", [])
        for url in urls:
            filename = Path(url.split("/")[-1])
            hashed = _hash_url(url)
            destination = raw_data_dir / f"{filename.stem}_{hashed}{filename.suffix}"
            if destination.exists():
                logger.info("Skipping existing file %s", destination)
                downloaded.append(destination)
                continue
            downloaded.append(download_file(url, destination))
    return downloaded


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    config_path = Path(__file__).resolve().parents[1] / "config" / "defaults.yaml"
    raw_data_dir = Path(__file__).resolve().parents[1] / "data" / "raw"
    download_from_config(config_path, raw_data_dir)


if __name__ == "__main__":
    main()
