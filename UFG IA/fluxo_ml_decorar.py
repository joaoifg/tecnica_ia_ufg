"""
Fluxo de ML no Scikit-Learn — DECORAR

1. Divisão treino/teste
2. Pré-processamento (fit_transform no treino, transform no teste)
3. Treinamento (fit)
4. Inferência e avaliação (predict + métrica)
"""

# ---------------------------------------------------------------------------
# IMPORTS — cada um traz uma peça do fluxo
# ---------------------------------------------------------------------------
from sklearn.datasets import load_iris              # dataset clássico (flores)
from sklearn.model_selection import train_test_split  # divide treino / teste
from sklearn.preprocessing import StandardScaler    # Transformer: padroniza X
from sklearn.neighbors import KNeighborsClassifier  # Predictor: classifica com k-NN
from sklearn.metrics import accuracy_score          # métrica: % de acertos


# ---------------------------------------------------------------------------
# DADOS — X = atributos, y = rótulo (alvo)
# ---------------------------------------------------------------------------
# return_X_y=True → devolve direto (X, y), sem o objeto Bunch
# X: matriz 2D (amostras × atributos)  |  y: vetor 1D (classe de cada amostra)
X, y = load_iris(return_X_y=True)


# ---------------------------------------------------------------------------
# 1. DIVISÃO EM TREINO E TESTE
# ---------------------------------------------------------------------------
# Sempre ANTES de qualquer fit (scaler ou modelo) → evita data leakage
X_train, X_test, y_train, y_test = train_test_split(
    X,                  # atributos de todas as amostras
    y,                  # rótulos de todas as amostras
    test_size=0.2,      # 20% vai para teste; 80% fica no treino
    random_state=42,    # semente fixa → mesma divisão toda vez que rodar
)
# Resultado:
#   X_train, y_train → usados para APRENDER (scaler + modelo)
#   X_test,  y_test  → usados só para AVALIAR (não entram no fit)


# ---------------------------------------------------------------------------
# 2. PRÉ-PROCESSAMENTO (ESCALONAMENTO) — Transformer
# ---------------------------------------------------------------------------
# StandardScaler: z = (x - média) / desvio
# Deixa cada coluna com média ~0 e desvio ~1 (importante para k-NN)

scaler = StandardScaler()  # cria o Transformer (ainda não aprendeu nada)

# fit_transform no TREINO:
#   fit      → aprende média e desvio de cada coluna do treino
#   transform → aplica a fórmula z usando esses parâmetros
X_train_scaled = scaler.fit_transform(X_train)

# transform (SEM fit) no TESTE:
#   reutiliza média/desvio já aprendidos no treino
#   NUNCA faça fit no teste → isso vazaria informação do futuro
X_test_scaled = scaler.transform(X_test)


# ---------------------------------------------------------------------------
# 3. TREINAMENTO DO MODELO — Predictor
# ---------------------------------------------------------------------------
# KNeighborsClassifier: classifica olhando os k vizinhos mais próximos
model = KNeighborsClassifier(n_neighbors=5)  # k=5 vizinhos

# fit(X, y): o Predictor APRENDE a relação entre atributos e rótulo
# Aqui o k-NN "memoriza" os pontos do treino já escalonados
model.fit(X_train_scaled, y_train)


# ---------------------------------------------------------------------------
# 4. INFERÊNCIA E AVALIAÇÃO
# ---------------------------------------------------------------------------
# predict: gera ŷ (previsões) para as amostras de teste
# Usa X_test_scaled (já transformado com o MESMO scaler do treino)
y_pred = model.predict(X_test_scaled)

# accuracy_score: compara rótulos reais (y_test) com previstos (y_pred)
# Resultado = fração de acertos (ex.: 0.966... = ~96,7%)
print("Acurácia:", accuracy_score(y_test, y_pred))
