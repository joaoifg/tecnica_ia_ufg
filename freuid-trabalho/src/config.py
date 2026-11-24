"""Caminhos e hiperparâmetros do projeto FREUID."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Dados ficam FORA do OneDrive (licença + volume): C:\freuid\data por padrão
DATA = Path(os.environ.get("FREUID_DATA", r"C:\freuid\data"))
REPORTS = Path(os.environ.get("FREUID_REPORTS", ROOT / "reports"))
FIGS = REPORTS / "figs"          # gráficos gerados pela análise
ANALISE = REPORTS / "analise"    # tabelas e JSON com os números
IMAGES = DATA / "images"
SUBSET_DIR = IMAGES / "train" / "train"   # gerado por src/baixar_imagens.py
SUBSET_MANIFEST = DATA / "amostra.csv"
FEATURES_CSV = DATA / "features.csv"

COMPETITION = "the-freuid-challenge-2026-ijcai-ecai"
# No Kaggle o caminho real é train/train/<id>.jpeg (CSV traz train/<id>.jpeg)
REMOTE_TRAIN_PREFIX = "train/train/"

SUBSET_SIZE = 2000  # amostra estratificada por label × type
RANDOM_SEED = 42
IMG_SIZE = 128  # features clássicas; CNN no Kaggle usa 384–512
N_JOBS_DOWNLOAD = 8

NOMES_PAIS = {
    "EGYPT/DL": "Egito",
    "GUINEA/DL": "Guiné",
    "BENIN/DL": "Benin",
    "MOZAMBIQUE/DL": "Moçambique",
    "MAURITIUS/ID": "Maurício",
}
