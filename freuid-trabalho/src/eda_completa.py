"""Análise exploratória completa do FREUID.

Parte A: os 69.352 rótulos (train_labels.csv).
Parte B: as imagens do subset (metadados e as 73 features).

Saídas: reports/figs/eda_*.png e reports/analise/eda.json
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from config import ANALISE, DATA, NOMES_PAIS
from protocolo import universo
from estilo import COR, COR_FAMILIA, aplicar, salvar
from features import FEATURES, METADADOS, build_feature_table, familia

import matplotlib.pyplot as plt  # noqa: E402  (estilo já fixou o backend)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confiança de 95% (Wilson) para uma proporção k/n."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z**2 / n
    centro = (p + z**2 / (2 * n)) / den
    meia = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
    return (centro - meia, centro + meia)


def cohen_d(a: np.ndarray, b: np.ndarray) -> float:
    """Tamanho de efeito: diferença de médias em desvios-padrão."""
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    return float((a.mean() - b.mean()) / sp) if sp > 0 else 0.0


# ============================================================ PARTE A
def eda_rotulos(df: pd.DataFrame, out: dict) -> None:
    out["n_total"] = int(len(df))
    out["colunas"] = list(df.columns)
    out["nulos"] = int(df.isna().sum().sum())
    out["ids_duplicados"] = int(df["id"].duplicated().sum())
    vc = df["label"].value_counts().sort_index()
    out["n_legitimo"], out["n_fraude"] = int(vc[0]), int(vc[1])
    out["pct_fraude"] = float(vc[1] / len(df))

    # --- classes
    fig, ax = plt.subplots(figsize=(7, 2.6))
    ax.barh(["Fraude (1)", "Legítimo (0)"], [vc[1], vc[0]], color=[COR["fraude"], COR["legitimo"]], height=0.6)
    for i, v in enumerate([vc[1], vc[0]]):
        ax.text(v + 400, i, f"{v:,}".replace(",", ".") + f"  ({v / len(df):.1%})".replace(".", ","),
                va="center", fontsize=11, color=COR["ink"], fontweight="bold")
    ax.set_xlim(0, vc.max() * 1.35)
    ax.set_xlabel("número de imagens rotuladas (train_labels.csv)")
    ax.set_title(f"Distribuição da variável alvo (label) · {len(df):,} rótulos".replace(",", "."))
    ax.grid(axis="y", visible=False)
    salvar(fig, "eda_classes")

    # --- tipo × label, taxa de fraude com IC 95%
    ct = pd.crosstab(df["type"], df["label"])
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    v_cramer = float(np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1))))
    taxa = []
    for t, row in ct.iterrows():
        n = int(row.sum())
        k = int(row[1])
        lo, hi = wilson(k, n)
        taxa.append({"type": t, "pais": NOMES_PAIS[t], "n": n, "legitimo": int(row[0]), "fraude": k,
                     "taxa": k / n, "ic_lo": lo, "ic_hi": hi})
    taxa = sorted(taxa, key=lambda r: r["taxa"])
    out["por_tipo"] = taxa
    out["qui2"] = {"chi2": float(chi2), "p": float(p), "gl": int(dof), "v_cramer": v_cramer}

    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8), gridspec_kw={"width_ratios": [1.5, 1]})
    nomes = [r["pais"] for r in taxa]
    leg = [r["legitimo"] for r in taxa]
    fra = [r["fraude"] for r in taxa]
    axes[0].barh(nomes, leg, color=COR["legitimo"], label="Legítimo")
    axes[0].barh(nomes, fra, left=leg, color=COR["fraude"], label="Fraude")
    for i, (a, b) in enumerate(zip(leg, fra)):
        axes[0].text(a / 2, i, f"{a:,}".replace(",", "."), va="center", ha="center", color="white", fontsize=10, fontweight="bold")
        axes[0].text(a + b / 2, i, f"{b:,}".replace(",", "."), va="center", ha="center", color="white", fontsize=10, fontweight="bold")
    axes[0].set_title("Imagens por documento e classe")
    axes[0].legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)
    axes[0].set_xlabel("número de imagens")
    axes[0].grid(axis="y", visible=False)
    t = np.array([r["taxa"] for r in taxa])
    err = np.array([[r["taxa"] - r["ic_lo"] for r in taxa], [r["ic_hi"] - r["taxa"] for r in taxa]])
    cores = [COR["fraude"] if r["pais"] == "Egito" else COR["soft"] for r in taxa]
    axes[1].barh(nomes, t, xerr=err, color=cores, capsize=4, error_kw={"ecolor": COR["ink"], "lw": 1})
    axes[1].axvline(out["pct_fraude"], color=COR["ink"], ls="--", lw=1)
    axes[1].text(out["pct_fraude"] + 0.004, -0.6, "média geral", fontsize=9, color=COR["muted"])
    for i, v in enumerate(t):
        axes[1].text(v + 0.012, i, f"{v:.1%}".replace(".", ","), va="center", fontsize=10, color=COR["ink"])
    axes[1].set_xlim(0.3, 0.56)
    axes[1].set_title("Taxa de fraude (IC 95%)")
    axes[1].set_xlabel("proporção de fraudes")
    axes[1].set_yticklabels([])
    axes[1].grid(axis="y", visible=False)
    fig.tight_layout()
    salvar(fig, "eda_tipo_label")

    # --- is_digital
    ctd = pd.crosstab(df["is_digital"], df["label"])
    odds, p_fisher = stats.fisher_exact(ctd.values)
    dig = []
    for flag, row in ctd.iterrows():
        n, k = int(row.sum()), int(row[1])
        lo, hi = wilson(k, n)
        dig.append({"is_digital": bool(flag), "n": n, "fraude": k, "taxa": k / n, "ic_lo": lo, "ic_hi": hi})
    out["is_digital"] = dig
    out["fisher"] = {"odds_ratio": float(odds), "p": float(p_fisher)}

    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    labels = [f"Recapturada\n(n = {dig[0]['n']})", f"Digital\n(n = {dig[1]['n']:,})".replace(",", ".")]
    vals = [dig[0]["taxa"], dig[1]["taxa"]]
    err = [[dig[0]["taxa"] - dig[0]["ic_lo"], dig[1]["taxa"] - dig[1]["ic_lo"]],
           [dig[0]["ic_hi"] - dig[0]["taxa"], dig[1]["ic_hi"] - dig[1]["taxa"]]]
    ax.bar(labels, vals, yerr=err, color=[COR["laranja"], COR["azul"]], capsize=8, width=0.5,
           error_kw={"ecolor": COR["ink"], "lw": 1.2})
    for i, v in enumerate(vals):
        ax.text(i + 0.28, v, f"{v:.1%}".replace(".", ","), va="center", fontsize=12, fontweight="bold", color=COR["ink"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("taxa de fraude")
    ax.set_title("Fraude por forma de captura (IC 95%)")
    salvar(fig, "eda_is_digital")


# ============================================================ PARTE B
def eda_subset(pop: pd.DataFrame, sub: pd.DataFrame, out: dict) -> None:
    """Confere se a amostra representa a população."""
    comp = []
    for t in sorted(pop["type"].unique()):
        p_pop = (pop["type"] == t).mean()
        p_sub = (sub["type"] == t).mean()
        f_pop = pop.loc[pop["type"] == t, "label"].mean()
        f_sub = sub.loc[sub["type"] == t, "label"].mean()
        comp.append({"pais": NOMES_PAIS[t], "pct_pop": p_pop, "pct_amostra": p_sub,
                     "fraude_pop": f_pop, "fraude_amostra": f_sub})
    out["amostra"] = {
        "n": int(len(sub)),
        "fracao_do_total": float(len(sub) / len(pop)),
        "pct_fraude": float(sub["label"].mean()),
        "recapturadas": int((~sub["is_digital"].astype(bool)).sum()),
        "comparacao": comp,
    }


def eda_metadados(tab: pd.DataFrame, out: dict) -> None:
    res = {}
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))
    for ax, col, titulo in zip(axes, METADADOS, ["Largura (px)", "Altura (px)", "Tamanho do arquivo (KB)"]):
        a = tab.loc[tab.label == 0, col].to_numpy()
        b = tab.loc[tab.label == 1, col].to_numpy()
        u, p = stats.mannwhitneyu(a, b)
        auc = roc_auc_score(tab["label"], tab[col])
        res[col] = {"mediana_legitimo": float(np.median(a)), "mediana_fraude": float(np.median(b)),
                    "p_mannwhitney": float(p), "auc_univariada": float(auc)}
        bp = ax.boxplot([a, b], tick_labels=["Legítimo", "Fraude"], patch_artist=True, widths=0.55,
                        medianprops={"color": "white", "lw": 2}, flierprops={"ms": 2, "alpha": 0.3})
        for patch, c in zip(bp["boxes"], [COR["legitimo"], COR["fraude"]]):
            patch.set_facecolor(c)
            patch.set_edgecolor(c)
        ax.set_title(titulo)
        ax.set_ylabel(titulo.split(" (")[0].lower())
        ax.text(0.98, 0.97, f"AUC = {auc:.2f}".replace(".", ","), transform=ax.transAxes, ha="right", va="top",
                fontsize=10, color=COR["muted"])
    fig.suptitle(f"Metadados do arquivo por classe (n = {len(tab)} imagens locais)", x=0.01, ha="left", fontweight="bold")
    fig.tight_layout()
    salvar(fig, "eda_metadados")
    out["metadados"] = res


def eda_features(tab: pd.DataFrame, out: dict) -> None:
    y = tab["label"].to_numpy()
    linhas = []
    for f in FEATURES:
        x = tab[f].to_numpy()
        a, b = x[y == 0], x[y == 1]
        _, p = stats.mannwhitneyu(a, b)
        auc = roc_auc_score(y, x)
        linhas.append({"feature": f, "familia": familia(f), "auc": float(auc), "poder": float(abs(auc - 0.5)),
                       "cohen_d": cohen_d(b, a), "p": float(p)})
    rank = pd.DataFrame(linhas).sort_values("poder", ascending=False).reset_index(drop=True)
    rank.to_csv(ANALISE / "ranking_features.csv", index=False)
    alpha = 0.05 / len(FEATURES)  # correção de Bonferroni
    out["features"] = {
        "n": len(FEATURES),
        "significativas_bonferroni": int((rank["p"] < alpha).sum()),
        "top": rank.head(15).to_dict("records"),
    }

    # --- ranking univariado
    top = rank.head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 5.4))
    ax.barh(top["feature"], top["auc"].where(top["auc"] >= 0.5, 1 - top["auc"]),
            color=[COR_FAMILIA[f] for f in top["familia"]])
    ax.axvline(0.5, color=COR["ink"], lw=1, ls="--")
    ax.set_xlim(0.45, max(0.9, top["auc"].max() + 0.05))
    ax.set_xlabel("AUC usando só esta feature (0,5 = chute)")
    ax.set_title(f"As 15 features que mais separam fraude de legítimo (n = {len(tab)})")
    ax.grid(axis="y", visible=False)
    hand = [plt.Rectangle((0, 0), 1, 1, color=c) for c in COR_FAMILIA.values()]
    ax.legend(hand, COR_FAMILIA.keys(), loc="lower right", fontsize=8.5)
    salvar(fig, "eda_ranking_features")

    # --- distribuições das 6 melhores
    fig, axes = plt.subplots(2, 3, figsize=(12, 6))
    for ax, f in zip(axes.ravel(), rank["feature"].head(6)):
        a = tab.loc[tab.label == 0, f]
        b = tab.loc[tab.label == 1, f]
        lo, hi = np.percentile(tab[f], [1, 99])
        bins = np.linspace(lo, hi, 35)
        ax.hist(a.clip(lo, hi), bins=bins, color=COR["legitimo"], alpha=0.55, density=True, label="Legítimo")
        ax.hist(b.clip(lo, hi), bins=bins, color=COR["fraude"], alpha=0.55, density=True, label="Fraude")
        d = rank.set_index("feature").loc[f, "cohen_d"]
        ax.set_title(f, fontsize=11.5)
        ax.set_xlabel("valor da feature")
        ax.set_ylabel("densidade")
        ax.text(0.98, 0.95, f"d = {d:+.2f}".replace(".", ","), transform=ax.transAxes, ha="right", va="top",
                fontsize=10, color=COR["muted"])
        ax.set_yticks([])
    axes[0, 0].legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    salvar(fig, "eda_distribuicoes")

    # --- histograma médio de cor por classe
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.3), sharey=True)
    centros = np.arange(16) * 16 + 8
    for ax, c, nome in zip(axes, "RGB", ["Vermelho", "Verde", "Azul"]):
        cols = [f"hist_{c}_{i:02d}" for i in range(16)]
        ax.plot(centros, tab.loc[tab.label == 0, cols].mean() * 1000, color=COR["legitimo"], lw=2.5, label="Legítimo")
        ax.plot(centros, tab.loc[tab.label == 1, cols].mean() * 1000, color=COR["fraude"], lw=2.5, ls="--", label="Fraude")
        ax.set_title(f"Canal {nome}")
        ax.set_xlabel("tom do pixel (0–255)")
    axes[0].set_ylabel("densidade (×1000)")
    axes[0].legend()
    fig.tight_layout()
    salvar(fig, "eda_histograma_medio")

    # --- correlação
    corr = tab[FEATURES].corr().to_numpy()
    iu = np.triu_indices_from(corr, k=1)
    out["features"]["pares_corr_maior_0_9"] = int((np.abs(corr[iu]) > 0.9).sum())
    out["features"]["total_pares"] = int(len(iu[0]))
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    limites = [0, 16, 32, 48, 60, 64, 73]
    nomes = ["Hist R", "Hist G", "Hist B", "Estat.", "Brilho", "Perícia"]
    for l in limites[1:-1]:
        ax.axhline(l - 0.5, color="white", lw=1.5)
        ax.axvline(l - 0.5, color="white", lw=1.5)
    meio = [(a + b) / 2 - 0.5 for a, b in zip(limites[:-1], limites[1:])]
    ax.set_xticks(meio, nomes, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(meio, nomes, fontsize=9)
    ax.grid(False)
    fig.colorbar(im, ax=ax, shrink=0.8, label="correlação de Pearson")
    ax.set_title(f"Correlação entre as 73 features (n = {len(tab)})")
    ax.set_xlabel("família de features")
    ax.set_ylabel("família de features")
    salvar(fig, "eda_correlacao")

    # --- PCA
    Z = StandardScaler().fit_transform(tab[FEATURES])
    pca = PCA(random_state=0).fit(Z)
    acum = np.cumsum(pca.explained_variance_ratio_)
    out["pca"] = {"var_pc1": float(pca.explained_variance_ratio_[0]), "var_pc2": float(pca.explained_variance_ratio_[1]),
                  "comp_90": int(np.searchsorted(acum, 0.90) + 1), "comp_95": int(np.searchsorted(acum, 0.95) + 1)}
    P = pca.transform(Z)[:, :2]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for lab, c, nome in [(0, COR["legitimo"], "Legítimo"), (1, COR["fraude"], "Fraude")]:
        m = tab.label == lab
        axes[0].scatter(P[m, 0], P[m, 1], s=7, alpha=0.45, color=c, label=nome)
    axes[0].set_title(f"PCA colorido pela classe (n = {len(tab)} imagens)")
    axes[0].legend(markerscale=3)
    paleta = [COR["azul"], COR["laranja"], COR["roxo"], COR["verde2"], COR["gold"]]
    for (t, nome), c in zip(NOMES_PAIS.items(), paleta):
        m = tab["type"] == t
        axes[1].scatter(P[m, 0], P[m, 1], s=7, alpha=0.45, color=c, label=nome)
    axes[1].set_title(f"PCA colorido pelo documento (n = {len(tab)})")
    axes[1].legend(markerscale=3)
    for ax in axes:
        ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.0%} da variância)")
        ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.0%})")
    fig.tight_layout()
    salvar(fig, "eda_pca")

    # separabilidade no plano do PCA: silhueta por classe vs por documento
    from sklearn.metrics import silhouette_score
    amostra = np.random.default_rng(0).choice(len(P), size=min(1500, len(P)), replace=False)
    out["pca"]["silhueta_classe"] = float(silhouette_score(Z[amostra], tab["label"].to_numpy()[amostra]))
    out["pca"]["silhueta_documento"] = float(silhouette_score(Z[amostra], tab["type"].to_numpy()[amostra]))


def main() -> None:
    aplicar()
    ANALISE.mkdir(parents=True, exist_ok=True)
    out: dict = {}
    pop = pd.read_csv(DATA / "train_labels.csv")
    eda_rotulos(pop, out)

    # Parte B usa só as imagens que existem no disco (mesmo universo da modelagem e da CNN)
    sub = universo()
    out["parte_b_n_imagens"] = int(len(sub))
    eda_subset(pop, sub, out)
    tab = build_feature_table(sub)
    eda_metadados(tab, out)
    eda_features(tab, out)

    (ANALISE / "eda.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("n_total", "pct_fraude", "qui2", "fisher", "pca")}, indent=2))


if __name__ == "__main__":
    main()
