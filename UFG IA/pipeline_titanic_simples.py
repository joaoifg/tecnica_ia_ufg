"""
Pipeline completo de preparacao de dados - Titanic Dataset
IIG0029 - Tecnicas de IA I

Objetivo: prever quais passageiros sobreviveram (Survived = 0 ou 1)
com base em Idade, Classe, Tarifa e Sexo.

Fluxo do pipeline:
  titanic.csv -> selecao de colunas -> split treino/teste ->
  One-Hot Encoding -> imputacao de Age -> StandardScaler -> pronto p/ modelo

Regra de ouro: primeiro train_test_split, depois fit() SOMENTE no treino!
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

# =============================================================================
# PASSO 1 - Carregar os dados
# =============================================================================
# O dataset tem 891 passageiros e 12 colunas.
# Problemas conhecidos:
#   - Age: ~20% de valores faltando (precisa imputacao)
#   - Cabin: ~77% nulos (descartada neste pipeline)
#   - Sex: texto (precisa virar numero com One-Hot Encoding)
url = "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
df = pd.read_csv(url)

# =============================================================================
# PASSO 2 - Selecionar features (X) e alvo (y), depois dividir treino/teste
# =============================================================================
# X = variaveis de entrada (o que o modelo usa para prever)
# y = variavel alvo (o que queremos prever: sobreviveu ou nao)
X = df[["Age", "Pclass", "Fare", "Sex"]]
y = df["Survived"]

# 80% treino (712 linhas) + 20% teste (179 linhas)
# random_state=42 garante a mesma divisao toda vez que rodar o script
# IMPORTANTE: o split vem ANTES de qualquer transformacao (imputer, scaler...)
# para evitar "vazamento de dados" (data leakage)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =============================================================================
# PASSO 3 - One-Hot Encoding na coluna categorica "Sex"
# =============================================================================
# Modelos de ML trabalham com numeros, nao com texto ("male"/"female").
# get_dummies cria colunas binarias (0 ou 1):
#   Sex_male = 1 se homem, 0 se mulher
# drop_first=True remove uma coluna redundante (evita multicolinearidade)
# Exemplo: se Sex_male=0, ja sabemos que e female (nao precisa de 2 colunas)
X_train = pd.get_dummies(X_train, columns=["Sex"], drop_first=True)
X_test = pd.get_dummies(X_test, columns=["Sex"], drop_first=True)

# =============================================================================
# PASSO 4 - Imputacao de valores ausentes em "Age"
# =============================================================================
# Age tem 177 nulos no dataset completo.
# SimpleImputer com strategy="median" preenche cada NaN com a mediana (~28 anos).
#
# fit_transform(X_train) -> aprende a mediana NO TREINO e aplica la
# transform(X_test)      -> usa a MESMA mediana do treino no teste
# (nunca fit no teste! senao o modelo "espiaria" dados futuros)
imputer = SimpleImputer(strategy="median")
X_train_imputed = imputer.fit_transform(X_train)
X_test_imputed = imputer.transform(X_test)

# =============================================================================
# PASSO 5 - Escalonamento com StandardScaler
# =============================================================================
# As colunas tem escalas muito diferentes:
#   Age    -> 0 a 80 anos
#   Fare   -> 0 a 500+
#   Pclass -> 1, 2 ou 3
# Sem padronizar, Fare domina o calculo de distancias nos algoritmos.
#
# StandardScaler transforma cada coluna: z = (x - media) / desvio_padrao
# Resultado: media ~ 0 e desvio ~ 1 em cada coluna do treino
#
# Mesma regra: fit_transform no treino, transform no teste
scaler = StandardScaler()
X_train_final = scaler.fit_transform(X_train_imputed)
X_test_final = scaler.transform(X_test_imputed)

# =============================================================================
# Resultado final
# =============================================================================
# Treino: 712 linhas x 4 colunas (Age, Pclass, Fare, Sex_male)
# Teste:  179 linhas x 4 colunas
# Dados prontos para alimentar um classificador (ex: KNN, Regressao Logistica)
print("Treino preparado (shape):", X_train_final.shape)
print("Teste preparado (shape):", X_test_final.shape)
