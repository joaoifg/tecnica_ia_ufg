# Guia Completo de Estudo — Aula 06
## IIG0029 — Técnicas de IA I
### Algoritmos Clássicos de Machine Learning com Scikit-Learn

> **Foco deste material:** revisão para **prova escrita**.  
> A ideia é você conseguir **explicar os conceitos com palavras**, interpretar exemplos, reconhecer fórmulas e justificar escolhas.

---

# 1. Visão geral da aula

A Aula 06 foi organizada em cinco blocos principais:

1. Arquitetura e filosofia do **Scikit-Learn**;
2. Algoritmos clássicos de **classificação**;
3. Algoritmos clássicos de **regressão**;
4. **Métricas de avaliação** e **matriz de confusão**;
5. Atividade prática com notebook.

A lógica central da aula inteira é:

**entender os dados → separar treino e teste → pré-processar → treinar → prever → avaliar → interpretar**

Essa sequência aparece várias vezes e é uma das coisas mais importantes para a prova.

---

# 2. O que é o Scikit-Learn

O **Scikit-Learn (sklearn)** é uma biblioteca de Machine Learning em Python.

Ele trabalha em conjunto com outras bibliotecas, como:

- **NumPy** — arrays e cálculos numéricos;
- **Pandas** — tabelas/DataFrames;
- **Matplotlib** — gráficos;
- **SciPy** — computação científica.

## Analogia do controle remoto universal

O professor compara o Scikit-Learn a um **controle remoto universal**.

Mesmo mudando a “marca da TV”, os botões principais continuam parecidos.

No Scikit-Learn acontece algo semelhante:

- diferentes algoritmos usam métodos parecidos;
- geralmente usamos `fit()`, `transform()`, `predict()` e `score()`;
- por isso é relativamente fácil trocar um algoritmo por outro.

### Frase para prova

> O Scikit-Learn padroniza a forma de utilizar diferentes algoritmos de Machine Learning por meio de uma API consistente.

---

# 3. Estimator, Transformer e Predictor

Essa parte é muito importante.

## 3.1 Estimator

Um **Estimator** é qualquer objeto que **aprende alguma coisa a partir dos dados**.

Método principal:

```python
fit(X, y)
```

Pense assim:

> **Estimator = aprende**

Exemplos:

- `StandardScaler`;
- `KNeighborsClassifier`;
- `LinearRegression`.

---

## 3.2 Transformer

Um **Transformer** pega os dados e **transforma/prepara** esses dados.

Métodos principais:

```python
transform(X)
fit_transform(X)
```

Exemplos:

- `StandardScaler`;
- `PCA`;
- `SimpleImputer`.

Pense assim:

> **Transformer = prepara os dados**

Exemplo:

```text
Dados brutos
   ↓
StandardScaler
   ↓
Dados padronizados
```

---

## 3.3 Predictor

Um **Predictor** é capaz de fazer previsões em novos dados.

Método principal:

```python
predict(X)
```

Exemplos:

- `KNeighborsClassifier`;
- `SVC`;
- `LinearRegression`.

Pense assim:

> **Predictor = prevê**

---

## 3.4 Macete principal

```text
FIT       → aprende
TRANSFORM → prepara
PREDICT   → prevê
```

Ou:

> **Estimator aprende, Transformer prepara, Predictor prevê.**

---

# 4. X e y

No Machine Learning supervisionado, normalmente trabalhamos com **X** e **y**.

## X

É o conjunto de **características/atributos/features** usados como entrada.

Exemplo no Iris:

- comprimento da pétala;
- largura da pétala;
- comprimento da sépala;
- largura da sépala.

## y

É a **resposta**, **rótulo**, **target** ou **label** que queremos prever.

Exemplo no Iris:

- Setosa;
- Versicolor;
- Virginica.

Exemplo no câncer de mama:

- maligno;
- benigno.

### Estrutura

- **X** é normalmente uma matriz 2D: amostras × atributos;
- **y** é normalmente um vetor 1D.

### Frase para prova

> X contém as características de entrada e y contém a variável alvo que o modelo deve aprender a prever.

---

# 5. Pipeline: como as etapas se encaixam

Uma pipeline típica pode ser pensada assim:

```text
Dados brutos (X)
      ↓
Transformer
      ↓
Dados preparados
      ↓
Predictor
      ↓
Predição (ŷ)
```

