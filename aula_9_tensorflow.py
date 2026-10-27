# UNIVERSIDADE FEDERAL DE GOIÁS (UFG)
# INSTITUTO DE INOVAÇÃO EM GESTÃO (IIG)
# DISCIPLINA: IIG0029 - TÉCNICAS DE INTELIGÊNCIA ARTIFICIAL I
# PROFESSOR: PAULO VICTOR DOS SANTOS
# AULA 09: FRAMEWORKS ESSENCIAIS - INTRODUÇÃO AO TENSORFLOW E GRAFOS COMPUTACIONAIS

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Dropout
from tensorflow.keras.callbacks import EarlyStopping

from sklearn.datasets import load_iris, load_digits, make_moons
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score, precision_score, recall_score

print(f"Versão do TensorFlow em execução: {tf.__version__}")

np.random.seed(42)
tf.random.set_seed(42)

# ===============================================================================
# PARTE 1: AQUECIMENTO COM TENSORES E TF.GRADIENTTAPE
# ===============================================================================
print("\n=== PARTE 1: OPERAÇÕES COM TENSORES E TF.GRADIENTTAPE ===")

a = tf.constant([[1.0, 2.0], [3.0, 4.0]], dtype=tf.float32)
w = tf.Variable([[0.5], [0.8]], dtype=tf.float32)
b = tf.Variable(0.1, dtype=tf.float32)

z = tf.matmul(a, w) + b
print("Matriz Entrada (a):\n", a.numpy())
print("Vetor Pesos (w):\n", w.numpy())
print("Saída do Neurônio (z):\n", z.numpy())

x_val = tf.Variable(3.0)
with tf.GradientTape() as tape:
    y_val = x_val**2 + 5.0 * x_val + 2.0

gradiente = tape.gradient(y_val, x_val)
print(f"Função y = x^2 + 5x + 2 em x=3.0 -> Derivada dy/dx calculada pelo TF: {gradiente.numpy():.2f}")

# ===============================================================================
# PARTE 2: CLASSIFICAÇÃO TABULAR COM IRIS DATASET E KERA
# ===============================================================================
print("\n=== PARTE 2: CLASSIFICAÇÃO TABULAR (IRIS DATASET) ===")

iris = load_iris()
X_iris, y_iris = iris.data, iris.target

X_train_iris, X_test_iris, y_train_iris, y_test_iris = train_test_split(
    X_iris, y_iris, test_size=0.3, random_state=42, stratify=y_iris
)

scaler_iris = StandardScaler()
X_train_iris_std = scaler_iris.fit_transform(X_train_iris)
X_test_iris_std = scaler_iris.transform(X_test_iris)

model_iris = Sequential([
    Dense(16, activation='relu', input_shape=(4,), name='Oculta_1'),
    Dense(8, activation='relu', name='Oculta_2'),
    Dense(3, activation='softmax', name='Saida_Flores')
])

model_iris.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("\nResumo do Modelo Iris:")
model_iris.summary()

history_iris = model_iris.fit(
    X_train_iris_std, y_train_iris,
    epochs=60, batch_size=16,
    validation_split=0.2, verbose=0
)

test_loss_iris, test_acc_iris = model_iris.evaluate(X_test_iris_std, y_test_iris, verbose=0)
y_pred_probs_iris = model_iris.predict(X_test_iris_std, verbose=0)
y_pred_iris = np.argmax(y_pred_probs_iris, axis=1)

f1_iris = f1_score(y_test_iris, y_pred_iris, average='weighted')
prec_iris = precision_score(y_test_iris, y_pred_iris, average='weighted')
rec_iris = recall_score(y_test_iris, y_pred_iris, average='weighted')

print(f"\nDesempenho no Teste (Iris):")
print(f"Acurácia:  {test_acc_iris*100:.2f}%")
print(f"Precisão:  {prec_iris*100:.2f}%")
print(f"Recall:    {rec_iris*100:.2f}%")
print(f"F1-Score:  {f1_iris*100:.2f}%")

# ===============================================================================
# PARTE 3: VISÃO COMPUTACIONAL COM DIGITS DATASET
# ===============================================================================
print("\n=== PARTE 3: VISÃO COMPUTACIONAL (DIGITS DATASET) ===")

digits = load_digits()
X_digits, y_digits = digits.data, digits.target

X_digits_norm = X_digits / 16.0

