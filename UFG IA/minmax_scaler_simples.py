import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

url = "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
df = pd.read_csv(url)

cols = ["Age", "Fare", "Pclass"]
X = df[cols].fillna(df[cols].median())

X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

scaler = MinMaxScaler()
X_train_norm = scaler.fit_transform(X_train)  # fit_transform so no treino
X_test_norm = scaler.transform(X_test)        # teste: so transform!

print(round(X_train_norm[:, 0].min(), 2), round(X_train_norm[:, 0].max(), 2))
