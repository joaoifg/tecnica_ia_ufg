"""Utilitários de caminho e manifesto do subset FREUID."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import DATA, SUBSET_DIR, SUBSET_MANIFEST


def remote_train_path(image_path: str) -> str:
    """CSV: train/<id>.jpeg → remoto: train/train/<id>.jpeg."""
    return f"train/train/{Path(image_path).name}"


def local_image_path(image_path: str) -> Path:
    return SUBSET_DIR / Path(image_path).name


def load_manifest(only_existing: bool = True) -> pd.DataFrame:
    path = SUBSET_MANIFEST if SUBSET_MANIFEST.exists() else DATA / "train_labels.csv"
    df = pd.read_csv(path)
    if only_existing:
        mask = df["image_path"].map(lambda p: local_image_path(p).exists())
        df = df[mask].reset_index(drop=True)
    return df
