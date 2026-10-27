"""
Eliminação de dados nulos com pandas.dropna()
Dataset: Titanic (fonte oficial do pandas / Kaggle)

Em Python, a eliminação de valores ausentes (NaN) é feita com o método dropna().
Este script mostra três formas comuns de uso.
"""

import pandas as pd

# ---------------------------------------------------------------------------
# Carregamento dos dados reais do Titanic
# ---------------------------------------------------------------------------
url = "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
df = pd.read_csv(url)

print("Dataset original:", df.shape[0], "linhas x", df.shape[1], "colunas")
print()

# ---------------------------------------------------------------------------
# Visualizacao do dataset
# ---------------------------------------------------------------------------
# Amostra rapida no terminal (primeiras e ultimas linhas)
print("Primeiras 5 linhas:")
print(df.head())
print()

print("Ultimas 5 linhas:")
print(df.tail())
print()

# Estrutura: colunas, tipos e contagem de nulos
print("Informacoes do dataset:")
df.info()
print()

# Estatisticas das colunas numericas
print("Estatisticas descritivas:")
print(df.describe())
print()

# Exporta para CSV e abre confortavelmente no Excel ou VS Code
arquivo_csv = "titanic_completo.csv"
df.to_csv(arquivo_csv, index=False)
print(f"Dataset completo salvo em: {arquivo_csv}")
print()

# Para ver TODAS as 891 linhas no terminal, descomente as 3 linhas abaixo:
# pd.set_option("display.max_rows", None)
# pd.set_option("display.max_columns", None)
# print(df.to_string())
print()

# ---------------------------------------------------------------------------
# 1. Remove qualquer linha que tenha pelo menos um valor nulo (NaN)
# ---------------------------------------------------------------------------
# axis=0  -> opera nas linhas (padrão)
# how='any' -> remove a linha se QUALQUER coluna tiver NaN (também é o padrão)
df_limpo = df.dropna(axis=0)

print("1) dropna(axis=0) - remove linhas com qualquer NaN:")
print(f"   {len(df)} -> {len(df_limpo)} linhas restantes")
print()

# ---------------------------------------------------------------------------
# 2. Remove colunas inteiras que possuem algum valor nulo
# ---------------------------------------------------------------------------
# axis=1  -> opera nas colunas
# Qualquer coluna com pelo menos um NaN e descartada por completo
df_sem_colunas = df.dropna(axis=1)

print("2) dropna(axis=1) - remove colunas com qualquer NaN:")
print(f"   {df.shape[1]} -> {df_sem_colunas.shape[1]} colunas restantes")
print()

# ---------------------------------------------------------------------------
# 3. Remove apenas linhas nulas em uma coluna especifica
# ---------------------------------------------------------------------------
# subset=['Age'] -> so considera NaN na coluna Age
# Linhas sem idade sao removidas; NaN em outras colunas sao ignorados
df_idade = df.dropna(subset=["Age"])

print("3) dropna(subset=['Age']) - remove linhas sem idade:")
print(f"   {len(df)} -> {len(df_idade)} linhas restantes")
print()

# ---------------------------------------------------------------------------
# Resumo visual (opcional)
# ---------------------------------------------------------------------------
print("Colunas removidas no passo 2:", set(df.columns) - set(df_sem_colunas.columns))