O **Transformer** trabalha principalmente sobre **X**.

O **Predictor** aprende a relação entre **X e y**.

---

# 6. Divisão em treino e teste

Antes de treinar um modelo, dividimos os dados.

Exemplo:

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

## O que significa?

- `X_train` → características usadas para treino;
- `y_train` → respostas corretas do treino;
- `X_test` → características reservadas para teste;
- `y_test` → respostas corretas do teste.

### Proporções comuns

- `test_size=0.1` → 90% treino / 10% teste;
- `test_size=0.2` → 80% treino / 20% teste;
- `test_size=0.3` → 70% treino / 30% teste.

### Por que fazemos isso?

Porque o modelo precisa ser avaliado em dados que ele **não viu durante o treinamento**.

### Frase para prova

> A divisão treino/teste permite verificar a capacidade de generalização do modelo em dados não utilizados no treinamento.

---

# 7. Data Leakage (vazamento de dados)

**Data leakage** acontece quando informações que deveriam estar disponíveis somente na avaliação acabam influenciando o treinamento.

Exemplo errado:

```python
scaler.fit(X_test)
```

O teste não deveria ensinar nada ao modelo nem ao pré-processamento.

## Regra de ouro

> **Fit somente no treino.**

Exemplo correto:

```python
scaler.fit_transform(X_train)
scaler.transform(X_test)
```

### Frase para prova

> Data leakage é o vazamento de informações do conjunto de teste para o processo de treinamento, produzindo uma avaliação artificialmente otimista.

---

# 8. StandardScaler e padronização

O `StandardScaler` faz **padronização**.

Ele transforma os dados para que, aproximadamente:

- média = **0**;
- desvio padrão = **1**.

## Fórmula conceitual

```text
(valor - média) / desvio padrão
```

Depois da padronização:

- valores negativos → abaixo da média;
- 0 → próximo da média;
- valores positivos → acima da média.

Exemplo:

```text
-1 → 1 desvio padrão abaixo da média
 0 → na média
+1 → 1 desvio padrão acima da média
```

## Importante

Padronização **não é** balanceamento de classes.

Padronização resolve **diferenças de escala entre atributos**.

Balanceamento resolve **diferenças de quantidade entre classes**.

### Macete

> **StandardScaler = média 0 e desvio 1.**

---

# 9. Fluxo padrão no Scikit-Learn

A sequência típica é:

```text
1. Dividir os dados
2. Pré-processar
3. Treinar
4. Prever
5. Avaliar
```

Ou:

```text
Split → Transform → Fit → Predict → Evaluate
```

Esse fluxo é central na aula.

---

# 10. Classificação x Regressão

## Classificação

Usada quando queremos prever uma **categoria/classe**.

Exemplos:

- maligno ou benigno;
- fraude ou não fraude;
- Setosa, Versicolor ou Virginica.

## Regressão

Usada quando queremos prever um **valor numérico contínuo**.

Exemplos:

- preço de uma casa;
- temperatura;
- faturamento;
- demanda.

### Macete

> **Classificação = qual classe?**  
> **Regressão = qual valor?**

---

# 11. Fronteira de decisão

Em classificação, o modelo tenta dividir o espaço dos atributos em regiões correspondentes às classes.

Isso é chamado de **fronteira de decisão**.

## Fronteira linear

Uma reta, plano ou hiperplano.

Exemplos:

- Regressão Logística;
- SVM Linear.

## Fronteira não linear

Uma fronteira mais flexível ou curva.

Exemplos:

- k-NN;
- SVM com kernel RBF;
- Árvores de decisão.

### Macete

> **Linear = reta.**  
> **Não linear = contorna melhor distribuições complexas.**

---

# 12. k-Nearest Neighbors (k-NN)

O **k-NN** classifica um ponto novo olhando os **k vizinhos mais próximos**.

## Como funciona

Se `k = 5`, o modelo observa os 5 vizinhos mais próximos.

Exemplo:

```text
3 vizinhos = Classe A
2 vizinhos = Classe B
```

Resultado:

> Classe A

Porque venceu a votação.

---

## 12.1 Lazy Learning

O k-NN é chamado de **Lazy Learner**.

Ele não cria uma função matemática complexa durante o treinamento.

