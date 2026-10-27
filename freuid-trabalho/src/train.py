"""Treina baselines clássicos (Regressão Logística + Random Forest) no subset FREUID."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DATA, RANDOM_SEED, REPORTS, SUBSET_DIR, SUBSET_MANIFEST  # noqa: E402
from features import extract_matrix  # noqa: E402
from metric import freuid_breakdown  # noqa: E402


def load_ready_manifest() -> pd.DataFrame:
    mf = pd.read_csv(SUBSET_MANIFEST)
    exists = mf["image_path"].map(lambda p: (SUBSET_DIR / Path(p).name).exists())
    ready = mf[exists].copy()
    print(f"Manifesto: {len(mf)} | com imagem local: {len(ready)}")
    if len(ready) < 100:
        raise RuntimeError("Poucas imagens baixadas. Rode src/download.py primeiro.")
    return ready.reset_index(drop=True)


def split_data(df: pd.DataFrame):
    """Split principal: deixa 1 type fora do treino (simula OOD)."""
    types = sorted(df["type"].unique())
    heldout = types[-1]  # determinístico
    train_df = df[df["type"] != heldout]
    test_ood = df[df["type"] == heldout]
    # dentro dos tipos vistos: holdout estratificado 20%
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_SEED)
    idx = np.arange(len(train_df))
    tr, te = next(gss.split(idx, train_df["label"], groups=train_df["type"]))
    # fallback se group split ficar estranho
    if len(te) < 50:
        tr_i, te_i = train_test_split(
            train_df.index,
            test_size=0.2,
            stratify=train_df["label"],
            random_state=RANDOM_SEED,
        )
        return train_df.loc[tr_i], train_df.loc[te_i], test_ood, heldout
    return train_df.iloc[tr], train_df.iloc[te], test_ood, heldout


def fit_models(X_train, y_train):
    models = {
        "logistic_regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        random_state=RANDOM_SEED,
                    ),
                ),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=20,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_SEED,
        ),
    }
    for name, model in models.items():
        print(f"Treinando {name}...")
        model.fit(X_train, y_train)
    return models


def evaluate(model, X, y, label: str) -> dict:
    if hasattr(model, "predict_proba"):
        score = model.predict_proba(X)[:, 1]
    else:
        score = model.decision_function(X)
    pred = (score >= 0.5).astype(int)
    out = freuid_breakdown(y, score)
    out["accuracy"] = float((pred == y).mean())
    out["n"] = int(len(y))
    out["split"] = label
    out["report"] = classification_report(
        y, pred, target_names=["legitimo", "fraude"], output_dict=True
    )
    return out, score, pred


def plot_roc(y, scores: dict[str, np.ndarray], title: str, path: Path) -> None:
    plt.figure(figsize=(6, 5))
    for name, s in scores.items():
        fpr, tpr, _ = roc_curve(y, s)
        auc = roc_auc_score(y, s)
        plt.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})")
    plt.plot([0, 1], [0, 1], "k--", lw=1)
    plt.xlabel("FPR (BPCER)")
    plt.ylabel("TPR (1 − APCER)")
    plt.title(title)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()


def plot_cm(y, pred, title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(4.5, 4))
    ConfusionMatrixDisplay.from_predictions(
        y, pred, display_labels=["legítimo", "fraude"], ax=ax, colorbar=False
    )
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_by_type(df: pd.DataFrame, scores: np.ndarray, path: Path) -> None:
    tmp = df.copy()
    tmp["score"] = scores
    rows = []
    for t, g in tmp.groupby("type"):
        if g["label"].nunique() < 2 or len(g) < 10:
            continue
        m = freuid_breakdown(g["label"].to_numpy(), g["score"].to_numpy())
        rows.append({"type": t, "n": len(g), **{k: m[k] for k in ("roc_auc", "freuid_score", "apcer_at_1pct_bpcer")}})
    tab = pd.DataFrame(rows).sort_values("freuid_score")
    tab.to_csv(path.with_suffix(".csv"), index=False)
    if tab.empty:
        return
    plt.figure(figsize=(7, 4))
    sns.barplot(data=tab, x="type", y="roc_auc", color="#2c6eaf")
    plt.xticks(rotation=20, ha="right")
    plt.ylim(0, 1)
    plt.title("ROC-AUC por tipo de documento (teste)")
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    df = load_ready_manifest()
    X = extract_matrix(df["image_path"].tolist())
    y = df["label"].to_numpy().astype(int)

    train_df, test_id, test_ood, heldout = split_data(df)
    print(f"Held-out type (OOD): {heldout}")
    print(f"train={len(train_df)} test_id={len(test_id)} test_ood={len(test_ood)}")

    X_train = X[train_df.index]
    y_train = y[train_df.index]
    models = fit_models(X_train, y_train)

    results = []
    for name, model in models.items():
        for split_name, part in (("id", test_id), ("ood", test_ood)):
            if len(part) == 0:
                continue
            metrics, score, pred = evaluate(model, X[part.index], y[part.index], split_name)
            metrics["model"] = name
            results.append(metrics)
            plot_cm(
                y[part.index],
                pred,
                f"{name} — {split_name}",
                REPORTS / f"cm_{name}_{split_name}.png",
            )
            if split_name == "id":
                plot_roc(
                    y[part.index],
                    {name: score},
                    f"ROC — {name} (tipos vistos)",
                    REPORTS / f"roc_{name}_id.png",
                )
                plot_by_type(part, score, REPORTS / f"auc_by_type_{name}.png")

    # ROC comparativa no teste ID
    scores = {}
    y_id = y[test_id.index]
    for name, model in models.items():
        s = model.predict_proba(X[test_id.index])[:, 1]
        scores[name] = s
    plot_roc(y_id, scores, "ROC comparativa (tipos vistos)", REPORTS / "roc_compare_id.png")

    # tabela resumo
    flat = []
    for r in results:
        flat.append(
            {
                "model": r["model"],
                "split": r["split"],
                "n": r["n"],
                "roc_auc": round(r["roc_auc"], 4),
                "audet": round(r["audet"], 4),
                "apcer@1%bpcer": round(r["apcer_at_1pct_bpcer"], 4),
                "freuid_score": round(r["freuid_score"], 4),
                "accuracy": round(r["accuracy"], 4),
                "f1_fraude": round(r["report"]["fraude"]["f1-score"], 4),
                "recall_fraude": round(r["report"]["fraude"]["recall"], 4),
            }
        )
    tab = pd.DataFrame(flat)
    tab.to_csv(REPORTS / "metrics.csv", index=False)

    summary = {
        "heldout_type": heldout,
        "n_total": int(len(df)),
        "n_train": int(len(train_df)),
        "n_test_id": int(len(test_id)),
        "n_test_ood": int(len(test_ood)),
        "metrics": flat,
        "note": (
            "Features clássicas (histograma + estatísticas). "
            "CNN/transfer learning no notebook Kaggle."
        ),
    }
    (REPORTS / "metrics.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    md = ["# Resultados — baselines FREUID", ""]
    md.append(f"- Subset local: **{len(df)}** imagens")
    md.append(f"- Tipo deixado de fora (OOD): `{heldout}`")
    md.append("")
    md.append(tab.to_markdown(index=False))
    md.append("")
    md.append("Gráficos: `roc_compare_id.png`, `cm_*.png`, `auc_by_type_*.png`.")
    (REPORTS / "results.md").write_text("\n".join(md), encoding="utf-8")
    print(tab.to_string(index=False))
    print(f"\nSalvo em {REPORTS}")


if __name__ == "__main__":
    main()
