"""
Tópico 1 — Scikit-Learn e o fluxo de Machine Learning
IIG0029 - Técnicas de IA I | Aula 06

Objetivo deste arquivo:
  Entender a interface padronizada do Scikit-Learn:
    Estimator  → aprende parâmetros com fit()
    Transformer → prepara/modifica X com transform() / fit_transform()
    Predictor  → faz previsões com predict()

Analogia do material:
  Controle remoto universal — muda a TV (algoritmo), mas os botões
  (fit / transform / predict) ficam sempre no mesmo lugar.
"""

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.base import BaseEstimator, TransformerMixin, ClassifierMixin


# =============================================================================
# 1) O QUE É CADA PEÇA? (visão conceitual)
# =============================================================================
#
#   Estimator (base de quase tudo)
#   -----------------------------
#   Qualquer objeto que "aprende" algo dos dados via fit().
#   Exemplos: StandardScaler, SimpleImputer, KNeighborsClassifier.
#
#   Transformer (é um Estimator que TRANSFORM A X)
#   -----------------------------------------------
#   Trabalha só com os atributos X (não prevê y).
#   Usa transform() depois de fit(), ou fit_transform() de uma vez.
#   Exemplos: StandardScaler, PCA, SimpleImputer.
#
#   Predictor (é um Estimator que PREVÊ y)
#   --------------------------------------
#   Aprende a relação entre X e y no fit(X, y).
#   Depois usa predict(X_novos) para gerar ŷ.
#   Exemplos: KNeighborsClassifier, LinearRegression, SVC.
#
#   Fluxo do material:
#
#     Dados brutos (X)  →  Transformer  →  Dados preparados  →  Predictor  →  Predição (ŷ)
#                          (ex: scaler)                         (ex: k-NN)
#
#   Regra de ouro:
#     Transformer reorganiza APENAS X.
#     Predictor usa X e y para aprender a associação entre eles.
#


# =============================================================================
# 2) DADOS DE EXEMPLO (Iris — clássico e pequeno)
# =============================================================================
# X: matriz 2D (n_amostras × n_atributos)  → 150 flores × 4 medidas
# y: vetor 1D (rótulo da espécie)           → 0, 1 ou 2
iris = load_iris()
X = iris.data
y = iris.target

print("=" * 60)
print("TÓPICO 1 — Scikit-Learn: Estimators, Transformers, Predictors")
print("=" * 60)
print(f"X shape: {X.shape}  |  y shape: {y.shape}")
print(f"Classes: {iris.target_names}")


# =============================================================================
# 3) DIVIDIR TREINO / TESTE (sempre ANTES de fit)
# =============================================================================
# Por quê? Se o scaler "olhar" o teste no fit(), há vazamento de informação
# (data leakage). O teste deve simular dados futuros, desconhecidos.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\nTreino: {X_train.shape[0]} amostras | Teste: {X_test.shape[0]} amostras")


# =============================================================================
# 4) TRANSFORMER NA PRÁTICA — StandardScaler
# =============================================================================
# O StandardScaler é Estimator + Transformer.
#
#   fit(X_train)           → aprende média e desvio de CADA coluna do treino
#   transform(X)           → aplica z = (x - média) / desvio
#   fit_transform(X_train) → atalho: fit + transform no mesmo passo
#
# IMPORTANTE:
#   fit_transform só no TREINO
#   transform (sem fit) no TESTE — reutiliza média/desvio já aprendidos

scaler = StandardScaler()  # ainda não aprendeu nada

# Aprende parâmetros (média, desvio) E transforma o treino
X_train_scaled = scaler.fit_transform(X_train)

# Só transforma o teste com os parâmetros do treino
X_test_scaled = scaler.transform(X_test)

print("\n--- Transformer (StandardScaler) ---")
print(f"Média aprendida no treino (4 atributos): {scaler.mean_.round(2)}")
print(f"Desvio aprendido no treino:              {scaler.scale_.round(2)}")
print(f"Média de X_train_scaled (~0):            {X_train_scaled.mean(axis=0).round(3)}")


# =============================================================================
# 5) PREDICTOR NA PRÁTICA — KNeighborsClassifier
# =============================================================================
# O k-NN é Estimator + Predictor (não é Transformer).
#
#   fit(X_train_scaled, y_train) → "memoriza" os pontos rotulados
#   predict(X_test_scaled)       → classifica cada ponto novo pelos vizinhos
#   score(X, y)                  → acurácia (método conveniente)

model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train_scaled, y_train)  # aprende a relação X → y

y_pred = model.predict(X_test_scaled)  # gera ŷ

