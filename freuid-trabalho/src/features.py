"""Extração de características clássicas a partir das imagens (sem deep learning)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image
from tqdm import tqdm

from config import IMG_SIZE, SUBSET_DIR


def _hist_features(arr: np.ndarray, bins: int = 16) -> np.ndarray:
    feats = []
    for c in range(arr.shape[2]):
        h, _ = np.histogram(arr[:, :, c], bins=bins, range=(0, 256), density=True)
        feats.append(h.astype(np.float32))
    return np.concatenate(feats)


def _stat_features(arr: np.ndarray) -> np.ndarray:
    # média/desvio/min/max por canal + luminância
    ch = arr.astype(np.float32)
    stats = []
    for c in range(3):
        x = ch[:, :, c]
        stats.extend([x.mean(), x.std(), x.min(), x.max()])
    gray = 0.299 * ch[:, :, 0] + 0.587 * ch[:, :, 1] + 0.114 * ch[:, :, 2]
    # gradientes simples (artefatos de edição / compressão)
    gx = np.abs(np.diff(gray, axis=1)).mean()
    gy = np.abs(np.diff(gray, axis=0)).mean()
    stats.extend([gray.mean(), gray.std(), gx, gy])
    return np.asarray(stats, dtype=np.float32)


def extract_one(path: Path, size: int = IMG_SIZE) -> np.ndarray:
    with Image.open(path) as im:
        im = im.convert("RGB").resize((size, size), Image.BILINEAR)
        arr = np.asarray(im, dtype=np.uint8)
    return np.concatenate([_hist_features(arr), _stat_features(arr)])


def extract_matrix(image_paths: list[str], size: int = IMG_SIZE) -> np.ndarray:
    rows = []
    for rel in tqdm(image_paths, desc="features"):
        local = SUBSET_DIR / Path(rel).name
        rows.append(extract_one(local, size=size))
    return np.vstack(rows)