Ele basicamente armazena os dados e, quando chega um novo ponto, procura os vizinhos mais próximos.

### Frase para prova

> O k-NN é chamado de Lazy Learner porque realiza grande parte do trabalho no momento da predição, usando os exemplos armazenados do treinamento.

---

## 12.2 Distância euclidiana

O k-NN normalmente utiliza distância euclidiana.

Fórmula:

```text
d(x, x') = √Σ(xᵢ - x'ᵢ)²
```

A lógica é:

```text
diferença → quadrado → soma → raiz
```

### Por que elevar ao quadrado?

Para eliminar o sinal negativo e medir distância corretamente.

---

## 12.3 Valor de k

### k muito pequeno

Exemplo: `k = 1`.

Pode gerar:

- alta variância;
- fronteira muito irregular;
- **overfitting**.

### k muito grande

Exemplo: `k = 50`.

Pode gerar:

- alto viés;
- fronteira excessivamente suave;
- **underfitting**.

### Macete

> **k pequeno → overfitting**  
> **k grande → underfitting**

---

## 12.4 k-NN e escalonamento

O k-NN depende de **distâncias**.

Por isso, atributos em escalas muito diferentes podem distorcer a decisão.

Por esse motivo, normalmente é importante aplicar padronização.

---

# 13. Regressão Logística

Apesar do nome “regressão”, a **Regressão Logística** é usada para **classificação**.

Ela aprende uma fronteira de decisão geralmente linear e utiliza uma função sigmoide para produzir probabilidades.

### Ideia principal

> Regressão Logística = classificador linear baseado em probabilidade.

---

# 14. Árvore de Decisão

A árvore de decisão funciona por regras do tipo:

```text
SE condição
ENTÃO caminho A
SENÃO caminho B
```

Exemplo do Iris:

```text
Largura da pétala <= 0,8?
├── Sim → Setosa
└── Não
     ↓
Comprimento da pétala <= 4,9?
├── Sim → Versicolor
└── Não → Virginica
```

---

## 14.1 Características importantes

### Interpretável

Árvores pequenas são fáceis de explicar.

### Não precisa de escalonamento

Árvores não trabalham diretamente com distância, portanto normalmente não precisam de normalização/padronização.

### Risco de overfitting

Se crescer demais, pode decorar os dados de treino.

---

## 14.2 max_depth

`max_depth` controla a profundidade máxima da árvore.

Pense como uma poda.

> **Árvore muito grande → pode decorar o treino.**

---

## 14.3 min_samples_split

Define o número mínimo de amostras necessário para permitir uma nova divisão.

Ajuda a controlar o crescimento da árvore.

---

# 15. SVM — Support Vector Machine

O **SVM** procura uma fronteira que separe as classes com a **maior margem possível**.

## Conceitos principais

### Hiperplano

É a fronteira de decisão.

### Margem

Distância entre o hiperplano e os pontos mais próximos das classes.

### Vetores de suporte

São os pontos mais próximos da margem.

Eles são muito importantes porque ajudam a definir a posição da fronteira.

### Macete

> **SVM = separar com a maior margem possível.**

---

## 15.1 Kernel Trick

Permite ao SVM trabalhar com separações não lineares.

Exemplos:

- kernel RBF/Gaussiano;
- kernel polinomial.

## Hiperparâmetros importantes

### C

Controla a penalidade por erros/violações da margem.

### gamma (γ)

Controla o raio de influência dos pontos no kernel RBF.

---

# 16. Naive Bayes

O **Naive Bayes** usa o Teorema de Bayes.

Sua hipótese clássica é que os atributos são independentes entre si, dada a classe.

### Macete

> **Naive Bayes = probabilidade + Teorema de Bayes.**

---

# 17. Comparando classificadores

Na aula foram comparados:

- k-NN;
- Regressão Logística;
- Árvore de Decisão;
- SVM;
- Naive Bayes.

## Ideia importante

Algoritmos diferentes podem atingir a **mesma acurácia**, mas criar fronteiras de decisão diferentes.

Portanto:

> **Mesma acurácia não significa mesmo comportamento.**

E:

> **Não existe um melhor algoritmo universal.**

A escolha depende dos dados e do problema.

---

# 18. Como escolher um modelo

O correto é:

```text
mesmos dados
   ↓
mesmo split
   ↓
modelos diferentes
   ↓
comparar métricas
```