print("\n--- Predictor (KNeighborsClassifier) ---")
print(f"Primeiras 10 previsões: {y_pred[:10]}")
print(f"Primeiros 10 reais:     {y_test[:10]}")
print(f"Acurácia: {accuracy_score(y_test, y_pred):.3f}")


# =============================================================================
# 6) DIFERENÇA QUE CAI NA PROVA (Transformer vs Predictor)
# =============================================================================
#
#   Transformer
#     - Pré-processa os atributos X (padronizar, imputar, reduzir dimensão...).
#     - Aprende parâmetros no treino (média, mediana, componentes PCA...).
#     - Não prevê a variável alvo y.
#     - Métodos: fit(), transform(), fit_transform().
#
#   Predictor
#     - Aprende a relação entre X e y.
#     - Usa essa relação para prever ŷ em dados novos.
#     - Métodos: fit(), predict(), score().
#
# Resposta-modelo (como no material):
#   "O Transformer é responsável pelo pré-processamento dos atributos X,
#    como padronização ou imputação. Ele aprende os parâmetros necessários
#    no conjunto de treino e transforma os dados. Já o Predictor aprende a
#    relação entre X e y e utiliza essa relação para realizar previsões em
#    novos dados."
#


# =============================================================================
# 7) HIERARQUIA MENTAL (quem é o quê)
# =============================================================================
#
#                    ┌─────────────────────┐
#                    │     Estimator       │
#                    │   (tem fit(...))    │
#                    └──────────┬──────────┘
#               ┌───────────────┴───────────────┐
#               ▼                               ▼
#      ┌────────────────┐              ┌────────────────┐
#      │  Transformer   │              │   Predictor    │
#      │ transform()    │              │  predict()     │
#      │ fit_transform()│              │  score()       │
#      └────────────────┘              └────────────────┘
#         StandardScaler                 KNeighborsClassifier
#         SimpleImputer                  LinearRegression
#         PCA                            SVC
#
# Observação: um objeto pode ser Estimator E Transformer (scaler),
# ou Estimator E Predictor (classificador). A base comum é sempre o fit().
#


# =============================================================================
# 8) MINI-DEMO: como o Scikit-Learn "reconhece" cada tipo
# =============================================================================
# Internamente, a API usa herança/mixins. Você não precisa criar classes
# próprias na prova — mas ver o padrão ajuda a fixar a ideia.

class MeuTransformer(BaseEstimator, TransformerMixin):
    """Exemplo didático: dobra cada valor de X (não usa y)."""

    def fit(self, X, y=None):
        # Aprenderia parâmetros aqui (neste exemplo não há o que aprender)
        return self

    def transform(self, X):
        return np.asarray(X) * 2


class MeuPredictor(BaseEstimator, ClassifierMixin):
    """Exemplo didático: sempre prevê a classe mais frequente do treino."""

    def fit(self, X, y):
        # Aprende um único parâmetro: a moda de y
        valores, contagens = {}, {}
        for rotulo in y:
            contagens[rotulo] = contagens.get(rotulo, 0) + 1
        self.classe_mais_frequente_ = max(contagens, key=contagens.get)
        return self

    def predict(self, X):
        return [self.classe_mais_frequente_] * len(X)


demo_t = MeuTransformer()
X_demo = demo_t.fit_transform([[1.0, 2.0], [3.0, 4.0]])
print("\n--- Mini Transformer caseiro ---")
print(f"Entrada [[1,2],[3,4]] -> saida: {X_demo.tolist()}")

demo_p = MeuPredictor()
demo_p.fit(X_train, y_train)
print("\n--- Mini Predictor caseiro ---")
print(f"Classe mais frequente no treino: {demo_p.classe_mais_frequente_}")
print(f"Previsões em 5 amostras de teste: {demo_p.predict(X_test[:5])}")


# =============================================================================
# 9) FLUXO COMPLETO EM 4 LINHAS (o que decorar)
# =============================================================================
#
#   1. split        → train_test_split(X, y)
#   2. transformar  → scaler.fit_transform(treino)  /  scaler.transform(teste)
#   3. treinar      → model.fit(X_treino_prep, y_treino)
#   4. prever       → model.predict(X_teste_prep)
#
# Isso é exatamente o pipeline do slide:
#   dados brutos → Transformer → dados preparados → Predictor → predição
#

print("\n" + "=" * 60)
print("Resumo rapido")
print("=" * 60)
print("Estimator  = tem fit()")
print("Transformer = prepara X (transform / fit_transform)")
print("Predictor  = preve y (predict)")
print("Fluxo     = brutos -> Transformer -> preparados -> Predictor -> y_hat")
print("=" * 60)
