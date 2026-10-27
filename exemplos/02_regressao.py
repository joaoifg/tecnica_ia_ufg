"""
Exemplo 2 — REGRESSÃO (versão visual)
IIG0029 — Técnicas de IA I

Pergunta: QUAL VALOR?
A saída é um número contínuo (preço da casa).

Rode o arquivo: abre janelas com gráficos.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# -------------------------------------------------
# Dados e modelo
# -------------------------------------------------
housing = fetch_california_housing()
X = housing.data
y = housing.target  # preço contínuo (em $100k)

# Um atributo forte para desenhar a reta: MedInc (renda mediana)
idx = 0
X1 = X[:, [idx]]
nome_x = housing.feature_names[idx]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

modelo = LinearRegression()
modelo.fit(X_train_s, y_train)
y_pred = modelo.predict(X_test_s)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

# Reta simples só com MedInc (para o painel 2 ficar intuitivo)
modelo_1d = LinearRegression()
modelo_1d.fit(X_train[:, [idx]], y_train)
x_linha = np.linspace(X[:, idx].min(), X[:, idx].max(), 200).reshape(-1, 1)
y_linha = modelo_1d.predict(x_linha)

print("=== REGRESSÃO ===")
print("Pergunta: qual o preço médio da casa?")
print(f"MAE={mae:.3f}  RMSE={rmse:.3f}  R²={r2:.3f}")
print("Gráficos abertos / salvos em exemplos/figuras/")

# -------------------------------------------------
# Figura com 3 painéis
# -------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
fig.suptitle(
    "REGRESSÃO — a saída é um NÚMERO CONTÍNUO",
    fontsize=14,
    fontweight="bold",
)

# 1) Distribuição do alvo contínuo
ax = axes[0]
ax.hist(y, bins=40, color="#16a085", edgecolor="white", alpha=0.9)
ax.set_xlabel("Preço médio da casa (× $100k)")
ax.set_ylabel("Quantidade de casas")
ax.set_title("1) y é contínuo (muitos valores possíveis)")
ax.grid(True, axis="y", alpha=0.25)

# 2) Nuvem + reta de regressão (1 atributo)
ax = axes[1]
amostra = np.random.RandomState(42).choice(len(X), size=1500, replace=False)
ax.scatter(
    X[amostra, idx],
    y[amostra],
    c="#34495e",
    alpha=0.25,
    s=18,
    label="casas reais",
)
ax.plot(x_linha, y_linha, color="#e67e22", linewidth=2.5, label="reta do modelo")
ax.set_xlabel(nome_x + " (renda mediana)")
ax.set_ylabel("Preço (× $100k)")
ax.set_title("2) Modelo aproxima uma curva/reta de valores")
ax.legend()
ax.grid(True, alpha=0.25)

# 3) Real × previsto (quanto mais perto da diagonal, melhor)
ax = axes[2]
ax.scatter(y_test, y_pred, c="#8e44ad", alpha=0.35, s=18, edgecolors="none")
lim_min = min(y_test.min(), y_pred.min())
lim_max = max(y_test.max(), y_pred.max())
ax.plot([lim_min, lim_max], [lim_min, lim_max], "k--", linewidth=1.5, label="acerto perfeito")
ax.set_xlabel("Preço real")
ax.set_ylabel("Preço previsto")
ax.set_title(f"3) Real × previsto  |  R²={r2:.2f}  MAE={mae:.2f}")
ax.legend()
ax.grid(True, alpha=0.25)
ax.set_aspect("equal", adjustable="box")

plt.tight_layout()

saida = Path(__file__).resolve().parent / "figuras"
saida.mkdir(exist_ok=True)
caminho = saida / "02_regressao.png"
fig.savefig(caminho, dpi=140, bbox_inches="tight")
print(f"Figura salva em: {caminho}")

plt.show()

print("---")
print("REGRESSÃO = prever VALOR NUMÉRICO.")
print("Não há 'classe vermelha/azul' — há uma escala de preços e uma reta.")