Não basta olhar apenas acurácia.

Também podemos olhar:

- precisão;
- recall;
- F1-score;
- matriz de confusão;
- estabilidade;
- overfitting/underfitting;
- interpretabilidade;
- custo computacional.

---

# 19. Regressão — principais algoritmos

## 19.1 Regressão Linear (OLS)

Tenta ajustar uma relação linear entre X e y.

Objetivo principal:

> minimizar o erro quadrático.

---

## 19.2 Ridge — L2

Adiciona penalização L2.

Ajuda a reduzir overfitting.

### Ideia

> Ridge diminui os coeficientes suavemente.

---

## 19.3 Lasso — L1

Adiciona penalização L1.

Pode levar alguns coeficientes a zero.

### Ideia

> Lasso pode funcionar como seleção automática de atributos.

---

## 19.4 Árvore de Regressão

Funciona como uma árvore de decisão, mas devolve valores numéricos contínuos.

---

## 19.5 SVR

É a versão do SVM para problemas de regressão.

---

# 20. Erro em regressão

Na regressão:

```text
y  = valor real
ŷ  = valor previsto
```

O erro é:

```text
erro = y - ŷ
```

Exemplo:

```text
Valor real:     500.000
Valor previsto: 470.000
Erro:            30.000
```

O objetivo do modelo é reduzir esses erros.

---

# 21. Matriz de Confusão

A matriz de confusão é usada em **classificação**.

Ela compara:

> classe real × classe prevista

Estrutura:

| | Previsto Positivo | Previsto Negativo |
|---|---:|---:|
| **Real Positivo** | VP | FN |
| **Real Negativo** | FP | VN |

---

## 21.1 VP — Verdadeiro Positivo

Era positivo e o modelo previu positivo.

✅ Acerto.

---

## 21.2 VN — Verdadeiro Negativo

Era negativo e o modelo previu negativo.

✅ Acerto.

---

## 21.3 FP — Falso Positivo

Era negativo, mas o modelo previu positivo.

❌ Erro.

---

## 21.4 FN — Falso Negativo

Era positivo, mas o modelo previu negativo.

❌ Erro.

---

## Macete

> **Diagonal principal = acertos.**  
> **Fora da diagonal = erros.**

---

# 22. Acurácia

Acurácia mede quantos o modelo acertou em relação ao total.

```text
Acurácia = (VP + VN) / (VP + VN + FP + FN)
```

### Pergunta que ela responde

> “De tudo que o modelo classificou, quanto ele acertou?”

---

# 23. Precisão

```text
Precisão = VP / (VP + FP)
```

### Pergunta que ela responde

> “De tudo que o modelo chamou de positivo, quantos realmente eram positivos?”

### Macete

> **Precisão olha para os positivos previstos.**

---

# 24. Recall / Revocação

```text
Recall = VP / (VP + FN)
```

### Pergunta que ele responde

> “De todos os positivos reais, quantos o modelo conseguiu encontrar?”

### Macete

> **Recall olha para os positivos reais.**

---

# 25. F1-Score

O F1 combina **Precisão e Recall**.

```text
F1 = 2 × (Precisão × Recall) / (Precisão + Recall)
```

É útil quando precisamos equilibrar precisão e recall.

---

# 26. Exemplo da matriz de confusão do Iris

Na aula apareceu um exemplo em que:

```text
14   1
0   15
```

Interpretação:

- 14 exemplos positivos foram classificados corretamente;
- 1 positivo foi classificado como negativo;
- 15 negativos foram classificados corretamente;
- não houve falso positivo.

Nesse caso:

```text
Precisão = 15/15 = 1,0
Recall ≈ 14/15 ≈ 0,93
```

A ideia principal é:

> a matriz de confusão mostra **qual tipo de erro ocorreu**, e não apenas quantos erros.

---

# 27. Métricas para regressão

Em regressão não usamos matriz de confusão.

Usamos métricas de erro.

---

## 27.1 MAE — Erro Médio Absoluto

```text
MAE = média de |y - ŷ|
```

Interpretação:

> quanto o modelo erra, em média, na unidade original.

Quanto menor, melhor.

---

## 27.2 MSE — Erro Quadrático Médio

```text
MSE = média de (y - ŷ)²
```

Eleva os erros ao quadrado.

Por isso pune erros grandes com mais força.

