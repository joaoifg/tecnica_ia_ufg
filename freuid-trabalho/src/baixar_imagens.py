"""Baixa uma amostra estratificada (label x type x is_digital) das imagens de treino.

Retomável: imagens já baixadas são puladas. Uso:
    python src/baixar_imagens.py --n 25000
Saída: <DATA>/images/train/train/<id>.jpeg  e  <DATA>/amostra.csv
"""

from __future__ import annotations

import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
from tqdm import tqdm

from config import COMPETITION, DATA, RANDOM_SEED

IMG_DIR = DATA / "images"
AMOSTRA = DATA / "amostra.csv"


def montar_amostra(n: int) -> pd.DataFrame:
    df = pd.read_csv(DATA / "train_labels.csv")
    raros = df[~df["is_digital"]]  # recapturados: todos entram (são só 21)
    resto = df[df["is_digital"]]
    frac = (n - len(raros)) / len(resto)
    amostra = resto.groupby(["type", "label"], group_keys=False).sample(frac=frac, random_state=RANDOM_SEED)
    out = pd.concat([raros, amostra]).sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    out["arquivo"] = out["image_path"].map(lambda p: str(IMG_DIR / "train" / "train" / p.split("/")[-1]))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=25000)
    ap.add_argument("--threads", type=int, default=16)
    args = ap.parse_args()

    amostra = montar_amostra(args.n)
    amostra.to_csv(AMOSTRA, index=False)
    print(amostra.groupby(["type", "label"]).size().unstack())

    api = KaggleApi()
    api.authenticate()
    from pathlib import Path

    faltam = [a for a in amostra["arquivo"] if not (Path(a).exists() and Path(a).stat().st_size > 0)]
    print(f"{len(amostra) - len(faltam)} já existem, baixando {len(faltam)}")

    def baixar(arquivo: str) -> bool:
        remoto = "train/train/" + Path(arquivo).name
        for tentativa in range(4):
            try:
                api.competition_download_file(COMPETITION, remoto, path=str(IMG_DIR), quiet=True)
                return True
            except Exception:  # noqa: BLE001 - rede instável: tenta de novo
                time.sleep(2 * (tentativa + 1))
        return False

    falhas = 0
    with ThreadPoolExecutor(args.threads) as ex:
        futs = [ex.submit(baixar, a) for a in faltam]
        for f in tqdm(as_completed(futs), total=len(futs), mininterval=30):
            falhas += not f.result()
    print(f"Concluído. Falhas: {falhas}")


if __name__ == "__main__":
    main()
