"""
Matriz de confusão — explicação visual
IIG0029 — Técnicas de IA I

Ideia: comparar CLASSE REAL × CLASSE PREVISTA.
Cada célula conta quantos casos caíram nessa combinação.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

# -------------------------------------------------
# Exemplo numérico FIXO (fácil de contar na mão)
# Imagine 20 pacientes:
#   10 realmente doentes (positivo)
#   10 realmente saudáveis (negativo)
#
# O modelo previu:
#   dos 10 doentes:     8 certos (VP), 2 errou e disse saudável (FN)
#   dos 10 saudáveis:   7 certos (VN), 3 errou e disse doente (FP)
# -------------------------------------------------
VP, FN = 8, 2
FP, VN = 3, 7

matriz = np.array([[VP, FN], [FP, VN]])
total = VP + FN + FP + VN

precisao = VP / (VP + FP)
recall = VP / (VP + FN)
acuracia = (VP + VN) / total

# -------------------------------------------------
# Figura didática
# -------------------------------------------------
fig = plt.figure(figsize=(12, 6.5))
fig.suptitle(
    "Matriz de confusão = tabela REAL × PREVISTO",
    fontsize=15,
    fontweight="bold",
)

# Painel 1: a matriz com rótulos grandes
ax1 = fig.add_subplot(1, 2, 1)
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.axis("off")
ax1.set_title("Como ler a tabela", fontsize=12, pad=10)

# Cabeçalhos
ax1.text(6.5, 9.2, "PREVISTO", ha="center", fontsize=11, fontweight="bold")
ax1.text(4.0, 8.3, "Positivo\n(doente)", ha="center", fontsize=9)
ax1.text(7.5, 8.3, "Negativo\n(saudável)", ha="center", fontsize=9)
ax1.text(0.8, 5.0, "REAL", ha="center", va="center", fontsize=11, fontweight="bold", rotation=90)
ax1.text(1.9, 6.2, "Positivo\n(doente)", ha="center", fontsize=9)
ax1.text(1.9, 3.2, "Negativo\n(saudável)", ha="center", fontsize=9)

# Células
celulas = [
    # (x, y, valor, titulo, cor, explicacao)
    (3.2, 5.0, VP, "VP", "#27ae60", "Era doente\ne acertou"),
    (6.7, 5.0, FN, "FN", "#e74c3c", "Era doente\nmas errou"),
    (3.2, 2.0, FP, "FP", "#e67e22", "Era saudável\nmas errou"),
    (6.7, 2.0, VN, "VN", "#27ae60", "Era saudável\ne acertou"),
]

for x, y, valor, titulo, cor, texto in celulas:
    box = FancyBboxPatch(
        (x, y), 2.8, 2.4,
        boxstyle="round,pad=0.05,rounding_size=0.2",
        linewidth=1.5,
        edgecolor="#2c3e50",
        facecolor=cor,
        alpha=0.35,
    )
    ax1.add_patch(box)
    ax1.text(x + 1.4, y + 1.7, f"{titulo} = {valor}", ha="center", fontsize=13, fontweight="bold")
    ax1.text(x + 1.4, y + 0.7, texto, ha="center", fontsize=9, color="#2c3e50")

ax1.text(
    5.0, 0.4,
    "Diagonal verde = ACERTOS   |   Fora da diagonal = ERROS",
    ha="center", fontsize=10, fontweight="bold",
)

# Painel 2: métricas derivadas
ax2 = fig.add_subplot(1, 2, 2)
ax2.axis("off")
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.set_title("O que cada métrica pergunta", fontsize=12, pad=10)

blocos = [
    (9.0, "Acurácia", f"(VP+VN)/total = ({VP}+{VN})/{total} = {acuracia:.2f}",
     "De TUDO, quanto acertei?"),
    (6.6, "Precisão", f"VP/(VP+FP) = {VP}/({VP}+{FP}) = {precisao:.2f}",
     "Dos que chamei de DOENTE,\nquantos realmente eram?"),
    (4.0, "Recall", f"VP/(VP+FN) = {VP}/({VP}+{FN}) = {recall:.2f}",
     "Dos DOENTES de verdade,\nquantos eu encontrei?"),
]

for y, nome, formula, pergunta in blocos:
    box = FancyBboxPatch(
        (0.5, y - 1.5), 9.0, 2.2,
        boxstyle="round,pad=0.05,rounding_size=0.2",
        linewidth=1.2,
        edgecolor="#34495e",
        facecolor="#ecf0f1",
    )
    ax2.add_patch(box)
    ax2.text(1.0, y + 0.2, nome, fontsize=12, fontweight="bold", va="center")
    ax2.text(1.0, y - 0.55, formula, fontsize=10, va="center", family="monospace")
    ax2.text(9.0, y - 0.2, pergunta, fontsize=9, ha="right", va="center", color="#2c3e50")

# Heatmap pequeno numérico estilo sklearn
ax_in = fig.add_axes([0.58, 0.08, 0.28, 0.22])
im = ax_in.imshow(matriz, cmap="Blues")
ax_in.set_xticks([0, 1], ["Prev. Positivo", "Prev. Negativo"])
ax_in.set_yticks([0, 1], ["Real Positivo", "Real Negativo"])
for i in range(2):
    for j in range(2):
        ax_in.text(j, i, str(matriz[i, j]), ha="center", va="center",
                   fontsize=14, fontweight="bold",
                   color="white" if matriz[i, j] > 5 else "black")
ax_in.set_title("Mesma matriz (formato da prova)", fontsize=9)

plt.tight_layout(rect=[0, 0.28, 1, 0.95])

saida = Path(__file__).resolve().parent / "figuras"
saida.mkdir(exist_ok=True)
caminho = saida / "04_matriz_confusao.png"
fig.savefig(caminho, dpi=140, bbox_inches="tight")
print(f"Figura salva em: {caminho}")
print()
print("Resumo:")
print(f"  VP={VP}  FN={FN}  FP={FP}  VN={VN}")
print(f"  Acurácia={acuracia:.2f}  Precisão={precisao:.2f}  Recall={recall:.2f}")
print()
print("Macete: diagonal = acertos | fora = erros")
print("Precisão olha os positivos PREVISTOS.")
print("Recall olha os positivos REAIS.")

# Também abre no visualizador padrão no Windows
try:
    import os
    os.startfile(caminho)
except Exception:
    pass

plt.show()
