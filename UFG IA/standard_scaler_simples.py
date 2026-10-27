import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

url = "https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv"
df = pd.read_csv(url)

cols = ["Age", "Fare", "Pclass"]
X = df[cols].fillna(df[cols].median())

X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

scaler = StandardScaler()
scaler.fit(X_train)  # media/desvio so do treino!
X_train_std = scaler.transform(X_train)
X_test_std = scaler.transform(X_test)

print("Media de Age apos StandardScaler:", round(X_train_std[:, 0].mean(), 2))
