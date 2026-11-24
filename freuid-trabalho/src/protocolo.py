"""Protocolo único de avaliação (clássicos e CNN usam exatamente os mesmos ids).

- Universo = linhas de amostra.csv cujo JPEG existe em SUBSET_DIR e tem tamanho > 0.
- OOD = o tipo MOZAMBIQUE/DL inteiro fica fora do treino.
- Tipos restantes: 80/20 estratificado por label (treino / validação ID), semente 42.

A tabela de split (ids) é gravada em <DATA>/split_protocolo.csv, fora do git, porque
lista ids do dataset. Nos JSON dos relatórios entram só contagens e um hash dos ids.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from config import DATA, RANDOM_SEED, SUBSET_DIR, SUBSET_MANIFEST

TIPO_OOD = "MOZAMBIQUE/DL"
FRAC_VAL_ID = 0.20
SPLIT_CSV = DATA / "split_protocolo.csv"


def _existe(p: str) -> bool:
    f = SUBSET_DIR / Path(p).name
    try:
        return f.is_file() and f.stat().st_size > 0
    except OSError:
        return False


def universo() -> pd.DataFrame:
    """Interseção de amostra.csv com os JPEGs que existem de verdade no disco."""
    df = pd.read_csv(SUBSET_MANIFEST)
    df = df.drop_duplicates("id")
    df = df[df["image_path"].map(_existe)].copy()
    df["arquivo"] = df["image_path"].map(lambda p: str(SUBSET_DIR / Path(p).name))
    df["is_digital"] = df["is_digital"].astype(bool)
    return df.sort_values("id").reset_index(drop=True)


def dividir(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Acrescenta a coluna `split` em {treino, val_id, ood}."""
    df = universo() if df is None else df.copy()
    df["split"] = "treino"
    df.loc[df["type"] == TIPO_OOD, "split"] = "ood"
    dentro = df.index[df["type"] != TIPO_OOD]
    _, val = train_test_split(dentro, test_size=FRAC_VAL_ID, stratify=df.loc[dentro, "label"],
                              random_state=RANDOM_SEED)
    df.loc[val, "split"] = "val_id"
    return df


def hash_ids(ids) -> str:
    return hashlib.sha256(",".join(sorted(map(str, ids))).encode()).hexdigest()[:16]


def resumo_split(df: pd.DataFrame) -> dict:
    """Contagens e hash por split, para conferir que todos os scripts usam os mesmos ids."""
    out = {"semente": RANDOM_SEED, "tipo_ood": TIPO_OOD, "frac_val_id": FRAC_VAL_ID, "n_universo": int(len(df))}
    for s in ("treino", "val_id", "ood"):
        g = df[df["split"] == s]
        out[s] = {"n": int(len(g)), "fraudes": int(g["label"].sum()), "legitimos": int((g["label"] == 0).sum()),
                  "hash_ids": hash_ids(g["id"])}
    return out


def carregar_split(salvar: bool = True) -> pd.DataFrame:
    df = dividir()
    if salvar:
        df[["id", "label", "type", "is_digital", "split"]].to_csv(SPLIT_CSV, index=False)
    return df


if __name__ == "__main__":
    import json

    print(json.dumps(resumo_split(carregar_split()), indent=2))
