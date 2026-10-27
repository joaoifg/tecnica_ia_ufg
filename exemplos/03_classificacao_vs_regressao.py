"""
Exemplo 3 — LADO A LADO: classificação × regressão
IIG0029 — Técnicas de IA I

Um único gráfico para fixar a diferença na prova.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import fetch_california_housing, load_breast_cancer
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

# ---------- Classificação (2 atributos) ----------
cancer = load_breast_cancer()
Xc = cancer.data[:, [0, 1]]
yc = cancer.target
scaler_c = StandardScaler()
Xc_s = scaler_c.fit_transform(Xc)
knn = KNeighborsClassifier(n_neighbors=7).fit(Xc_s, yc)

h = 0.08
xmin, xmax = Xc_s[:, 0].min() - 0.4, Xc_s[:, 0].max() + 0.4
ymin, ymax = Xc_s[:, 1].min() - 0.4, Xc_s[:, 1].max() + 0.4
xx, yy = np.meshgrid(np.arange(xmin, xmax, h), np.arange(ymin, ymax, h))
Z = knn.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
grid_o = scaler_c.inverse_transform(np.c_[xx.ravel(), yy.ravel()])
xx_o, yy_o = grid_o[:, 0].reshape(xx.shape), grid_o[:, 1].reshape(yy.shape)

# ---------- Regressão (1 atributo) ----------
housing = fetch_california_housing()
xr = housing.data[:, [0]]
yr = housing.target
reg = LinearRegression().fit(xr, yr)
x_linha = np.linspace(xr.min(), xr.max(), 200).reshape(-1, 1)
y_linha = reg.predict(x_linha)

# ---------- Figura ----------
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle(
    "Diferença visual: CLASSIFICAÇÃO  ×  REGRESSÃO",
    fontsize=14,
    fontweight="bold",
)

# Esquerda: classificação
ax = axes[0]
ax.contourf(xx_o, yy_o, Z, alpha=0.22, levels=[-0.5, 0.5, 1.5], colors=["#c0392b", "#2980b9"])
ax.scatter(
    Xc[yc == 0, 0], Xc[yc == 0, 1],
    c="#c0392b", s=28, alpha=0.7, edgecolors="white", linewidths=0.3, label="Maligno",
)
ax.scatter(
    Xc[yc == 1, 0], Xc[yc == 1, 1],
    c="#2980b9", s=28, alpha=0.7, edgecolors="white", linewidths=0.3, label="Benigno",
)
ax.set_title("CLASSIFICAÇÃO\nPergunta: QUAL CLASSE?")
ax.set_xlabel("mean radius")
ax.set_ylabel("mean texture")
ax.legend(title="Categorias")
ax.text(
    0.02, 0.98,
    "Saída: rótulo discreto\n(Maligno / Benigno)\nMétricas: acurácia, precisão, recall",
    transform=ax.transAxes, va="top", ha="left", fontsize=9,
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.85),
)
ax.grid(True, alpha=0.2)

# Direita: regressão
ax = axes[1]
amostra = np.random.RandomState(0).choice(len(xr), 1200, replace=False)
ax.scatter(xr[amostra], yr[amostra], c="#7f8c8d", s=12, alpha=0.3, label="casas")
ax.plot(x_linha, y_linha, color="#e67e22", linewidth=2.8, label="preço previsto")
ax.set_title("REGRESSÃO\nPergunta: QUAL VALOR?")
ax.set_xlabel("renda mediana (MedInc)")
ax.set_ylabel("preço da casa (× $100k)")
ax.legend()
ax.text(
    0.02, 0.98,
    "Saída: número contínuo\n(ex.: 1.52, 3.87, 4.10…)\nMétricas: MAE, MSE, RMSE, R²",
    transform=ax.transAxes, va="top", ha="left", fontsize=9,
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.85),
)
ax.grid(True, alpha=0.2)

plt.tight_layout()

saida = Path(__file__).resolve().parent / "figuras"
saida.mkdir(exist_ok=True)
caminho = saida / "03_classificacao_vs_regressao.png"
fig.savefig(caminho, dpi=140, bbox_inches="tight")
print(f"Figura salva em: {caminho}")
plt.show()

print("Macete: classificação = cores/classes | regressão = reta/números.")
