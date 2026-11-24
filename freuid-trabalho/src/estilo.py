"""Estilo único dos gráficos (mesmas cores dos slides)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from config import FIGS  # noqa: E402

COR = {
    "navy": "#0B2545",
    "ink": "#1B2433",
    "muted": "#5E6878",
    "soft": "#8A93A3",
    "line": "#E4DED1",
    "grid": "#EEE9DF",
    "fraude": "#C0473B",
    "legitimo": "#2E8B57",
    "gold": "#C9A227",
    "azul": "#2C6EAF",
    "laranja": "#D0832B",
    "roxo": "#7B5EA7",
    "verde2": "#4FA3A5",
    "cinza": "#9AA3B2",
}

# uma cor fixa por modelo, usada em todos os gráficos
COR_MODELO = {
    "Baseline": "#9AA3B2",
    "Regressão logística": "#2C6EAF",
    "KNN": "#4FA3A5",
    "Naive Bayes": "#7B5EA7",
    "Árvore de decisão": "#C9A227",
    "Random Forest": "#D0832B",
    "Gradient Boosting": "#C0473B",
}

COR_FAMILIA = {
    "Histograma R": "#C0473B",
    "Histograma G": "#2E8B57",
    "Histograma B": "#2C6EAF",
    "Estatísticas de cor": "#C9A227",
    "Brilho e bordas": "#0B2545",
    "Perícia (ELA, nitidez, frequência)": "#7B5EA7",
}


def aplicar() -> None:
    mpl.rcParams.update(
        {
            "font.family": ["Segoe UI", "DejaVu Sans"],
            "font.size": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": COR["line"],
            "axes.labelcolor": COR["muted"],
            "axes.titlecolor": COR["ink"],
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "axes.titlelocation": "left",
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": COR["grid"],
            "grid.linewidth": 0.8,
            "xtick.color": COR["muted"],
            "ytick.color": COR["muted"],
            "legend.frameon": False,
            "figure.dpi": 100,
            "savefig.dpi": 200,
        }
    )


def salvar(fig, nome: str) -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGS / f"{nome}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
