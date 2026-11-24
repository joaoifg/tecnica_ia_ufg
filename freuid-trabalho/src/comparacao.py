"""Passo 5: tabela única de comparação, gerada só a partir dos JSON desta execução.

Entradas: reports/analise/modelagem.json (clássicos) e reports/analise/cnn.json (EfficientNet).
Saídas:   reports/analise/comparacao.csv e reports/figs/comparacao_id_ood.png
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from config import ANALISE

CLASSICOS = ("Regressão logística", "Random Forest", "Gradient Boosting")
NOME_SPLIT = {"id": "validação ID", "ood": "OOD (Moçambique)"}


def main() -> None:
    mod = json.loads((ANALISE / "modelagem.json").read_text(encoding="utf-8"))
    linhas = []
    for s in ("id", "ood"):
        h = mod["holdout"][s]
        for nome in CLASSICOS:
            r = h["modelos"][nome]
            linhas.append({"modelo": nome, "split": NOME_SPLIT[s], "n": h["n_teste"], "roc_auc": r["auc"],
                           "audet": r["audet"], "apcer_1pct_bpcer": r["apcer_1pct_bpcer"], "freuid": r["freuid"],
                           "limiar_custo": r["limiar_custo"]["limiar"], "recall_limiar_custo": r["limiar_custo"]["recall"],
                           "recall_limiar_0_5": r["limiar_0_5"]["recall"], "fonte": "modelagem.json"})
    arq_cnn = ANALISE / "cnn.json"
    if arq_cnn.exists():
        cnn = json.loads(arq_cnn.read_text(encoding="utf-8"))
        for s in ("id", "ood"):
            c, m5 = cnn["holdout"][s]["limiar_custo"], cnn["holdout"][s]["limiar_0.5"]
            linhas.append({"modelo": "EfficientNet-B0", "split": NOME_SPLIT[s], "n": c["n"], "roc_auc": c["auc"],
                           "audet": c["audet"], "apcer_1pct_bpcer": c["apcer_1pct_bpcer"], "freuid": c["freuid"],
                           "limiar_custo": c["limiar"], "recall_limiar_custo": c["recall"],
                           "recall_limiar_0_5": m5["recall"], "fonte": "cnn.json"})
    else:
        print("AVISO: cnn.json não existe; a tabela sai só com os modelos clássicos")
    tab = pd.DataFrame(linhas)
    tab.to_csv(ANALISE / "comparacao.csv", index=False, float_format="%.6f")
    print(tab.drop(columns=["fonte"]).to_string(index=False, float_format=lambda v: f"{v:.3f}"))

    from estilo import COR, aplicar, salvar
    import matplotlib.pyplot as plt

    aplicar()
    modelos = list(dict.fromkeys(tab["modelo"]))
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
    x = np.arange(len(modelos))
    for ax, (col, titulo, ylim) in zip(axes, (("roc_auc", "ROC-AUC (maior é melhor)", (0.4, 1.0)),
                                               ("freuid", "FREUID Score (menor é melhor)", (0, 1.0)))):
        for k, (s, cor) in enumerate(((NOME_SPLIT["id"], COR["azul"]), (NOME_SPLIT["ood"], COR["laranja"]))):
            v = [tab.loc[(tab.modelo == m) & (tab.split == s), col].squeeze() for m in modelos]
            b = ax.bar(x + (k - 0.5) * 0.38, v, 0.38, color=cor, label=s)
            ax.bar_label(b, [f"{val:.2f}".replace(".", ",") for val in v], fontsize=9, padding=2)
        ax.set_xticks(x, modelos, fontsize=9)
        ax.set_ylim(*ylim)
        ax.set_title(titulo)
        ax.set_ylabel(col.replace("roc_auc", "ROC-AUC").replace("freuid", "FREUID"))
    axes[0].axhline(0.5, color="grey", ls=":", lw=1)
    fig.suptitle("Mesmo modelo, documento visto (ID) × documento nunca visto (OOD)", y=1.08)
    fig.tight_layout()
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.02), frameon=False)
    salvar(fig, "comparacao_id_ood")


if __name__ == "__main__":
    main()
