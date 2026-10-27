"""Caminhos e hiperparâmetros do projeto FREUID."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
IMAGES = DATA / "images"  # junction → E:\ufg-freuid-data
SUBSET_DIR = IMAGES / "subset"
SUBSET_MANIFEST = DATA / "subset_manifest.csv"

COMPETITION = "the-freuid-challenge-2026-ijcai-ecai"
# No Kaggle o caminho real é train/train/<id>.jpeg (CSV traz train/<id>.jpeg)
REMOTE_TRAIN_PREFIX = "train/train/"

SUBSET_SIZE = 600  # local rápido; CNN completa no notebook Kaggle
RANDOM_SEED = 42
IMG_SIZE = 128  # features clássicas; CNN no Kaggle usa 384–512
N_JOBS_DOWNLOAD = 4
