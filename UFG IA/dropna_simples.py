import pandas as pd

url = "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
df = pd.read_csv(url)

# 1. Remove qualquer linha com pelo menos um NaN
df_limpo = df.dropna(axis=0)

# 2. Remove colunas inteiras com algum valor nulo
df_sem_colunas = df.dropna(axis=1)

# 3. Remove linhas nulas em uma coluna específica
df_idade = df.dropna(subset=["Age"])

print(len(df), "->", len(df_limpo), "linhas restantes")
print(df.shape[1], "->", df_sem_colunas.shape[1], "colunas restantes")