Quanto menor, melhor.

---

## 27.3 RMSE

```text
RMSE = √MSE
```

Traz o erro novamente para uma escala mais próxima da variável original.

Quanto menor, melhor.

---

## 27.4 R²

O R² mede a proporção da variância explicada pelo modelo.

É uma métrica adimensional.

---

# 28. Parte prática — EDA

A aula prática começou com **EDA — Análise Exploratória de Dados**.

EDA significa:

> entender os dados antes de modelar.

Antes de treinar qualquer modelo, você deve investigar:

- primeiras linhas;
- tipos de dados;
- valores nulos;
- distribuição das classes;
- correlações;
- atributos importantes;
- possíveis outliers.

### Frase para prova

> A EDA é importante porque permite compreender a estrutura, qualidade e comportamento dos dados antes do treinamento do modelo.

---

# 29. Dataset Breast Cancer Wisconsin

Na prática foi utilizado o dataset de câncer de mama.

Objetivo:

> prever se o tumor é **maligno** ou **benigno**.

Logo:

> é um problema de **classificação binária**.

---

# 30. DataFrame

O professor explicou de forma simples:

> **DataFrame = uma tabela/planilha dentro do Python.**

Quem trabalha com DataFrame é principalmente o **Pandas**.

Exemplo:

```python
df = pd.DataFrame(cancer.data, columns=cancer.feature_names)
```

---

# 31. Target e diagnóstico

No dataset:

```text
0 = Maligno
1 = Benigno
```

Foi criada uma coluna de diagnóstico com um mapeamento.

Exemplo:

```python
df['diagnostico'] = df['target'].map({
    0: 'Maligno',
    1: 'Benigno'
})
```

Isso é equivalente a criar uma nova coluna em uma planilha.

---

# 32. Balanceamento de classes

Uma base está balanceada quando as classes têm quantidades parecidas.

Exemplo Iris:

```text
50 Setosa
50 Versicolor
50 Virginica
```

Perfeitamente balanceada.

No Breast Cancer havia mais benignos do que malignos.

Isso pode fazer o modelo favorecer a classe majoritária.

---

# 33. Como lidar com desbalanceamento

## 33.1 Stratify

```python
train_test_split(..., stratify=y)
```

Mantém proporções semelhantes de classes no treino e no teste.

---

## 33.2 Undersampling

Reduz a quantidade da classe majoritária.

Vantagem:

- simples.

Problema:

- joga dados reais fora;
- pode empobrecer o dataset.

---

## 33.3 Oversampling

Aumenta a classe minoritária.

Pode ser feito duplicando exemplos ou criando novos exemplos sintéticos.

---

## 33.4 SMOTE / dados sintéticos

Cria amostras sintéticas da classe minoritária com base em exemplos existentes.

### Regra importante

> Balanceamento deve ser aplicado somente no conjunto de treino, nunca antes do split.

---

# 34. Correlação e mapa de calor

O mapa de calor mostra a correlação entre variáveis.

Os valores variam aproximadamente entre:

```text
-1 e +1
```

## Interpretação

- +1 → relação positiva perfeita;
- 0 → pouca relação linear;
- -1 → relação negativa perfeita.

A correlação de uma variável com ela mesma é sempre:

```text
1,0
```

---

## 34.1 Cuidado importante

Valor negativo **não significa variável ruim**.

Exemplo:

```text
-0,78
```

é uma correlação forte, só que inversa.

O que mede força é o módulo:

```text
|0,99|  → muito forte
|-0,99| → muito forte também
|0,05|  → fraca relação linear
```

---

## 34.2 Correlação alta entre X e X

Quando dois atributos têm correlação muito alta entre si, eles podem estar carregando informação redundante.

Exemplo:

- raio;
- perímetro;
- área.

Essas medidas naturalmente podem estar fortemente relacionadas.

---

# 35. Split no Breast Cancer

Na prática foi usado algo como:

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,
    random_state=42,
    stratify=y
)
```

Resultado aproximado:

```text
398 amostras para treino
171 amostras para teste
```

---

# 36. Padronização na prática

Depois do split:

```python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

O `fit` aprende a média e o desvio no treino.

O `transform` aplica essa mesma transformação.

Por isso aparecem valores negativos e positivos.

---

# 37. k-NN na prática

Exemplo:

