import pandas as pd
from sklearn.impute import KNNImputer

url = "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
df = pd.read_csv(url)

df_num = df[["Age", "Pclass", "Fare", "SibSp"]]

knn_imputer = KNNImputer(n_neighbors=5)
X_imputado = knn_imputer.fit_transform(df_num)

df_knn = pd.DataFrame(X_imputado, columns=df_num.columns)

print("Idade media (KNN):", round(df_knn["Age"].mean(), 1))
