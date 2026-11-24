"""Diagnóstico da CNN depois do treino: AUC por tipo (ID) e deslocamento do escore no OOD.

Lê C:\\freuid\\runs\\ood_efficientnet_b0\\previsoes_validacao.csv (fora do git) e grava só números
agregados em reports/analise/cnn_diagnostico.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_auc_score

from config import ANALISE, NOMES_PAIS

RUN = Path(r"C:\freuid\runs\ood_efficientnet_b0")


def main():
    p = pd.read_csv(RUN / "previsoes_validacao.csv")
    res = json.loads((RUN / "resultado_protocolo.json").read_text(encoding="utf-8"))
    out = {"limiar_custo_id": res["limiar_custo"], "auc_por_tipo_id": {}, "escore_ood": {}}
    vid = p[p.conjunto == "ID"]
    for t, g in vid.groupby("type"):
        out["auc_por_tipo_id"][NOMES_PAIS[t]] = {"n": int(len(g)), "auc": float(roc_auc_score(g.label, g.prob))}
    for conj, g in p.groupby("conjunto"):
        d = {}
        for lab, nome in ((0, "legitimo"), (1, "fraude")):
            q = g.loc[g.label == lab, "prob"].quantile([0.05, 0.25, 0.5, 0.75, 0.95])
            d[nome] = {"quantis_5_25_50_75_95": [float(v) for v in q]}
        d["frac_legitimos_com_p_maior_0_5"] = float((g.loc[g.label == 0, "prob"] >= 0.5).mean())
        out["escore_ood" if conj == "OOD" else "escore_id"] = d
    # Limiar que daria 1% de BPCER se fosse escolhido com rótulos do próprio tipo novo (diagnóstico,
    # não é protocolo: usa rótulos do OOD). Mostra o quanto o limiar herdado do ID está deslocado.
    o = p[p.conjunto == "OOD"]
    t1 = float(np.quantile(o.loc[o.label == 0, "prob"], 0.99))
    tn, fp, fn, tp = confusion_matrix(o.label, (o.prob > t1).astype(int), labels=[0, 1]).ravel()
    out["ood_limiar_para_1pct_bpcer_diagnostico"] = {
        "limiar": t1, "vn": int(tn), "fp": int(fp), "fn": int(fn), "vp": int(tp),
        "recall": float(tp / (tp + fn)), "bpcer": float(fp / (fp + tn)),
        "aviso": "usa rótulos do OOD; serve só para mostrar o deslocamento do escore, não é resultado do protocolo"}
    # Bootstrap pareado (mesmos ids reamostrados) da diferença de AUC CNN − clássico, no ID e no OOD.
    from config import DATA

    cls = pd.read_csv(DATA / "previsoes_classicos.csv")
    rng = np.random.default_rng(42)
    out["bootstrap_auc"] = {"reamostragens": 1000, "semente": 42}
    for conj, sp in (("ID", "id"), ("OOD", "ood")):
        c = p[p.conjunto == conj][["id", "label", "prob"]]
        for nome in ("Regressão logística", "Random Forest"):
            m = cls[(cls.split == sp) & (cls.modelo == nome)][["id", "prob"]].rename(columns={"prob": "p_cls"})
            d = c.merge(m, on="id", validate="1:1")
            assert len(d) == len(c)
            y, a, b = d.label.to_numpy(), d.prob.to_numpy(), d.p_cls.to_numpy()
            difs = []
            for _ in range(1000):
                i = rng.integers(0, len(y), len(y))
                if y[i].min() == y[i].max():
                    continue
                difs.append(roc_auc_score(y[i], a[i]) - roc_auc_score(y[i], b[i]))
            out["bootstrap_auc"][f"{conj}: EfficientNet − {nome}"] = {
                "n": int(len(y)), "dif": float(roc_auc_score(y, a) - roc_auc_score(y, b)),
                "ic95": [float(np.percentile(difs, 2.5)), float(np.percentile(difs, 97.5))]}
    (ANALISE / "cnn_diagnostico.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
