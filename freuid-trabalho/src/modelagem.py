"""Modelagem completa do FREUID com os modelos clássicos da disciplina.

Experimentos:
  1. Validação cruzada estratificada (5 folds) com 7 modelos.
  2. Conjunto de features: V1 (64) contra Completo (73).
  3. Leave-one-type-out: treina em 4 documentos, testa no 5º (5 rodadas).
  4. Ajuste de hiperparâmetros (curvas de validação + GridSearchCV por documento).
  5. Curva de aprendizado.
  6. Holdout final: ROC, precisão-revocação, matriz, limiar por custo, calibração.
  7. Importância das features por permutação.
  8. Erros por documento.
  9. Checagem de atalhos (shortcut): metadados, tipo do documento, ids repetidos.

Protocolo (src/protocolo.py): universo = amostra.csv ∩ JPEGs existentes; MOZAMBIQUE/DL fora
do treino (OOD); demais tipos 80/20 estratificado por label (treino / validação ID); semente 42.
Os experimentos 1, 2, 4 e 5 usam só o split de treino. O 3 (LOTO) usa o universo inteiro
porque precisa dos 5 tipos, e é reportado à parte. O holdout final (6-8) treina no split de
treino e avalia na validação ID e no OOD, com os mesmos ids da CNN.

Saídas: reports/figs/mod_*.png e reports/analise/modelagem.json
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import calibration_curve
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import (
    GridSearchCV,
    LeaveOneGroupOut,
    StratifiedKFold,
    cross_val_predict,
    cross_validate,
    learning_curve,
    train_test_split,
    validation_curve,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from config import ANALISE, JOBS, NOMES_PAIS, RANDOM_SEED
from protocolo import carregar_split, resumo_split
from estilo import COR, COR_FAMILIA, COR_MODELO, aplicar, salvar
from features import FEATURES, FEATURES_V1, build_feature_table, familia
from metric import freuid_breakdown

import matplotlib.pyplot as plt  # noqa: E402

CUSTO_FN = 5  # deixar uma fraude passar custa 5x mais
CUSTO_FP = 1  # que mandar um legítimo para conferência manual


def criar_modelos() -> dict:
    """Os modelos vistos na disciplina, mais um baseline que sempre chuta a classe maior."""
    escala = lambda m: Pipeline([("escala", StandardScaler()), ("modelo", m)])  # noqa: E731
    return {
        "Baseline": DummyClassifier(strategy="most_frequent"),
        "Regressão logística": escala(LogisticRegression(max_iter=5000, class_weight="balanced")),
        "KNN": escala(KNeighborsClassifier(n_neighbors=15, weights="distance")),
        "Naive Bayes": escala(GaussianNB()),
        "Árvore de decisão": DecisionTreeClassifier(max_depth=8, min_samples_leaf=5,
                                                    class_weight="balanced", random_state=RANDOM_SEED),
        "Random Forest": RandomForestClassifier(n_estimators=400, min_samples_leaf=2, n_jobs=JOBS,
                                                class_weight="balanced_subsample", random_state=RANDOM_SEED),
        "Gradient Boosting": HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05,
                                                            class_weight="balanced", random_state=RANDOM_SEED),
    }


def metricas(y, prob, limiar: float = 0.5) -> dict:
    pred = (prob >= limiar).astype(int)
    m = freuid_breakdown(y, prob) if len(np.unique(y)) > 1 else {}
    return {
        "auc": float(m.get("roc_auc", np.nan)),
        "freuid": float(m.get("freuid_score", np.nan)),
        "tpr_1pct": float(m.get("tpr_at_1pct_fpr", np.nan)),
        "audet": float(m.get("audet", np.nan)),
        "apcer_1pct_bpcer": float(m.get("apcer_at_1pct_bpcer", np.nan)),
        "acuracia": float((pred == y).mean()),
        "precisao": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
    }


# ------------------------------------------------------------------ 1
def exp_cv(X, y, modelos, out):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    scoring = {"auc": "roc_auc", "acuracia": "accuracy", "precisao": "precision",
               "recall": "recall", "f1": "f1", "bal_acc": "balanced_accuracy"}
    res, folds = {}, {}
    for nome, m in modelos.items():
        t0 = time.time()
        r = cross_validate(m, X, y, cv=cv, scoring=scoring, n_jobs=1)
        res[nome] = {k: {"media": float(r[f"test_{k}"].mean()), "desvio": float(r[f"test_{k}"].std())} for k in scoring}
        res[nome]["segundos"] = round(time.time() - t0, 1)
        folds[nome] = r["test_auc"].tolist()
        print(f"  CV {nome:22s} AUC={res[nome]['auc']['media']:.3f}±{res[nome]['auc']['desvio']:.3f}")
    out["cv"] = res
    out["cv_folds_auc"] = folds

    ordem = sorted(folds, key=lambda k: np.mean(folds[k]))
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for i, nome in enumerate(ordem):
        v = folds[nome]
        ax.barh(i, np.mean(v), color=COR_MODELO[nome], height=0.6, alpha=0.9)
        ax.scatter(v, [i] * len(v), color=COR["ink"], s=14, zorder=3)
        ax.text(np.mean(v) + 0.012, i, f"{np.mean(v):.3f}".replace(".", ","), va="center", fontsize=10,
                fontweight="bold", color=COR["ink"])
    ax.set_yticks(range(len(ordem)), ordem)
    ax.axvline(0.5, color=COR["ink"], ls="--", lw=1)
    ax.set_xlim(0.4, 1.03)
    ax.set_xlabel("ROC-AUC (barra = média · pontos = cada um dos 5 folds)")
    ax.set_title("Validação cruzada estratificada, 5 folds")
    ax.grid(axis="y", visible=False)
    salvar(fig, "mod_cv")


# ------------------------------------------------------------------ 2
def exp_conjuntos(tab, y, modelos, out):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    res = {}
    for nome in ("Regressão logística", "Random Forest", "Gradient Boosting"):
        res[nome] = {}
        for rotulo, cols in (("V1 (64)", FEATURES_V1), ("Completo (73)", FEATURES)):
            s = cross_validate(modelos[nome], tab[cols].to_numpy(), y, cv=cv, scoring="roc_auc")["test_score"]
            res[nome][rotulo] = {"media": float(s.mean()), "desvio": float(s.std())}
    out["conjuntos"] = res

    fig, ax = plt.subplots(figsize=(8, 3.8))
    nomes = list(res)
    x = np.arange(len(nomes))
    for j, (rot, c) in enumerate((("V1 (64)", COR["cinza"]), ("Completo (73)", COR["roxo"]))):
        v = [res[n][rot]["media"] for n in nomes]
        e = [res[n][rot]["desvio"] for n in nomes]
        ax.bar(x + (j - 0.5) * 0.36, v, 0.34, yerr=e, color=c, label=rot, capsize=4)
        for xi, vi in zip(x, v):
            ax.text(xi + (j - 0.5) * 0.36, vi + 0.02, f"{vi:.3f}".replace(".", ","), ha="center", fontsize=9.5)
    ax.set_xticks(x, nomes)
    ax.set_ylim(0.5, 1.05)
    ax.set_ylabel("ROC-AUC (CV 5 folds)")
    ax.set_title("Vale a pena adicionar as features de perícia?")
    ax.legend(loc="upper left", ncol=2)
    salvar(fig, "mod_conjuntos")


# ------------------------------------------------------------------ 3
def exp_loto(X, y, grupos, modelos, out):
    """Leave-one-type-out: cada documento vira, uma vez, o documento 'nunca visto'."""
    logo = LeaveOneGroupOut()
    tipos = [t for t in NOMES_PAIS if t in set(grupos)]
    res = {n: {} for n in modelos}
    for tr, te in logo.split(X, y, grupos):
        tipo = grupos[te][0]
        for nome, m in modelos.items():
            mod = clone(m).fit(X[tr], y[tr])
            prob = mod.predict_proba(X[te])[:, 1]
            res[nome][NOMES_PAIS[tipo]] = metricas(y[te], prob)
    for nome in res:
        aucs = [res[nome][NOMES_PAIS[t]]["auc"] for t in tipos]
        fr = [res[nome][NOMES_PAIS[t]]["freuid"] for t in tipos]
        res[nome]["_media"] = {"auc": float(np.nanmean(aucs)), "freuid": float(np.nanmean(fr)),
                               "acuracia": float(np.mean([res[nome][NOMES_PAIS[t]]["acuracia"] for t in tipos])),
                               "recall": float(np.mean([res[nome][NOMES_PAIS[t]]["recall"] for t in tipos]))}
        print(f"  LOTO {nome:22s} AUC média={res[nome]['_media']['auc']:.3f}")
    out["loto"] = res

    # heatmap modelos × documento
    nomes = [n for n in modelos if n != "Baseline"]
    paises = [NOMES_PAIS[t] for t in tipos]
    M = np.array([[res[n][p]["auc"] for p in paises] + [res[n]["_media"]["auc"]] for n in nomes])
    fig, ax = plt.subplots(figsize=(10, 4.6))
    im = ax.imshow(M, cmap="RdYlGn", vmin=0.4, vmax=1.0, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, f"{M[i, j]:.2f}".replace(".", ","), ha="center", va="center", fontsize=11,
                    fontweight="bold" if j == M.shape[1] - 1 else "normal", color=COR["ink"])
    ax.set_xticks(range(len(paises) + 1), paises + ["MÉDIA"])
    ax.set_yticks(range(len(nomes)), nomes)
    ax.axvline(len(paises) - 0.5, color="white", lw=3)
    ax.grid(False)
    ax.set_title("ROC-AUC no documento deixado de fora do treino")
    fig.colorbar(im, ax=ax, shrink=0.85)
    salvar(fig, "mod_loto_heatmap")

    # CV × LOTO: o tamanho da queda
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ordem = sorted(nomes, key=lambda n: out["cv"][n]["auc"]["media"])
    for i, n in enumerate(ordem):
        a, b = out["cv"][n]["auc"]["media"], res[n]["_media"]["auc"]
        ax.plot([b, a], [i, i], color=COR["line"], lw=5, zorder=1)
        ax.scatter([a], [i], s=90, color=COR["azul"], zorder=3, label="Validação cruzada (documentos vistos)" if i == 0 else None)
        ax.scatter([b], [i], s=90, color=COR["fraude"], zorder=3, label="Documento nunca visto (LOTO)" if i == 0 else None)
        ax.text(a + 0.012, i, f"{a:.2f}".replace(".", ","), va="center", fontsize=9.5, color=COR["azul"])
        ax.text(b - 0.012, i, f"{b:.2f}".replace(".", ","), va="center", ha="right", fontsize=9.5, color=COR["fraude"])
    ax.set_yticks(range(len(ordem)), ordem)
    ax.axvline(0.5, color=COR["ink"], ls="--", lw=1)
    ax.set_xlim(0.35, 1.05)
    ax.set_xlabel("ROC-AUC")
    ax.set_title("Quanto cada modelo perde num documento novo")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="y", visible=False)
    salvar(fig, "mod_cv_vs_loto")


# ------------------------------------------------------------------ 4
def exp_hiperparametros(X, y, grupos, out):
    logo = LeaveOneGroupOut()
    res = {}
    fig, axes = plt.subplots(1, 3, figsize=(14, 3.8))

    curvas = [
        ("Regressão logística", Pipeline([("escala", StandardScaler()),
                                          ("modelo", LogisticRegression(max_iter=5000, class_weight="balanced"))]),
         "modelo__C", np.logspace(-3, 2, 8), "C (força da regularização inversa)", True),
        ("KNN", Pipeline([("escala", StandardScaler()), ("modelo", KNeighborsClassifier(weights="distance"))]),
         "modelo__n_neighbors", np.array([1, 3, 5, 9, 15, 25, 41, 61]), "k (número de vizinhos)", False),
        ("Árvore de decisão", DecisionTreeClassifier(class_weight="balanced", min_samples_leaf=5, random_state=RANDOM_SEED),
         "max_depth", np.array([1, 2, 3, 4, 6, 8, 12, 16, 24]), "profundidade máxima", False),
    ]
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    for ax, (nome, est, param, grade, rotulo, log) in zip(axes, curvas):
        tr, va = validation_curve(est, X, y, param_name=param, param_range=grade, cv=cv, scoring="roc_auc", n_jobs=1)
        ax.plot(grade, tr.mean(1), "o-", color=COR["azul"], label="treino")
        ax.plot(grade, va.mean(1), "o-", color=COR["laranja"], label="validação")
        ax.fill_between(grade, va.mean(1) - va.std(1), va.mean(1) + va.std(1), color=COR["laranja"], alpha=0.15)
        melhor = grade[int(np.argmax(va.mean(1)))]
        ax.axvline(melhor, color=COR["ink"], ls=":", lw=1)
        if log:
            ax.set_xscale("log")
        ax.set_title(nome)
        ax.set_xlabel(rotulo)
        ax.set_ylim(0.45, 1.02)
        res[nome] = {"param": param, "melhor": float(melhor), "auc_valid": float(va.mean(1).max()),
                     "grade": grade.tolist(), "treino": tr.mean(1).tolist(), "validacao": va.mean(1).tolist()}
    axes[0].set_ylabel("ROC-AUC")
    axes[0].legend()
    fig.tight_layout()
    salvar(fig, "mod_curvas_validacao")

    # GridSearch da Random Forest usando 'documento nunca visto' como validação
    grade_rf = {"max_depth": [6, 12, None], "min_samples_leaf": [1, 3, 8], "max_features": ["sqrt", 0.5]}
    gs = GridSearchCV(RandomForestClassifier(n_estimators=250, class_weight="balanced_subsample",
                                             random_state=RANDOM_SEED, n_jobs=JOBS),
                      grade_rf, cv=logo, scoring="roc_auc", n_jobs=1)
    gs.fit(X, y, groups=grupos)
    res["grid_rf"] = {"melhores": {k: (v if v is not None else "None") for k, v in gs.best_params_.items()},
                      "auc_loto": float(gs.best_score_), "combinacoes": int(len(gs.cv_results_["params"]))}
    print(f"  GridSearch RF: {gs.best_params_} AUC LOTO={gs.best_score_:.3f}")
    out["hiper"] = res


# ------------------------------------------------------------------ 5
def exp_aprendizado(X, y, modelos, out):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    tamanhos = np.linspace(0.1, 1.0, 8)
    res = {}
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for nome in ("Regressão logística", "Random Forest", "Gradient Boosting"):
        n, tr, va = learning_curve(modelos[nome], X, y, train_sizes=tamanhos, cv=cv, scoring="roc_auc", n_jobs=1,
                                   shuffle=True, random_state=RANDOM_SEED)
        ax.plot(n, va.mean(1), "o-", color=COR_MODELO[nome], lw=2.2, label=f"{nome} (validação)")
        ax.plot(n, tr.mean(1), ":", color=COR_MODELO[nome], lw=1.5)
        res[nome] = {"n": n.tolist(), "treino": tr.mean(1).tolist(), "validacao": va.mean(1).tolist()}
    ax.set_xlabel("imagens de treino")
    ax.set_ylabel("ROC-AUC")
    ax.set_title("Curva de aprendizado (pontilhado = treino)")
    ax.legend(fontsize=9, loc="lower right")
    salvar(fig, "mod_aprendizado")
    out["aprendizado"] = res


# ------------------------------------------------------------------ 6
def limiar_por_custo(y, prob) -> tuple[float, list]:
    """Escolhe o corte que minimiza custo = 5·FN + 1·FP."""
    grade = np.linspace(0.02, 0.98, 97)
    custos = []
    for t in grade:
        tn, fp, fn, tp = confusion_matrix(y, (prob >= t).astype(int), labels=[0, 1]).ravel()
        custos.append(CUSTO_FN * fn + CUSTO_FP * fp)
    return float(grade[int(np.argmin(custos))]), custos


def limiares_oof(X, y, modelos) -> dict:
    """Limiar de custo de cada modelo, escolhido SEM olhar validação/OOD:
    previsões out-of-fold (5 folds) dentro do próprio split de treino."""
    cv = StratifiedKFold(5, shuffle=True, random_state=RANDOM_SEED)
    res = {}
    for nome, m in modelos.items():
        if nome == "Baseline":
            res[nome] = 0.5
            continue
        oof = cross_val_predict(m, X, y, cv=cv, method="predict_proba")[:, 1]
        res[nome] = limiar_por_custo(y, oof)[0]
    return res


def resumo_limiar(y, p, t) -> dict:
    cm = confusion_matrix(y, (p >= t).astype(int), labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    return {"limiar": float(t), "vn": int(tn), "fp": int(fp), "fn": int(fn), "vp": int(tp),
            "custo": int(CUSTO_FN * fn + CUSTO_FP * fp), **metricas(y, p, t)}


def exp_holdout(tab, X, y, modelos, out, nome_final, tr, te, rotulo, lim_custo, previsoes):
    """Treina no split de treino e avalia em `te` (validação ID ou OOD)."""
    sufixo = f"_{rotulo}"
    nome_split = {"id": "validação ID (tipos vistos)", "ood": "OOD (Moçambique, tipo nunca visto)"}[rotulo]
    res = out.setdefault("holdout", {})[rotulo] = {
        "split": nome_split, "n_treino": int(len(tr)), "n_teste": int(len(te)),
        "fraudes_teste": int(y[te].sum()), "legitimos_teste": int((y[te] == 0).sum()),
        "modelo_final": nome_final, "modelos": {}}
    probs = {}
    for nome, m in modelos.items():
        mod = clone(m).fit(X[tr], y[tr])
        probs[nome] = mod.predict_proba(X[te])[:, 1]
        r = metricas(y[te], probs[nome])
        r["ap"] = float(average_precision_score(y[te], probs[nome]))
        r["limiar_0_5"] = resumo_limiar(y[te], probs[nome], 0.5)
        r["limiar_custo"] = resumo_limiar(y[te], probs[nome], lim_custo[nome])
        res["modelos"][nome] = r
        previsoes.append(pd.DataFrame({"id": tab["id"].to_numpy()[te], "split": rotulo, "modelo": nome,
                                       "label": y[te], "prob": probs[nome]}))

    # ROC e precisão-revocação
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for nome, p in probs.items():
        if nome == "Baseline":
            continue
        fpr, tpr, _ = roc_curve(y[te], p)
        pr, rc, _ = precision_recall_curve(y[te], p)
        lw = 3 if nome == nome_final else 1.6
        axes[0].plot(fpr, tpr, color=COR_MODELO[nome], lw=lw,
                     label=f"{nome} ({res['modelos'][nome]['auc']:.3f})".replace(".", ","))
        axes[1].plot(rc, pr, color=COR_MODELO[nome], lw=lw,
                     label=f"{nome} ({res['modelos'][nome]['ap']:.3f})".replace(".", ","))
    axes[0].plot([0, 1], [0, 1], "--", color=COR["soft"], lw=1)
    axes[0].axvline(0.01, color=COR["fraude"], ls=":", lw=1)
    axes[0].set_xlabel("alarme falso (FPR)")
    axes[0].set_ylabel("fraudes pegas (TPR)")
    axes[0].set_title(f"Curva ROC (AUC) · {nome_split}, n = {len(te)}")
    axes[0].legend(fontsize=8.5, loc="lower right")
    axes[1].axhline(y[te].mean(), ls="--", color=COR["soft"], lw=1)
    axes[1].set_xlabel("revocação")
    axes[1].set_ylabel("precisão")
    axes[1].set_title(f"Precisão-revocação (AP) · n = {len(te)}")
    axes[1].legend(fontsize=8.5, loc="lower left")
    fig.tight_layout()
    salvar(fig, "mod_roc_pr" + sufixo)

    # limiar escolhido SEM olhar o teste: previsões out-of-fold no treino (ver limiares_oof)
    final = modelos[nome_final]
    t_custo = lim_custo[nome_final]
    p = probs[nome_final]
    res["limiares"] = {"0,5": res["modelos"][nome_final]["limiar_0_5"],
                       "custo": res["modelos"][nome_final]["limiar_custo"]}

    # matrizes de confusão da logística e da floresta no limiar de custo
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.3))
    for ax, nome in zip(axes, ("Regressão logística", "Random Forest")):
        d = res["modelos"][nome]["limiar_custo"]
        M = np.array([[d["vn"], d["fp"]], [d["fn"], d["vp"]]])
        ax.imshow(M, cmap="Blues", vmin=0, vmax=max(1, M.max()))
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(M[i, j]), ha="center", va="center", fontsize=18, fontweight="bold",
                        color="white" if M[i, j] > M.max() / 2 else COR["ink"])
        ax.set_xticks([0, 1], ["previu legítimo", "previu fraude"])
        ax.set_yticks([0, 1], ["era legítimo", "era fraude"])
        ax.set_xlabel("previsão do modelo")
        ax.set_ylabel("rótulo verdadeiro")
        ax.grid(False)
        ax.set_title(f"{nome} · limiar {d['limiar']:.2f}".replace(".", ","), fontsize=11.5)
    fig.suptitle(f"Matriz de confusão no limiar de custo · {nome_split} (n = {len(te)})",
                 x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    salvar(fig, "mod_matriz" + sufixo)

    # curva do limiar
    grade = np.linspace(0.02, 0.98, 97)
    prec = [precision_score(y[te], (p >= t).astype(int), zero_division=1) for t in grade]
    rec = [recall_score(y[te], (p >= t).astype(int), zero_division=0) for t in grade]
    f1s = [f1_score(y[te], (p >= t).astype(int), zero_division=0) for t in grade]
    _, custos = limiar_por_custo(y[te], p)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(grade, prec, color=COR["azul"], lw=2.2, label="precisão")
    ax.plot(grade, rec, color=COR["fraude"], lw=2.2, label="revocação")
    ax.plot(grade, f1s, color=COR["gold"], lw=2.2, label="F1")
    ax2 = ax.twinx()
    ax2.plot(grade, custos, color=COR["ink"], lw=1.5, ls="--", label="custo (5·FN + FP)")
    ax2.set_ylabel("custo total", color=COR["ink"])
    ax2.grid(False)
    ax2.spines["right"].set_visible(True)
    ax.axvline(0.5, color=COR["soft"], lw=1)
    ax.axvline(t_custo, color=COR["legitimo"], lw=2)
    ax.text(t_custo + 0.01, 0.04, f"limiar por custo = {t_custo:.2f}".replace(".", ","), color=COR["legitimo"],
            fontsize=10, fontweight="bold")
    ax.set_xlabel("limiar de decisão (risco ≥ limiar → fraude)")
    ax.set_ylim(0, 1.02)
    ax.set_title(f"{nome_final}: efeito do limiar · {nome_split}")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="center left", fontsize=9)
    salvar(fig, "mod_limiar" + sufixo)

    # calibração
    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    ax.plot([0, 1], [0, 1], "--", color=COR["soft"], lw=1, label="perfeitamente calibrado")
    calib = {}
    for nome in ("Regressão logística", "Random Forest", "Gradient Boosting", "Naive Bayes"):
        fr, mp = calibration_curve(y[te], probs[nome], n_bins=8, strategy="quantile")
        ax.plot(mp, fr, "o-", color=COR_MODELO[nome], lw=2, ms=4, label=nome)
        calib[nome] = float(np.mean(np.abs(fr - mp)))
    ax.set_xlabel("risco previsto")
    ax.set_ylabel("fração real de fraudes")
    ax.set_title(f"Curva de calibração · {rotulo.upper()} (n = {len(te)})")
    ax.legend(fontsize=8.5)
    salvar(fig, "mod_calibracao" + sufixo)
    res["erro_calibracao"] = calib

    if rotulo == "id":
        _importancia(final, X, y, tr, te, nome_final, out)
    _erros_documento(tab, y, te, p, t_custo, nome_final, res, sufixo)


def _importancia(final, X, y, tr, te, nome_final, out):
    # importância por permutação (na validação ID)
    mod_final = clone(final).fit(X[tr], y[tr])
    pi = permutation_importance(mod_final, X[te], y[te], scoring="roc_auc", n_repeats=10,
                                random_state=RANDOM_SEED, n_jobs=1)
    imp = pd.DataFrame({"feature": FEATURES, "familia": [familia(f) for f in FEATURES],
                        "queda_auc": pi.importances_mean, "desvio": pi.importances_std})
    imp = imp.sort_values("queda_auc", ascending=False)
    imp.to_csv(ANALISE / "importancia_permutacao.csv", index=False)
    fam = imp.groupby("familia")["queda_auc"].sum().sort_values()
    out["importancia"] = {"top": imp.head(12).to_dict("records"), "por_familia": fam.to_dict()}
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1.4, 1]})
    top = imp.head(12).iloc[::-1]
    axes[0].barh(top["feature"], top["queda_auc"], xerr=top["desvio"], color=[COR_FAMILIA[f] for f in top["familia"]],
                 error_kw={"ecolor": COR["muted"], "lw": 1})
    axes[0].set_xlabel("queda na AUC ao embaralhar a feature")
    axes[0].set_title(f"Top 12 features ({nome_final}, permutação na validação ID)")
    axes[0].grid(axis="y", visible=False)
    axes[1].barh(fam.index, fam.values, color=[COR_FAMILIA[f] for f in fam.index])
    axes[1].set_xlabel("soma da queda na AUC")
    axes[1].set_title("Importância por família")
    axes[1].grid(axis="y", visible=False)
    fig.tight_layout()
    salvar(fig, "mod_importancia")



def _erros_documento(tab, y, te, p, t_custo, nome_final, res, sufixo):
    # erros por documento (teste)
    pred = (p >= t_custo).astype(int)
    df_te = tab.iloc[te].assign(pred=pred, y=y[te])
    erros = []
    for t, g in df_te.groupby("type"):
        fra = g[g.y == 1]
        leg = g[g.y == 0]
        erros.append({"pais": NOMES_PAIS[t], "n": int(len(g)),
                      "fraude_passou": float((fra.pred == 0).mean()) if len(fra) else 0.0,
                      "alarme_falso": float((leg.pred == 1).mean()) if len(leg) else 0.0})
    res["erros_por_documento"] = erros
    e = pd.DataFrame(erros).sort_values("fraude_passou")
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    yy = np.arange(len(e))
    ax.barh(yy + 0.2, e["fraude_passou"], 0.38, color=COR["fraude"], label="fraude que passou (FN)")
    ax.barh(yy - 0.2, e["alarme_falso"], 0.38, color=COR["laranja"], label="alarme falso (FP)")
    for i, (a, b) in enumerate(zip(e["fraude_passou"], e["alarme_falso"])):
        ax.text(a + 0.005, i + 0.2, f"{a:.0%}", va="center", fontsize=9.5)
        ax.text(b + 0.005, i - 0.2, f"{b:.0%}", va="center", fontsize=9.5)
    ax.set_yticks(yy, e["pais"])
    ax.set_xlabel("taxa de erro no teste")
    ax.set_title(f"Onde o modelo erra ({nome_final}, limiar por custo, {sufixo[1:].upper()})")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="y", visible=False)
    ax.set_ylabel("documento")
    salvar(fig, "mod_erros_documento" + sufixo)


# ------------------------------------------------------------------ 9
def exp_atalhos(tab, X, y, tr, te_id, te_ood, out):
    """Procura atalhos (shortcut learning): sinais que dão AUC alta sem ter a ver com fraude."""
    res = {}
    ids = tab["id"].to_numpy()
    res["ids_compartilhados"] = {
        "treino_val_id": int(len(set(ids[tr]) & set(ids[te_id]))),
        "treino_ood": int(len(set(ids[tr]) & set(ids[te_ood]))),
        "val_id_ood": int(len(set(ids[te_id]) & set(ids[te_ood]))),
    }
    # (a) só metadados do arquivo (largura, altura, tamanho em KB)
    meta = tab[["largura", "altura", "tamanho_kb"]].to_numpy()
    lr = Pipeline([("escala", StandardScaler()), ("modelo", LogisticRegression(max_iter=5000))])
    mod = clone(lr).fit(meta[tr], y[tr])
    res["so_metadados_auc"] = {"id": float(roc_auc_score(y[te_id], mod.predict_proba(meta[te_id])[:, 1])),
                               "ood": float(roc_auc_score(y[te_ood], mod.predict_proba(meta[te_ood])[:, 1]))}
    # (b) só o tipo do documento (one-hot) — mede quanto o "prior" do país ajuda
    tipos = pd.get_dummies(tab["type"]).to_numpy(float)
    mod = LogisticRegression(max_iter=5000).fit(tipos[tr], y[tr])
    res["so_tipo_auc_id"] = float(roc_auc_score(y[te_id], mod.predict_proba(tipos[te_id])[:, 1]))
    # (c) as 73 features conseguem dizer QUAL é o documento? (acurácia em 5 folds, universo inteiro)
    cv = StratifiedKFold(5, shuffle=True, random_state=RANDOM_SEED)
    acc_tipo = cross_validate(RandomForestClassifier(n_estimators=300, random_state=RANDOM_SEED, n_jobs=JOBS),
                              X, tab["type"].to_numpy(), cv=cv, scoring="accuracy")["test_score"]
    res["acuracia_prever_tipo_pelas_features"] = {"media": float(acc_tipo.mean()), "chance": float(
        tab["type"].value_counts(normalize=True).max())}
    # (d) algum AUC acima de 0,98?
    altos = []
    for split in ("id", "ood"):
        for nome, r in out["holdout"][split]["modelos"].items():
            if r["auc"] > 0.98:
                altos.append(f"{nome}/{split}: {r['auc']:.3f}")
    res["auc_acima_0_98"] = altos
    out["atalhos"] = res
    print("  atalhos:", json.dumps(res, ensure_ascii=False))


def main() -> None:
    aplicar()
    ANALISE.mkdir(parents=True, exist_ok=True)
    split = carregar_split()
    tab = build_feature_table(split)
    tab = tab.merge(split[["id", "split"]], on="id", how="left", validate="1:1")
    assert tab["split"].notna().all() and len(tab) == len(split)
    X = tab[FEATURES].to_numpy()
    y = tab["label"].to_numpy().astype(int)
    grupos = tab["type"].to_numpy()
    tr = np.flatnonzero(tab["split"] == "treino")
    te_id = np.flatnonzero(tab["split"] == "val_id")
    te_ood = np.flatnonzero(tab["split"] == "ood")
    modelos = criar_modelos()
    out = {"n": int(len(y)), "n_features": len(FEATURES), "pct_fraude": float(y.mean()),
           "custo_fn": CUSTO_FN, "custo_fp": CUSTO_FP, "protocolo": resumo_split(split),
           "observacao": "Experimentos 1, 2, 4 e 5 usam só o split de treino; LOTO usa o universo inteiro; "
                         "holdout treina no split de treino e avalia em val_id e ood."}
    Xtr, ytr, gtr = X[tr], y[tr], grupos[tr]

    print(f"universo={len(y)} treino={len(tr)} val_id={len(te_id)} ood={len(te_ood)}")
    print("1. validação cruzada (split de treino)")
    exp_cv(Xtr, ytr, modelos, out)
    print("2. conjuntos de features (split de treino)")
    exp_conjuntos(tab.iloc[tr], ytr, modelos, out)
    print("3. leave-one-type-out (universo, 5 tipos)")
    exp_loto(X, y, grupos, modelos, out)
    # modelo para as figuras detalhadas: entre os dois modelos centrais da disciplina,
    # o de maior AUC na validação cruzada do treino (não olha validação ID nem OOD)
    candidatos = {n: out["cv"][n]["auc"]["media"] for n in ("Regressão logística", "Random Forest")}
    nome_final = max(candidatos, key=candidatos.get)
    out["modelo_final"] = nome_final
    print(f"   modelo das figuras detalhadas: {nome_final}")
    print("4. hiperparâmetros (split de treino; GridSearch RF com LOGO nos 4 tipos de treino)")
    exp_hiperparametros(Xtr, ytr, gtr, out)
    print("5. curva de aprendizado (split de treino)")
    exp_aprendizado(Xtr, ytr, modelos, out)
    print("6-8. holdout ID e OOD, limiar, calibração, importância, erros")
    lim = limiares_oof(Xtr, ytr, modelos)
    out["limiar_custo_oof"] = lim
    prev = []
    exp_holdout(tab, X, y, modelos, out, nome_final, tr, te_id, "id", lim, prev)
    exp_holdout(tab, X, y, modelos, out, nome_final, tr, te_ood, "ood", lim, prev)
    print("9. checagem de atalhos")
    exp_atalhos(tab, X, y, tr, te_id, te_ood, out)
    # previsões ficam fora do git (listam ids do dataset)
    from config import DATA
    pd.concat(prev).to_csv(DATA / "previsoes_classicos.csv", index=False)

    for split_ in ("id", "ood"):
        for nome in ("Regressão logística", "Random Forest", "Gradient Boosting"):
            r = out["holdout"][split_]["modelos"][nome]
            print(f"  {split_:3s} {nome:22s} AUC={r['auc']:.3f} FREUID={r['freuid']:.3f} "
                  f"APCER@1%={r['apcer_1pct_bpcer']:.3f} recall_custo={r['limiar_custo']['recall']:.3f}")
    (ANALISE / "modelagem.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, default=float),
                                            encoding="utf-8")
    print("OK ->", ANALISE / "modelagem.json")


if __name__ == "__main__":
    main()
