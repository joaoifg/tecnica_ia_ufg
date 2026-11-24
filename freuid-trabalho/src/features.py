"""Extração de características clássicas das imagens (sem deep learning).

Dois conjuntos:
- V1 (64): histograma de cor + estatísticas + brilho + gradiente (versão original).
- Completo (73): V1 + 9 features de perícia de imagem (ELA, nitidez, frequência...).
"""

from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

from config import FEATURES_CSV, IMG_SIZE, SUBSET_DIR

# ---------------------------------------------------------------- nomes
CANAIS = ("R", "G", "B")
NOMES_HIST = [f"hist_{c}_{i:02d}" for c in CANAIS for i in range(16)]
NOMES_STATS = [f"{s}_{c}" for c in CANAIS for s in ("media", "desvio", "min", "max")]
NOMES_BRILHO = ["cinza_media", "cinza_desvio", "gradiente_x", "gradiente_y"]
FEATURES_V1 = NOMES_HIST + NOMES_STATS + NOMES_BRILHO  # 64
FEATURES_PERICIA = [
    "ela_media", "ela_desvio", "ela_p99",   # Error Level Analysis
    "nitidez_laplaciano",                  # variância do laplaciano
    "energia_alta_freq",                   # fração de energia em alta frequência (FFT)
    "densidade_bordas",
    "entropia_cinza",
    "saturacao_media", "saturacao_desvio",
]
FEATURES = FEATURES_V1 + FEATURES_PERICIA  # 73
METADADOS = ["largura", "altura", "tamanho_kb"]


def familia(nome: str) -> str:
    if nome.startswith("hist_R"):
        return "Histograma R"
    if nome.startswith("hist_G"):
        return "Histograma G"
    if nome.startswith("hist_B"):
        return "Histograma B"
    if nome in NOMES_STATS:
        return "Estatísticas de cor"
    if nome in NOMES_BRILHO:
        return "Brilho e bordas"
    return "Perícia (ELA, nitidez, frequência)"


# ---------------------------------------------------------------- V1
def _hist_features(arr: np.ndarray, bins: int = 16) -> np.ndarray:
    feats = []
    for c in range(arr.shape[2]):
        h, _ = np.histogram(arr[:, :, c], bins=bins, range=(0, 256), density=True)
        feats.append(h.astype(np.float32))
    return np.concatenate(feats)


def _stat_features(arr: np.ndarray) -> np.ndarray:
    ch = arr.astype(np.float32)
    stats = []
    for c in range(3):
        x = ch[:, :, c]
        stats.extend([x.mean(), x.std(), x.min(), x.max()])
    gray = 0.299 * ch[:, :, 0] + 0.587 * ch[:, :, 1] + 0.114 * ch[:, :, 2]
    gx = np.abs(np.diff(gray, axis=1)).mean()
    gy = np.abs(np.diff(gray, axis=0)).mean()
    stats.extend([gray.mean(), gray.std(), gx, gy])
    return np.asarray(stats, dtype=np.float32)


# ---------------------------------------------------------------- perícia
def _ela(im: Image.Image, qualidade: int = 90, lado: int = 256) -> np.ndarray:
    """Error Level Analysis: recomprime o JPEG e mede quanto cada pixel muda.

    Regiões coladas ou editadas costumam ter um nível de erro diferente do resto.
    Usa um recorte central sem redimensionar, para preservar a grade do JPEG.
    """
    w, h = im.size
    s = min(lado, w, h)
    left, top = (w - s) // 2, (h - s) // 2
    crop = im.crop((left, top, left + s, top + s))
    buf = io.BytesIO()
    crop.save(buf, "JPEG", quality=qualidade)
    buf.seek(0)
    recomp = Image.open(buf).convert("RGB")
    diff = np.abs(np.asarray(crop, np.float32) - np.asarray(recomp, np.float32))
    return np.array([diff.mean(), diff.std(), np.percentile(diff, 99)], np.float32)


def _pericia(im: Image.Image, arr: np.ndarray) -> np.ndarray:
    ela = _ela(im)
    gray = arr.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    # laplaciano 4-vizinhos por fatiamento
    lap = (
        -4 * gray[1:-1, 1:-1] + gray[:-2, 1:-1] + gray[2:, 1:-1] + gray[1:-1, :-2] + gray[1:-1, 2:]
    )
    nitidez = lap.var()
    # energia fora do quarto central do espectro
    spec = np.abs(np.fft.fftshift(np.fft.fft2(gray - gray.mean()))) ** 2
    n = gray.shape[0]
    q = n // 4
    centro = spec[n // 2 - q: n // 2 + q, n // 2 - q: n // 2 + q].sum()
    alta = 1.0 - centro / (spec.sum() + 1e-9)
    gx = np.abs(np.diff(gray, axis=1))[:-1, :]
    gy = np.abs(np.diff(gray, axis=0))[:, :-1]
    bordas = (np.hypot(gx, gy) > 30).mean()
    h, _ = np.histogram(gray, bins=64, range=(0, 256))
    p = h[h > 0] / h.sum()
    entropia = -(p * np.log2(p)).sum()
    sat = np.asarray(im.resize((IMG_SIZE, IMG_SIZE)).convert("HSV"), np.float32)[:, :, 1]
    return np.concatenate(
        [ela, [nitidez, alta, bordas, entropia, sat.mean(), sat.std()]]
    ).astype(np.float32)


# ---------------------------------------------------------------- API
def extract_one(path: Path, size: int = IMG_SIZE) -> tuple[np.ndarray, list[float]]:
    """Retorna (73 features, metadados [largura, altura, tamanho_kb])."""
    with Image.open(path) as raw:
        im = raw.convert("RGB")
    meta = [im.size[0], im.size[1], path.stat().st_size / 1024]
    arr = np.asarray(im.resize((size, size), Image.BILINEAR), dtype=np.uint8)
    feats = np.concatenate([_hist_features(arr), _stat_features(arr), _pericia(im, arr)])
    return feats, meta


def extract_matrix(image_paths: list[str], size: int = IMG_SIZE) -> np.ndarray:
    """Compatibilidade com o train.py antigo: só as 64 features V1."""
    rows = [extract_one(SUBSET_DIR / Path(p).name, size)[0][: len(FEATURES_V1)] for p in image_paths]
    return np.vstack(rows)


def build_feature_table(manifest: pd.DataFrame, force: bool = False) -> pd.DataFrame:
    """Extrai as features de todas as imagens do manifesto (com cache em CSV)."""
    if FEATURES_CSV.exists() and not force:
        cache = pd.read_csv(FEATURES_CSV)
        if set(manifest["id"]).issubset(set(cache["id"])):
            return cache[cache["id"].isin(manifest["id"])].reset_index(drop=True)
    rows = []
    for rec in tqdm(manifest.itertuples(index=False), total=len(manifest), desc="features"):
        local = SUBSET_DIR / Path(rec.image_path).name
        feats, meta = extract_one(local)
        rows.append([rec.id, rec.label, rec.type, rec.is_digital, *meta, *feats])
    cols = ["id", "label", "type", "is_digital", *METADADOS, *FEATURES]
    tab = pd.DataFrame(rows, columns=cols)
    tab.to_csv(FEATURES_CSV, index=False)
    return tab