```python
knn = KNeighborsClassifier(n_neighbors=7)
knn.fit(X_train_scaled, y_train)
```

Depois o modelo é avaliado em `X_test_scaled`.

Na aula foi mostrado que mudar o valor de `k` altera os resultados.

Exemplo:

```text
k = 5
k = 7
k = 13
k = 22
```

Nem sempre aumentar k melhora.

Isso mostra que `k` é um **hiperparâmetro**.

---

# 38. O que é hiperparâmetro

Hiperparâmetro é uma configuração definida antes/do lado de fora do processo de treinamento.

Exemplos:

- `k` no k-NN;
- `max_depth` em árvore;
- `C` e `gamma` no SVM;
- `alpha` em Ridge/Lasso.

Eles influenciam o comportamento do modelo.

---

# 39. Overfitting e Underfitting

## Overfitting

O modelo aprende demais os detalhes do treino.

Resultado:

- excelente no treino;
- pior em dados novos.

Exemplos:

- árvore muito profunda;
- k-NN com k muito pequeno.

---

## Underfitting

O modelo é simples demais e não aprende adequadamente.

Resultado:

- ruim no treino;
- ruim no teste.

Exemplo:

- k muito grande no k-NN;
- árvore excessivamente podada.

---

# 40. Questões com alta chance de aparecer em prova escrita

## Questão 1

**Qual a diferença entre Transformer e Predictor?**

Resposta:

> Transformer prepara ou modifica os dados de entrada, enquanto Predictor utiliza os dados para aprender um padrão e realizar previsões.

---

## Questão 2

**Por que fazer split entre treino e teste?**

Resposta:

> Para treinar o modelo em uma parte dos dados e avaliar sua capacidade de generalização em dados não vistos durante o treinamento.

---

## Questão 3

**O que é data leakage?**

Resposta:

> É quando informações do conjunto de teste influenciam o treinamento ou pré-processamento, causando uma avaliação artificialmente otimista.

---

## Questão 4

**Por que fazemos fit_transform no treino e somente transform no teste?**

Resposta:

> Porque os parâmetros da transformação devem ser aprendidos somente no conjunto de treino. O teste deve apenas receber a transformação já aprendida para evitar vazamento de dados.

---

## Questão 5

**Por que o k-NN precisa de dados escalonados?**

Resposta:

> Porque ele utiliza distância entre pontos. Atributos com escalas maiores poderiam dominar o cálculo da distância.

---

## Questão 6

**Por que k muito pequeno pode causar overfitting?**

Resposta:

> Porque o modelo passa a depender demais de exemplos individuais e ruídos locais, criando fronteiras muito irregulares.

---

## Questão 7

**Por que k muito grande pode causar underfitting?**

Resposta:

> Porque muitos vizinhos suavizam demais a fronteira de decisão e o modelo perde detalhes importantes das classes.

---

## Questão 8

**Por que árvores de decisão não precisam de escalonamento?**

Resposta:

> Porque elas tomam decisões por regras e limiares sobre os atributos, e não por cálculo de distância.

---

## Questão 9

**O que é max_depth?**

Resposta:

> É o limite máximo de profundidade de uma árvore de decisão. Ele ajuda a evitar árvores excessivamente complexas e overfitting.

---

## Questão 10

**O que são vetores de suporte no SVM?**

Resposta:

> São os pontos mais próximos da fronteira de decisão e que ajudam a determinar a margem máxima e a posição do hiperplano.

---

## Questão 11

**O que é a matriz de confusão?**

Resposta:

> É uma tabela que compara classes reais e previstas e mostra acertos e tipos de erro do classificador.

---

## Questão 12

**Qual a diferença entre precisão e recall?**

Resposta:

> Precisão mede quantos dos casos previstos como positivos eram realmente positivos. Recall mede quantos dos positivos reais foram encontrados pelo modelo.

---

## Questão 13

**Qual a diferença entre classificação e regressão?**

Resposta:

> Classificação prevê categorias ou classes; regressão prevê valores numéricos contínuos.

---

## Questão 14

**O que significam MAE, MSE e RMSE?**

Resposta:

> São métricas de erro para regressão. MAE calcula o erro absoluto médio, MSE calcula o erro quadrático médio e RMSE é a raiz do MSE.

---

## Questão 15

**O que significa uma base desbalanceada?**

