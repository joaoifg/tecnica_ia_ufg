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
# Pasta dos JPEGs de treino. Ordem de procura:
#   1) variável FREUID_IMAGES;
#   2) dataset completo extraído do zip oficial (69.352 JPEGs) em <DATA>/dataset_completo
#      (fora do OneDrive; foi movido de ../dataset_completo em 24/11/2026);
#   3) amostra baixada por src/baixar_imagens.py em C:\freuid\data\images\train\train.
_AMOSTRA_DIR = IMAGES / "train" / "train"   # gerado por src/baixar_imagens.py
_COMPLETO_DIR = DATA / "dataset_completo" / "the-freuid-challenge-2026-ijcai-ecai" / "train" / "train"
if os.environ.get("FREUID_IMAGES"):
    SUBSET_DIR = Path(os.environ["FREUID_IMAGES"])
elif _COMPLETO_DIR.is_dir():
    SUBSET_DIR = _COMPLETO_DIR
else:
    SUBSET_DIR = _AMOSTRA_DIR
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

# Núcleos de CPU para extração de features e Random Forest. A máquina teve telas azuis
# sob carga total em 24/11/2026; por isso o padrão não usa todos os núcleos.
JOBS = int(os.environ.get("FREUID_JOBS", "8"))
