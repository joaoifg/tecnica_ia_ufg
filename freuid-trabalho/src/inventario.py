"""Passo 1: inventário do que existe de verdade no disco.

Conta os JPEGs, monta o universo (amostra.csv ∩ JPEGs com tamanho > 0) e compara a
distribuição de label, type e is_digital com os 69.352 rótulos de train_labels.csv.

Saída: reports/analise/inventario.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from config import ANALISE, DATA, SUBSET_DIR, SUBSET_MANIFEST
from protocolo import carregar_split, resumo_split


def dist(s: pd.Series) -> dict:
    vc = s.astype(str).value_counts().sort_index()
    return {k: {"n": int(v), "pct": float(v / len(s))} for k, v in vc.items()}


def main() -> None:
    ANALISE.mkdir(parents=True, exist_ok=True)
    jpegs = list(SUBSET_DIR.glob("*.jpeg"))
    vazios = [p for p in jpegs if p.stat().st_size == 0]
    pop = pd.read_csv(DATA / "train_labels.csv")
    man = pd.read_csv(SUBSET_MANIFEST)
    df = carregar_split()

    ids_disco = {p.stem for p in jpegs}
    fora_manifesto = len(ids_disco - set(man["id"]))
    out = {
        "pasta_imagens": str(SUBSET_DIR),
        "n_jpegs_no_disco": len(jpegs),
        "n_jpegs_vazios": len(vazios),
        "n_jpegs_fora_do_manifesto": fora_manifesto,
        "n_linhas_manifesto": int(len(man)),
        "n_linhas_manifesto_sem_jpeg": int(len(man) - len(df)),
        "n_rotulos_populacao": int(len(pop)),
        "n_universo": int(len(df)),
        "fracao_da_populacao": float(len(df) / len(pop)),
        "universo": {"label": dist(df["label"]), "type": dist(df["type"]), "is_digital": dist(df["is_digital"])},
        "populacao": {"label": dist(pop["label"]), "type": dist(pop["type"]), "is_digital": dist(pop["is_digital"])},
    }
    # desvio da amostra em relação à população, em pontos percentuais
    desvio = {}
    for col in ("label", "type", "is_digital"):
        u, p = out["universo"][col], out["populacao"][col]
        desvio[col] = {k: float(100 * (u.get(k, {"pct": 0})["pct"] - p[k]["pct"])) for k in p}
    out["desvio_pp_universo_menos_populacao"] = desvio
    out["desvio_max_pp"] = float(max(abs(v) for d in desvio.values() for v in d.values()))
    # taxa de fraude por tipo nos dois conjuntos
    out["taxa_fraude_por_tipo"] = {
        t: {"populacao": float(pop.loc[pop.type == t, "label"].mean()),
            "universo": float(df.loc[df.type == t, "label"].mean()) if (df.type == t).any() else None,
            "n_universo": int((df.type == t).sum())}
        for t in sorted(pop["type"].unique())
    }
    out["protocolo"] = resumo_split(df)
    # checagem: nenhum id em dois splits
    out["protocolo"]["ids_em_mais_de_um_split"] = int(df["id"].duplicated().sum())

    (ANALISE / "inventario.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"JPEGs no disco: {len(jpegs)} (vazios: {len(vazios)}) | universo: {len(df)} | "
          f"manifesto: {len(man)} | populacao: {len(pop)}")
    print(json.dumps(out["protocolo"], indent=2))
    print("desvio máximo (pp):", round(out["desvio_max_pp"], 2))


if __name__ == "__main__":
    main()