Resposta:

> Significa que uma classe possui significativamente mais exemplos que outra, podendo influenciar o aprendizado do modelo.

---

## Questão 16

**Qual a diferença entre undersampling e oversampling?**

Resposta:

> Undersampling reduz a classe majoritária; oversampling aumenta a classe minoritária.

---

## Questão 17

**O que é EDA?**

Resposta:

> É a análise exploratória dos dados realizada antes do treinamento para entender estrutura, distribuição, qualidade, correlações e possíveis problemas do dataset.

---

# 41. Fórmulas que vale decorar

## Distância Euclidiana

```text
d(x,x') = √Σ(xᵢ - x'ᵢ)²
```

## Acurácia

```text
(VP + VN) / (VP + VN + FP + FN)
```

## Precisão

```text
VP / (VP + FP)
```

## Recall

```text
VP / (VP + FN)
```

## F1

```text
2 × (Precisão × Recall) / (Precisão + Recall)
```

## MAE

```text
média de |y - ŷ|
```

## MSE

```text
média de (y - ŷ)²
```

## RMSE

```text
√MSE
```

---

# 42. Macetes finais

```text
Estimator   → aprende
Transformer → prepara
Predictor   → prevê
```

```text
X → características
Y → resposta real
Ŷ → resposta prevista
```

```text
Split → separa
Fit → aprende
Transform → prepara
Predict → prevê
Evaluate → avalia
```

```text
k pequeno → overfitting
k grande → underfitting
```

```text
Árvore → Se/Então
SVM → margem máxima
k-NN → vizinhos
Naive Bayes → probabilidade
Regressão Logística → classificação linear
```

```text
VP + VN → acertos
FP + FN → erros
```

```text
Precisão → dos positivos previstos, quantos estavam certos?
Recall → dos positivos reais, quantos encontrei?
```

```text
Classificação → classe
Regressão → número
```

```text
MAE / MSE / RMSE → quanto menor, melhor
```

---

# 43. O que eu priorizaria na revisão final

Se o tempo estiver curto, foque nesta ordem:

1. **X, y, treino/teste e data leakage**;
2. **Estimator, Transformer e Predictor**;
3. **StandardScaler**;
4. **k-NN + distância euclidiana + valor de k**;
5. **Árvore de decisão + max_depth + overfitting**;
6. **SVM + margem + vetores de suporte**;
7. **Matriz de confusão: VP, VN, FP, FN**;
8. **Acurácia, precisão, recall e F1**;
9. **Classificação x regressão**;
10. **MAE, MSE e RMSE**;
11. **EDA, balanceamento e correlação**;
12. **Undersampling, oversampling e dados sintéticos**.

---

# 44. Resumo em uma página

> **Machine Learning supervisionado:** temos X e y. X são as características e y é a resposta.
>
> **Scikit-Learn:** usa uma interface padronizada. Estimator aprende com `fit`, Transformer prepara com `transform`, Predictor prevê com `predict`.
>
> **Fluxo:** separar treino/teste → pré-processar → treinar → prever → avaliar.
>
> **Data leakage:** teste não pode participar do aprendizado.
>
> **StandardScaler:** média 0, desvio padrão 1.
>
> **Classificação:** prevê classes. **Regressão:** prevê valores numéricos.
>
> **k-NN:** voto dos k vizinhos mais próximos; depende de distância; k pequeno pode overfitar, k grande pode underfitar.
>
> **Árvore:** regras Se/Então; interpretável; não precisa escalonamento; árvore grande pode overfitar.
>
> **SVM:** procura margem máxima; vetores de suporte definem a fronteira.
>
> **Naive Bayes:** trabalha com probabilidades e Teorema de Bayes.
>
> **Matriz de confusão:** VP/VN = acertos; FP/FN = erros.
>
> **Acurácia:** acertos/total. **Precisão:** positivos previstos corretos. **Recall:** positivos reais encontrados. **F1:** equilíbrio entre precisão e recall.
>
> **Regressão:** MAE, MSE, RMSE e R².
>
> **EDA:** entender os dados antes de modelar. Ver distribuição, classes, correlação, nulos e qualidade dos atributos.
>
> **Desbalanceamento:** pode ser tratado com stratify, undersampling, oversampling ou dados sintéticos — sempre cuidando para não vazar informação do teste.