X_train_dig, X_test_dig, y_train_dig, y_test_dig = train_test_split(
    X_digits_norm, y_digits, test_size=0.25, random_state=42, stratify=y_digits
)

model_digits = Sequential([
    Dense(64, activation='relu', input_shape=(64,), name='Pixels_Entrada'),
    Dropout(0.2, name='Preenchendo_Overfitting'),
    Dense(32, activation='relu', name='Camada_Oculta'),
    Dense(10, activation='softmax', name='Classificador_Digitos')
])

model_digits.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

history_digits = model_digits.fit(
    X_train_dig, y_train_dig,
    epochs=100, batch_size=32,
    validation_split=0.2,
    callbacks=[early_stop], verbose=0
)

test_loss_dig, test_acc_dig = model_digits.evaluate(X_test_dig, y_test_dig, verbose=0)
y_pred_probs_dig = model_digits.predict(X_test_dig, verbose=0)
y_pred_dig = np.argmax(y_pred_probs_dig, axis=1)

f1_dig = f1_score(y_test_dig, y_pred_dig, average='weighted')
prec_dig = precision_score(y_test_dig, y_pred_dig, average='weighted')
rec_dig = recall_score(y_test_dig, y_pred_dig, average='weighted')

print(f"\nDesempenho no Teste (Digits Visão Computacional):")
print(f"Acurácia:  {test_acc_dig*100:.2f}%")
print(f"Precisão:  {prec_dig*100:.2f}%")
print(f"Recall:    {rec_dig*100:.2f}%")
print(f"F1-Score:  {f1_dig*100:.2f}%")

# ===============================================================================
# PARTE 4: COMPARATIVO DE FRONTEIRAS DE DECISÃO 2D (MAKE_MOONS)
# ===============================================================================
print("\n=== PARTE 4: FRONTEIRAS DE DECISÃO 2D (MAKE_MOONS) ===")

X_moons, y_moons = make_moons(n_samples=400, noise=0.25, random_state=42)
X_m_train, X_m_test, y_m_train, y_m_test = train_test_split(X_moons, y_moons, test_size=0.3, random_state=42)

model_lin = Sequential([Dense(1, activation='sigmoid', input_shape=(2,))])
model_lin.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model_lin.fit(X_m_train, y_m_train, epochs=80, verbose=0)

model_deep = Sequential([
    Dense(32, activation='relu', input_shape=(2,)),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')
])
model_deep.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model_deep.fit(X_m_train, y_m_train, epochs=80, verbose=0)

acc_lin = accuracy_score(y_m_test, (model_lin.predict(X_m_test, verbose=0)>0.5).astype(int))
acc_deep = accuracy_score(y_m_test, (model_deep.predict(X_m_test, verbose=0)>0.5).astype(int))

print(f"Acurácia Modelo Linear em Keras: {acc_lin*100:.2f}%")
print(f"Acurácia Modelo Profundo em Keras: {acc_deep*100:.2f}%")

# ===============================================================================
# PARTE 5: CONSOLIDAÇÃO COMPARATIVA
# ===============================================================================
print("\n=== PARTE 5: TABELA CONSOLIDADA DE RESULTADOS ===")

df_res = pd.DataFrame([
    {"Modelo / Dataset": "Keras Linear (Moons 2D)", "Acurácia": f"{acc_lin*100:.2f}%", "F1-Score": f"{f1_score(y_m_test, (model_lin.predict(X_m_test, verbose=0)>0.5).astype(int), average='weighted')*100:.2f}%"},
    {"Modelo / Dataset": "Keras Deep MLP (Moons 2D)", "Acurácia": f"{acc_deep*100:.2f}%", "F1-Score": f"{f1_score(y_m_test, (model_deep.predict(X_m_test, verbose=0)>0.5).astype(int), average='weighted')*100:.2f}%"},
    {"Modelo / Dataset": "Keras MLP (Iris Tabular)", "Acurácia": f"{accuracy_score(y_test_iris, y_pred_iris)*100:.2f}%", "F1-Score": f"{f1_iris*100:.2f}%"},
    {"Modelo / Dataset": "Keras Vision MLP (Digits)", "Acurácia": f"{accuracy_score(y_test_dig, y_pred_dig)*100:.2f}%", "F1-Score": f"{f1_dig*100:.2f}%"}
])

print(df_res.to_string(index=False))
print("\nExecução finalizada com sucesso!")
