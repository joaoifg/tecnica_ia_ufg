"""Passo 4: EfficientNet-B0 no MESMO split dos modelos clássicos (src/protocolo.py).

- Treino = split "treino"; early stopping pela ROC-AUC da validação ID; OOD = MOZAMBIQUE/DL.
- Reaproveita de src/cnn.py: Docs (leitura + augmentation de recaptura), carregar, prever.
- Checkpoint a cada época (ultimo.pt) para retomar com --retomar se a máquina cair.
- Pesos, log, previsões e JSON completo ficam em C:\\freuid\\runs\\ood_efficientnet_b0\\ (fora do git).
- No repositório entram só métricas agregadas (reports/analise/cnn.json) e figuras sem imagem
  de documento (reports/figs/cnn_*.png).
- Não prevê teste público/privado nem gera submissão.

Uso:
  python src/cnn_protocolo.py --epocas 10 --paciencia 3 --bs 16 --workers 2
  python src/cnn_protocolo.py --epocas 10 --paciencia 3 --bs 16 --workers 2 --retomar
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import timm
import torch
import torch.nn as nn
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, roc_curve

from cnn import Docs, carregar, prever
from config import ANALISE, RANDOM_SEED
from metric import freuid_breakdown
from protocolo import carregar_split, resumo_split

CUSTO_FN, CUSTO_FP = 5, 1


def metricas(y, p, limiar: float = 0.5) -> dict:
    y, p = np.asarray(y).astype(int), np.asarray(p)
    m = freuid_breakdown(y, p)
    pred = (p >= limiar).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {"n": int(len(y)), "auc": m["roc_auc"], "audet": m["audet"], "apcer_1pct_bpcer": m["apcer_at_1pct_bpcer"],
            "tpr_1pct": m["tpr_at_1pct_fpr"], "freuid": m["freuid_score"], "limiar": float(limiar),
            "acuracia": float((pred == y).mean()), "precisao": float(precision_score(y, pred, zero_division=0)),
            "recall": float(recall_score(y, pred, zero_division=0)), "f1": float(f1_score(y, pred, zero_division=0)),
            "vn": int(tn), "fp": int(fp), "fn": int(fn), "vp": int(tp), "custo": int(CUSTO_FN * fn + CUSTO_FP * fp)}


def limiar_por_custo(y, p) -> float:
    grade = np.linspace(0.02, 0.98, 97)
    custos = []
    for t in grade:
        tn, fp, fn, tp = confusion_matrix(y, (p >= t).astype(int), labels=[0, 1]).ravel()
        custos.append(CUSTO_FN * fn + CUSTO_FP * fp)
    return float(grade[int(np.argmin(custos))])


def figuras(y_id, p_id, y_ood, p_ood, t_custo):
    from estilo import COR, aplicar, salvar
    import matplotlib.pyplot as plt
    from scipy.stats import norm

    aplicar()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6))
    for y, p, nome, cor in ((y_id, p_id, "validação ID", COR["azul"]), (y_ood, p_ood, "OOD (Moçambique)", COR["laranja"])):
        fpr, tpr, _ = roc_curve(y, p)
        auc = freuid_breakdown(y, p)["roc_auc"]
        a1.plot(fpr, tpr, color=cor, lw=2.2, label=f"{nome}: AUC {auc:.3f}".replace(".", ","))
        bp = np.clip(fpr, 1e-4, 1 - 1e-4)
        ap = np.clip(1 - tpr, 1e-4, 1 - 1e-4)
        a2.plot(norm.ppf(bp), norm.ppf(ap), color=cor, lw=2.2, label=nome)
    a1.plot([0, 1], [0, 1], ":", color="grey", lw=1)
    a1.set_xlabel("taxa de legítimos barrados (BPCER)")
    a1.set_ylabel("taxa de fraudes detectadas (1 − APCER)")
    a1.set_title("Curva ROC — EfficientNet-B0")
    a1.legend(loc="lower right")
    marcas = [0.001, 0.01, 0.05, 0.2, 0.5]
    a2.set_xticks(norm.ppf(marcas), [f"{100 * m:g}%".replace(".", ",") for m in marcas])
    a2.set_yticks(norm.ppf(marcas), [f"{100 * m:g}%".replace(".", ",") for m in marcas])
    a2.axvline(norm.ppf(0.01), color=COR["ink"], ls=":", lw=1)
    a2.set_xlabel("BPCER (legítimos barrados)")
    a2.set_ylabel("APCER (fraudes que passam)")
    a2.set_title("Curva DET (linha pontilhada = 1% BPCER)")
    a2.legend(loc="upper right")
    fig.tight_layout()
    salvar(fig, "cnn_roc_det")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    for ax, (y, p, nome) in zip(axes, ((y_id, p_id, "validação ID"), (y_ood, p_ood, "OOD (Moçambique)"))):
        cm = confusion_matrix(y, (p >= t_custo).astype(int), labels=[0, 1])
        ax.imshow(cm, cmap="Blues")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{cm[i, j]}", ha="center", va="center", fontsize=15,
                        color="white" if cm[i, j] > cm.max() / 2 else COR["ink"])
        ax.set_xticks([0, 1], ["previsto legítimo", "previsto fraude"])
        ax.set_yticks([0, 1], ["legítimo", "fraude"])
        ax.set_ylabel("rótulo verdadeiro")
        ax.set_title(f"{nome} — limiar de custo {t_custo:.2f}".replace(".", ","))
    fig.tight_layout()
    salvar(fig, "cnn_matriz")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arq", default="efficientnet_b0")
    ap.add_argument("--epocas", type=int, default=10)
    ap.add_argument("--paciencia", type=int, default=3)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--max-treino", type=int, default=0, help="só para teste rápido")
    ap.add_argument("--retomar", action="store_true")
    ap.add_argument("--saida", default=r"C:\freuid\runs\ood_efficientnet_b0")
    args = ap.parse_args()

    random.seed(RANDOM_SEED), np.random.seed(RANDOM_SEED), torch.manual_seed(RANDOM_SEED)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)
    arq_log = open(saida / "log_protocolo.txt", "a", encoding="utf-8")

    def log(msg):
        print(msg, flush=True)
        arq_log.write(msg + "\n")
        arq_log.flush()

    split = carregar_split(salvar=False)
    tr = split[split.split == "treino"]
    if args.max_treino:
        tr = tr.sample(min(args.max_treino, len(tr)), random_state=RANDOM_SEED)
    va = split[split.split == "val_id"]
    ood = split[split.split == "ood"]
    log(f"dispositivo={dev} args={vars(args)}")
    log(f"universo={len(split)} treino={len(tr)} val_id={len(va)} ood={len(ood)}")

    modelo = timm.create_model(args.arq, pretrained=True, num_classes=1).to(dev)
    opt = torch.optim.AdamW(modelo.parameters(), lr=args.lr, weight_decay=1e-2)
    dl_tr = carregar(Docs(tr.arquivo, tr.label, True), args.bs, True, args.workers)
    dl_va = carregar(Docs(va.arquivo, va.label, False), args.bs * 2, False, args.workers)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, args.lr, total_steps=args.epocas * len(dl_tr), pct_start=0.1)
    scaler = torch.amp.GradScaler(enabled=dev.type == "cuda")
    perda_fn = nn.BCEWithLogitsLoss()
    hist, melhor_auc, melhor_ep, ep0 = [], -1.0, 0, 0
    ck = saida / "ultimo.pt"
    if args.retomar and ck.exists():
        st = torch.load(ck, map_location=dev, weights_only=False)
        modelo.load_state_dict(st["modelo"]), opt.load_state_dict(st["opt"])
        sched.load_state_dict(st["sched"]), scaler.load_state_dict(st["scaler"])
        hist, melhor_auc, melhor_ep, ep0 = st["hist"], st["melhor_auc"], st["melhor_ep"], st["epoca"]
        log(f"retomando depois da época {ep0} (melhor AUC ID {melhor_auc:.4f} na época {melhor_ep})")

    for ep in range(ep0, args.epocas):
        if ep - melhor_ep >= args.paciencia and melhor_ep > 0:
            log(f"early stopping: {args.paciencia} épocas sem melhorar")
            break
        modelo.train()
        t0, soma, n = time.time(), 0.0, 0
        for i, (x, y) in enumerate(dl_tr):
            x, y = x.to(dev, non_blocking=True), y.to(dev)
            with torch.autocast(dev.type, dtype=torch.float16, enabled=dev.type == "cuda"):
                perda = perda_fn(modelo(x).squeeze(1), y * 0.95 + 0.025)
            opt.zero_grad(set_to_none=True)
            scaler.scale(perda).backward()
            scaler.step(opt)
            scaler.update()
            sched.step()
            soma, n = soma + perda.item() * len(y), n + len(y)
            if i % 200 == 0:
                log(f"  ep{ep + 1} {i}/{len(dl_tr)} perda={soma / n:.4f} {n / (time.time() - t0):.0f} img/s")
        p = prever(modelo, dl_va, dev)
        m = freuid_breakdown(va.label.to_numpy(), p)
        reg = {"epoca": ep + 1, "perda_treino": soma / n, "seg": time.time() - t0, "val_id_auc": m["roc_auc"],
               "val_id_freuid": m["freuid_score"]}
        if m["roc_auc"] > melhor_auc:
            melhor_auc, melhor_ep = m["roc_auc"], ep + 1
            torch.save(modelo.state_dict(), saida / "modelo_melhor.pt")
        reg["melhor_ep"] = melhor_ep
        hist.append(reg)
        log(json.dumps(reg))
        torch.save({"modelo": modelo.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(),
                    "scaler": scaler.state_dict(), "hist": hist, "melhor_auc": melhor_auc, "melhor_ep": melhor_ep,
                    "epoca": ep + 1}, ck)

    modelo.load_state_dict(torch.load(saida / "modelo_melhor.pt", map_location=dev))
    p_id = prever(modelo, dl_va, dev)
    p_ood = prever(modelo, carregar(Docs(ood.arquivo, ood.label, False), args.bs * 2, False, args.workers), dev)
    y_id, y_ood = va.label.to_numpy().astype(int), ood.label.to_numpy().astype(int)
    t_custo = limiar_por_custo(y_id, p_id)
    res = {
        "modelo": "EfficientNet-B0", "args": vars(args), "protocolo": resumo_split(split),
        "n_treino_usado": int(len(tr)), "historico": hist, "melhor_epoca": melhor_ep,
        "limiar_custo": t_custo,
        "observacao_limiar": "limiar de custo (5·FN + 1·FP) escolhido nas previsões da validação ID, que também "
                             "serviu ao early stopping: os números ID no limiar de custo são otimistas; os OOD não.",
        "holdout": {
            "id": {"limiar_0.5": metricas(y_id, p_id, 0.5), "limiar_custo": metricas(y_id, p_id, t_custo)},
            "ood": {"limiar_0.5": metricas(y_ood, p_ood, 0.5), "limiar_custo": metricas(y_ood, p_ood, t_custo)},
        },
    }
    pd.concat([va.assign(prob=p_id, conjunto="ID"), ood.assign(prob=p_ood, conjunto="OOD")])[
        ["id", "label", "is_digital", "type", "conjunto", "prob"]].to_csv(saida / "previsoes_validacao.csv", index=False)
    (saida / "resultado_protocolo.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    ANALISE.mkdir(parents=True, exist_ok=True)
    (ANALISE / "cnn.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    figuras(y_id, p_id, y_ood, p_ood, t_custo)
    for s in ("id", "ood"):
        r = res["holdout"][s]["limiar_custo"]
        log(f"{s}: AUC={r['auc']:.4f} FREUID={r['freuid']:.4f} APCER@1%={r['apcer_1pct_bpcer']:.4f} "
            f"recall_custo={r['recall']:.4f}")
    log("OK")


if __name__ == "__main__":
    main()
