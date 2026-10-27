import pandas as pd
from sklearn.impute import SimpleImputer

url = "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
df = pd.read_csv(url)

df_num = df[["Age", "Pclass", "Fare", "SibSp"]]

imputer = SimpleImputer(strategy="median")
X = imputer.fit_transform(df_num)

print("Nulos em 'Age' antes:", df_num["Age"].isna().sum())
print("Mediana usada:", imputer.statistics_[0])
