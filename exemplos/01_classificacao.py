"""
Exemplo 1 — CLASSIFICAÇÃO (versão visual)
IIG0029 — Técnicas de IA I

Pergunta: QUAL CLASSE?
A saída é uma categoria (rótulo discreto): maligno ou benigno.

Rode o arquivo: abre janelas com gráficos.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

# -------------------------------------------------
# Dados e modelo
# -------------------------------------------------
cancer = load_breast_cancer()
X = cancer.data
y = cancer.target  # 0 = malignant, 1 = benign
nomes = ["Maligno", "Benigno"]

# Dois atributos só para desenhar no plano 2D
idx_a, idx_b = 0, 1  # mean radius, mean texture
X2 = X[:, [idx_a, idx_b]]
nome_a = cancer.feature_names[idx_a]
nome_b = cancer.feature_names[idx_b]

X_train, X_test, y_train, y_test = train_test_split(
    X2, y, test_size=0.3, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

modelo = KNeighborsClassifier(n_neighbors=7)
modelo.fit(X_train_s, y_train)
y_pred = modelo.predict(X_test_s)
acc = accuracy_score(y_test, y_pred)

print("=== CLASSIFICAÇÃO ===")
print("Pergunta: o tumor é Maligno ou Benigno?")
print(f"Acurácia no teste: {acc:.3f}")
print("Gráficos abertos / salvos em exemplos/figuras/")

# -------------------------------------------------
# Figura com 3 painéis
# -------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
fig.suptitle(
    "CLASSIFICAÇÃO — a saída é uma CLASSE (categoria)",
    fontsize=14,
    fontweight="bold",
)

cores = {0: "#c0392b", 1: "#2980b9"}  # maligno / benigno

# 1) Nuvem de pontos colorida por classe
ax = axes[0]
for classe, nome in enumerate(nomes):
    mascara = y == classe
    ax.scatter(
        X[mascara, idx_a],
        X[mascara, idx_b],
        c=cores[classe],
        label=nome,
        alpha=0.65,
        edgecolors="white",
        linewidths=0.4,
        s=35,
    )
ax.set_xlabel(nome_a)
ax.set_ylabel(nome_b)
ax.set_title("1) Dados: cada ponto tem uma classe")
ax.legend(title="Classe real")
ax.grid(True, alpha=0.25)

# 2) Fronteira de decisão do k-NN (espaço padronizado → original)
ax = axes[1]
h = 0.05
x_min, x_max = X_train_s[:, 0].min() - 0.5, X_train_s[:, 0].max() + 0.5
y_min, y_max = X_train_s[:, 1].min() - 0.5, X_train_s[:, 1].max() + 0.5
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
Z = modelo.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

# Desenhar no espaço original (inverso do scaler)
grid_orig = scaler.inverse_transform(np.c_[xx.ravel(), yy.ravel()])
xx_o = grid_orig[:, 0].reshape(xx.shape)
yy_o = grid_orig[:, 1].reshape(yy.shape)

ax.contourf(xx_o, yy_o, Z, alpha=0.25, levels=[-0.5, 0.5, 1.5], colors=["#c0392b", "#2980b9"])
for classe, nome in enumerate(nomes):
    mascara = y_test == classe
    ax.scatter(
        X_test[mascara, 0],
        X_test[mascara, 1],
        c=cores[classe],
        label=nome,
        edgecolors="black",
        linewidths=0.5,
        s=45,
    )
ax.set_xlabel(nome_a)
ax.set_ylabel(nome_b)
ax.set_title("2) Modelo: divide o espaço em regiões")
ax.legend(title="Teste (real)")
ax.grid(True, alpha=0.25)

# 3) Matriz de confusão
ax = axes[2]
ConfusionMatrixDisplay.from_predictions(
    y_test,
    y_pred,
    display_labels=nomes,
    cmap="Blues",
    colorbar=False,
    ax=ax,
)
ax.set_title(f"3) Matriz de confusão  |  acurácia={acc:.2f}")

plt.tight_layout()

saida = Path(__file__).resolve().parent / "figuras"
saida.mkdir(exist_ok=True)
caminho = saida / "01_classificacao.png"
fig.savefig(caminho, dpi=140, bbox_inches="tight")
print(f"Figura salva em: {caminho}")

plt.show()

print("---")
print("CLASSIFICAÇÃO = prever CATEGORIA.")
print("No gráfico, as cores são classes — não uma reta de valores.")
