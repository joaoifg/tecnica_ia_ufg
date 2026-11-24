"""Figuras e tempos extras para a apresentação (depois de rodar CNN, diagnóstico e Grad-CAM).

Saídas:
- reports/analise/tempos.json: duração de cada etapa, medida pelos logs e pelos carimbos de data dos
  arquivos que cada script grava (método registrado no próprio JSON).
- reports/figs/cnn_treino.png: AUC da validação ID e perda por época.
- reports/figs/cnn_escores.png: distribuição de P(fraude) por classe, ID × OOD (só histograma agregado).
- reports/figs/gradcam_borda.png: fração do mapa Grad-CAM na borda e no centro (números, sem imagem).
- reports/figs/tempos.png: duração das etapas.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import ANALISE, DATA
from estilo import COR, aplicar, salvar

RUNS = Path(r"C:\freuid\runs")
RUN = RUNS / "ood_efficientnet_b0"


def mtime(p: Path) -> float:
    return p.stat().st_mtime


def tempos() -> dict:
    out = {"metodo": "logs (tqdm, histórico da CNN) e carimbos de data dos arquivos gravados por cada script; "
                      "valores aproximados ao segundo"}
    # extração de features: soma do tempo de cada bloco no log do tqdm
    log = (RUNS / "features_stdout.txt").read_text(encoding="utf-8", errors="ignore")
    seg = 0
    for bloco in re.findall(r"100%\|[^\[]*\[(\d+):(\d+)<", log):
        seg += int(bloco[0]) * 60 + int(bloco[1])
    n_img = len(pd.read_csv(DATA / "features.csv", usecols=["id"]))
    out["extracao_features"] = {"seg": seg, "imagens": n_img, "img_por_seg": n_img / max(seg, 1),
                                "nucleos": 8, "fonte": "features_stdout.txt (tqdm)"}
    out["eda"] = {"seg": mtime(ANALISE / "eda.json") - mtime(DATA / "features.csv"),
                  "fonte": "eda.json − features.csv"}
    out["modelagem"] = {"seg": mtime(ANALISE / "modelagem.json") - mtime(RUNS / "modelagem_stderr.txt"),
                        "fonte": "modelagem.json − início do processo (modelagem_stderr.txt)"}
    cnn = json.loads((ANALISE / "cnn.json").read_text(encoding="utf-8"))
    eps = [h["seg"] for h in cnn["historico"]]
    out["cnn"] = {"epocas": len(eps), "melhor_epoca": cnn["melhor_epoca"], "seg_por_epoca": eps,
                  "seg_treino": float(sum(eps)),
                  "seg_total": mtime(RUN / "resultado_protocolo.json") - mtime(RUNS / "cnn_stderr.txt"),
                  "img_por_seg_treino": cnn["n_treino_usado"] / float(np.mean(eps)),
                  "gpu": "NVIDIA RTX 4060 8 GB", "batch": cnn["args"]["bs"], "workers": cnn["args"]["workers"],
                  "fonte": "cnn.json (historico.seg) e carimbos de data"}
    pngs = sorted((RUN / "gradcam").glob("*.png"), key=mtime)
    out["gradcam"] = {"seg": mtime(RUN / "gradcam_resumo.json") - mtime(pngs[0]) if pngs else None,
                      "imagens": len(pngs), "fonte": "carimbos de data em runs\\...\\gradcam"}
    (ANALISE / "tempos.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def fig_tempos(t: dict) -> None:
    etapas = [("Extração das 73 features\n(24.998 imagens, CPU)", t["extracao_features"]["seg"]),
              ("EDA", t["eda"]["seg"]),
              ("7 modelos clássicos\n(CV, LOTO, grade, holdout)", t["modelagem"]["seg"]),
              (f"CNN: {t['cnn']['epocas']} épocas\n(GPU, com avaliação)", t["cnn"]["seg_total"])]
    fig, ax = plt.subplots(figsize=(10, 3.8))
    nomes = [e[0] for e in etapas][::-1]
    mins = [e[1] / 60 for e in etapas][::-1]
    b = ax.barh(nomes, mins, color=[COR["azul"], COR["azul"], COR["cinza"], COR["laranja"]][::-1])
    ax.bar_label(b, [f"{m:.1f} min".replace(".", ",") if m >= 1 else f"{m * 60:.0f} s" for m in mins], padding=4)
    ax.set_xlabel("minutos")
    ax.set_title("Quanto tempo cada etapa levou nesta máquina")
    ax.set_xlim(0, max(mins) * 1.18)
    salvar(fig, "tempos")


def fig_cnn_treino() -> None:
    cnn = json.loads((ANALISE / "cnn.json").read_text(encoding="utf-8"))
    h = pd.DataFrame(cnn["historico"])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.9))
    a1.plot(h.epoca, h.val_id_auc, "o-", color=COR["azul"], lw=2.2)
    a1.axvline(cnn["melhor_epoca"], color=COR["ink"], ls=":", lw=1)
    a1.annotate("melhor época\n(pesos usados)", (cnn["melhor_epoca"], h.val_id_auc.max()),
                xytext=(10, -40), textcoords="offset points", fontsize=10)
    a1.set_ylim(0.999, 1.0)
    a1.set_xlabel("época")
    a1.set_ylabel("ROC-AUC na validação ID")
    a1.set_title("AUC por época (early stopping, paciência 3)")
    a2.plot(h.epoca, h.perda_treino, "o-", color=COR["laranja"], lw=2.2)
    a2.set_xlabel("época")
    a2.set_ylabel("perda de treino (BCE)")
    a2.set_title("Perda de treino por época")
    fig.tight_layout()
    salvar(fig, "cnn_treino")


def fig_cnn_escores() -> None:
    p = pd.read_csv(RUN / "previsoes_validacao.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.9), sharey=True)
    bins = np.linspace(0, 1, 41)
    for ax, (conj, nome) in zip(axes, (("ID", "validação ID (tipos vistos)"), ("OOD", "OOD (Moçambique)"))):
        g = p[p.conjunto == conj]
        for lab, rot, cor in ((0, "legítimo", COR["legitimo"]), (1, "fraude", COR["fraude"])):
            v = g.loc[g.label == lab, "prob"]
            ax.hist(v, bins=bins, color=cor, alpha=0.6, label=rot, weights=np.ones(len(v)) / len(v))
        ax.axvline(0.5, color=COR["ink"], ls=":", lw=1)
        ax.set_title(nome)
        ax.set_xlabel("P(fraude) dada pela CNN")
    axes[0].set_ylabel("fração das imagens da classe")
    axes[0].legend()
    fig.suptitle("No tipo novo, os legítimos também recebem escore alto", y=1.03)
    fig.tight_layout()
    salvar(fig, "cnn_escores")


def fig_gradcam() -> None:
    r = json.loads((ANALISE / "gradcam_resumo.json").read_text(encoding="utf-8"))
    grupos = ["ID_acerto", "ID_erro", "OOD_acerto", "OOD_erro"]
    rot = [g.replace("_", "\n").replace("acerto", "acertos").replace("erro", "erros") +
           f" (n={r['grupos'][g]['n']})" for g in grupos]
    borda = [r["grupos"][g]["borda_10pct"] for g in grupos]
    fig, ax = plt.subplots(figsize=(9, 3.8))
    b = ax.bar(rot, borda, color=[COR["azul"], COR["azul"], COR["laranja"], COR["laranja"]])
    ax.bar_label(b, [f"{v:.2f}".replace(".", ",") for v in borda], padding=3)
    ax.axhline(r["borda_se_mapa_uniforme"], color=COR["ink"], ls="--", lw=1.2,
               label="se o mapa fosse uniforme (0,36)")
    ax.set_ylim(0, 0.7)
    ax.set_ylabel("fração do Grad-CAM na borda de 10%")
    ax.set_title("A CNN não se apoia na borda da foto")
    ax.legend(loc="upper right")
    salvar(fig, "gradcam_borda")


def main():
    aplicar()
    t = tempos()
    print(json.dumps(t, indent=2, ensure_ascii=False))
    fig_tempos(t)
    fig_cnn_treino()
    fig_cnn_escores()
    fig_gradcam()


if __name__ == "__main__":
    main()
