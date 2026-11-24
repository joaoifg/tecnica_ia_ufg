# Detecção de fraude em documentos de identidade com modelos clássicos de aprendizado de máquina

**Autor:** João Henrique Gomes Dias  
**Curso:** Bacharelado em IA Aplicada à Gestão Pública — UFG / IIG  
**Disciplina:** Técnicas de IA I  
**Dataset:** The FREUID Challenge 2026 – IJCAI-ECAI (Microblink Fraud Lab)

As imagens e os CSVs do dataset não acompanham este texto. A licença da Microblink permite pesquisa não comercial e proíbe redistribuição. Os números abaixo saem dos rótulos e de características numéricas calculadas localmente. Nenhuma imagem de documento é publicada.

## Resumo

Órgãos públicos decidem direitos a partir de documentos de identidade apresentados em cadastros, concursos e conselhos profissionais. Este trabalho trata a verificação como classificação supervisionada: cada exemplo é um par `(x, y)`, em que `x` é um vetor de 73 características da imagem e `y` vale 0 (legítimo) ou 1 (fraude).

O estudo usa os 69.352 rótulos de treino da competição FREUID 2026 e treina os modelos da disciplina em 464 imagens que estão de fato no disco. A validação tem duas perguntas diferentes. Na primeira, o documento já apareceu no treino (validação ID, 76 imagens). Na segunda, um tipo inteiro fica de fora: a carteira de Moçambique (84 imagens).

Nos documentos vistos, o gradient boosting alcançou ROC-AUC 0,978, a Random Forest 0,965 e a regressão logística 0,940, contra 0,500 de um baseline que sempre responde a classe majoritária. No documento nunca visto, os três caem para 0,55, 0,51 e 0,55. A checagem de atalho explica o contraste: as mesmas 73 características identificam o tipo do documento com acurácia 1,00, enquanto largura, altura e tamanho do arquivo não separam fraude de documento legítimo (AUC 0,53). O modelo aprende o visual de cada carteira, não uma regra de fraude que viaje para um país novo.

O resultado serve como triagem auxiliar dentro dos tipos já vistos, com uma pessoa conferindo o caso. Não serve para produção, nem para um tipo de documento ausente do treino. O uso permanece acadêmico e não comercial.

**Palavras-chave:** classificação supervisionada; regressão logística; Random Forest; fraude documental; validação fora da distribuição; gestão pública.

## 1. Introdução

Cadastros públicos concedem benefícios, inscrições e credenciais. Uma fraude aceita entrega um direito a quem não o tem. Uma recusa errada trava um cidadão legítimo. As duas falhas não custam a mesma coisa, e um limiar único de 0,5 não responde à política do órgão.

O professor pediu quatro itens: um dataset ligado à administração pública; a verificação de que existem entradas `X` e rótulos `Y`; a escolha das técnicas de IA e a justificativa; e um artigo que explique o que foi desenvolvido. As respostas, desenvolvidas nas seções seguintes, são estas.

| Item | Resposta |
|---|---|
| Dataset | FREUID 2026, fraude em documentos de identidade, uso de pesquisa |
| Serve para IA? | Sim. `X` é a imagem resumida em 73 números; `Y` é `label` 0/1 |
| Técnicas | Baseline, regressão logística, KNN, Naive Bayes, árvore, Random Forest e gradient boosting |
| O que o código fez | Estudo dos rótulos, características, protocolo único, treino, holdout e checagem de atalho |

O objetivo é estimar a probabilidade de fraude e dizer em que condição essa probabilidade pode orientar uma decisão humana.

## 2. Referencial

### 2.1 Aprendizado supervisionado

Um conjunto supervisionado é `D = {(x_i, y_i)}`. O ajuste (`fit`) usa só o treino. A avaliação usa exemplos que o ajuste não viu. No Scikit-Learn a troca de algoritmo preserva a mesma sequência: separar os dados, pré-processar, treinar, prever, medir.

A regressão logística desenha um hiperplano depois de padronizar as colunas. O coeficiente de cada característica tem sinal e magnitude, o que ajuda a explicar o modelo. A árvore de decisão corta o espaço em regras. A Random Forest junta muitas árvores e reduz a variância de uma árvore só. O KNN classifica pelo voto dos vizinhos. O Naive Bayes trata as características como independentes dado o rótulo, o que aqui é uma aproximação, porque bins de histograma são correlacionados. O gradient boosting (`HistGradientBoosting`) soma árvores pequenas em sequência. O baseline da classe majoritária existe para mostrar o que qualquer modelo precisa ultrapassar: chutar sempre “legítimo” acerta cerca de 56% desta amostra e tem AUC 0,50.

### 2.2 Métricas e custo

A acurácia esconde o tipo de erro. A matriz de confusão separa verdadeiro negativo, falso positivo (legítimo marcado como fraude), falso negativo (fraude aceita) e verdadeiro positivo.

A ROC-AUC resume a ordenação dos escores, sem fixar um limiar. O escore da competição combina essa ordenação com a taxa de fraudes pegas quando só 1% dos legítimos pode ser recusado (TPR a 1% de FPR). O APCER nesse ponto é `1 − TPR`. O escore FREUID vale `1` menos a média harmônica entre a AUC e esse TPR. Quanto menor, melhor. Um modelo que só acerta com muitos alarmes falsos fica com FREUID perto de 1, mesmo com AUC moderada.

Para a decisão do órgão, o limiar minimiza `5·FN + 1·FP`. Deixar uma fraude passar custa cinco vezes mandar um legítimo para conferência. O limiar é escolhido nas previsões out-of-fold do treino, antes de olhar a validação e o documento deixado de fora.

### 2.3 Generalização e atalho

Um modelo pode ir bem no sorteio aleatório e falhar num documento de outro país. Por isso o protocolo guarda um tipo inteiro como teste fora da distribuição (OOD) e ainda repete o experimento deixando cada um dos cinco tipos de fora (leave-one-type-out).

Também se mede o atalho. Se largura, altura ou tamanho do arquivo já separam as classes, o modelo não está olhando a fraude. Se as características adivinham o país do documento e não a fraude, o número alto no teste aleatório descreve o template da carteira, não um detector portátil.

## 3. Materiais e métodos

### 3.1 Dataset

A competição é sintética: não há pessoa real nem documento oficial verdadeiro. O treino rotulado tem 69.352 linhas, sem identificador duplicado e sem valor ausente. As colunas usadas são `id`, `image_path`, `label`, `is_digital` e `type`.

| Classe | n | % |
|---|---:|---:|
| Legítimo (`label = 0`) | 40.005 | 57,7 |
| Fraude (`label = 1`) | 29.347 | 42,3 |

Cinco tipos aparecem no treino. Egito concentra mais fraude (49,6%) do que Benin, Guiné, Maurício e Moçambique (cerca de 40,1% a 40,2% cada). O qui-quadrado é significativo (`χ² = 444,9`, 4 graus de liberdade, `p` da ordem de `10⁻⁹⁴`), mas a associação é fraca: V de Cramer = 0,080. O país muda pouco a taxa de fraude.

Quase tudo é digital. Só 20 imagens são recaptura (`is_digital = 0`), 14 delas fraude. O teste exato de Fisher dá razão de chances 0,31 e `p = 0,021`, com intervalo largo. Vinte casos não sustentam um detector de recaptura.

### 3.2 Amostra que entrou no treino

O arquivo completo tem dezenas de gigabytes. No disco deste trabalho há 464 JPEGs não vazios, todos presentes no manifesto e todos digitais. Isso é 0,67% da população rotulada. A taxa de fraude da amostra é 43,5%, perto dos 42,3% da população. A participação de cada país também fica próxima: Egito 26,3% na amostra contra 22,9% na população; os outros quatro ficam entre 17% e 20%.

| Tipo | n | fraudes |
|---|---:|---:|
| Egito / DL | 122 | 64 |
| Benin / DL | 92 | 39 |
| Guiné / DL | 85 | 32 |
| Moçambique / DL | 84 | 33 |
| Maurício / ID | 81 | 34 |
| Total | 464 | 202 |

Não há recaptura nessa amostra. Conclusões sobre *print-and-capture* ficam fora do alcance do treino.

### 3.3 Características

Cada imagem vira 73 números, em duas famílias.

O bloco V1 tem 64 características: histograma de 16 bins em R, G e B, média, desvio, mínimo e máximo de cada canal, e brilho e gradiente da luminância. A imagem entra redimensionada para 128×128.

O bloco de perícia acrescenta 9 características, calculadas para aproximar o que um perito olha sem deep learning: média, desvio e percentil 99 do Error Level Analysis (recompressão JPEG de um recorte central), variância do laplaciano, energia fora do centro do espectro, densidade de bordas, entropia do cinza e média e desvio da saturação.

Largura, altura e tamanho em KB entram só na checagem de atalho. Não entram no vetor dos classificadores.

No estudo univariado da amostra, 10 características passam o limiar de Bonferroni. A mais forte é o primeiro bin do histograma verde (`hist_G_00`, AUC 0,749, d de Cohen 0,70). Em seguida vêm bins escuros de azul e vermelho e o desvio da saturação. Trinta pares de características têm correlação acima de 0,90, em 2.628 pares possíveis: há redundância, e modelos lineares precisam de regularização.

A PCA precisa de 9 componentes para 90% da variância e de 14 para 95%. A silhueta por classe (fraude contra legítimo) é 0,014. A silhueta por tipo de documento é 0,484. No plano dos dois primeiros componentes, os países se separam e as classes se misturam.

Largura, altura e tamanho não diferem entre fraude e legítimo (Mann–Whitney, `p` de 0,62, 0,43 e 0,86). A AUC univariada desses três metadados fica entre 0,48 e 0,50.

### 3.4 Protocolo

O universo é a interseção do manifesto com os 464 JPEGs. A semente é 42.

1. Moçambique/DL inteiro vai para o teste OOD (84 imagens, 33 fraudes). Esse corte foi definido antes de olhar o resultado.
2. Dos outros quatro tipos, 20% formam a validação ID, estratificada pelo rótulo (76 imagens, 34 fraudes). O resto é treino (304 imagens, 135 fraudes, 169 legítimos).
3. Nenhum `id` aparece em dois splits. Os identificadores ficam fora do git; o relatório guarda só contagens e um hash.

A validação cruzada, a comparação de características, as curvas de hiperparâmetro e a curva de aprendizado usam somente as 304 imagens de treino. O leave-one-type-out usa as 464, porque precisa dos cinco tipos, e é lido à parte. O holdout final treina nas 304 e avalia nos dois testes.

### 3.5 Modelos

| Modelo | Ajuste usado no comparativo |
|---|---|
| Baseline | Classe majoritária |
| Regressão logística | Padronização, `class_weight=balanced`, `max_iter=5000` |
| KNN | Padronização, 15 vizinhos, peso pela distância |
| Naive Bayes | Gaussiano, depois da padronização |
| Árvore | Profundidade 8, folha mínima 5, classes balanceadas |
| Random Forest | 400 árvores, folha mínima 2, classes balanceadas |
| Gradient boosting | 300 iterações, taxa 0,05, classes balanceadas |

A curva de validação percorre `C` da logística, `k` do KNN e a profundidade da árvore, com 5 folds no treino. A Random Forest passa por uma grade de 18 combinações (`max_depth` em {6, 12, sem limite}, `min_samples_leaf` em {1, 3, 8}, `max_features` em {sqrt, 0,5}), com leave-one-group-out nos quatro tipos do treino. Essa grade não vê Moçambique.

O código está em `freuid-trabalho/src/`. O estudo exploratório é `eda_completa.py`. O treino e as figuras são `modelagem.py`. Os números brutos estão em `reports/analise/modelagem.json`.

## 4. Resultados

### 4.1 Validação cruzada no treino

Cinco folds estratificados, 304 imagens, 73 características.

| Modelo | ROC-AUC | Acurácia | F1 | Acurácia balanceada |
|---|---:|---:|---:|---:|
| Baseline | 0,500 ± 0,000 | 0,556 | 0,000 | 0,500 |
| KNN | 0,829 ± 0,046 | 0,793 | 0,708 | 0,770 |
| Naive Bayes | 0,875 ± 0,032 | 0,783 | 0,741 | 0,775 |
| Árvore de decisão | 0,888 ± 0,027 | 0,839 | 0,826 | 0,840 |
| Regressão logística | 0,913 ± 0,014 | 0,849 | 0,821 | 0,842 |
| Random Forest | 0,951 ± 0,024 | 0,882 | 0,851 | 0,870 |
| Gradient boosting | 0,956 ± 0,019 | 0,878 | 0,851 | 0,869 |

Todos os modelos da disciplina passam o baseline. A logística é a mais estável entre os modelos lineares (desvio 0,014). Floresta e boosting lideram a ordenação. O F1 do baseline é zero porque ele nunca prevê fraude.

Entre logística e floresta, a floresta tem a maior AUC de validação cruzada. As figuras de matriz, limiar e importância usam esse modelo. O boosting entra na mesma tabela porque o código o treinou no mesmo protocolo; ele não substitui os dois modelos centrais da disciplina.

### 4.2 O que as nove características de perícia acrescentam

A mesma validação cruzada, no mesmo treino, compara o bloco V1 (64) com o vetor completo (73).

| Modelo | AUC V1 | AUC completo |
|---|---:|---:|
| Regressão logística | 0,876 ± 0,035 | 0,913 ± 0,014 |
| Random Forest | 0,894 ± 0,020 | 0,951 ± 0,024 |
| Gradient boosting | 0,900 ± 0,027 | 0,956 ± 0,019 |

ELA, nitidez, frequência e saturação sobem a AUC em cerca de 0,04 a 0,06 e, na logística, também reduzem o desvio. O histograma sozinho já separa parte dos casos. A perícia não é enfeite.

### 4.3 Documento deixado de fora

Média das cinco rodadas em que um tipo inteiro é o teste:

| Modelo | AUC média | FREUID médio |
|---|---:|---:|
| Baseline | 0,500 | 1,000 |
| Árvore de decisão | 0,617 | 0,771 |
| Naive Bayes | 0,683 | 0,766 |
| Regressão logística | 0,714 | 0,639 |
| Gradient boosting | 0,752 | 0,530 |
| KNN | 0,765 | 0,762 |
| Random Forest | 0,783 | 0,357 |

A média esconde tipos fáceis e tipos difíceis. AUC da Random Forest em cada documento deixado de fora:

| Tipo deixado de fora | Logística | Random Forest | Boosting |
|---|---:|---:|---:|
| Benin | 0,672 | 0,638 | 0,724 |
| Egito | 0,843 | 0,788 | 0,742 |
| Guiné | 0,863 | 0,952 | 0,785 |
| Maurício | 0,644 | 0,981 | 0,925 |
| Moçambique | 0,548 | 0,556 | 0,583 |

Guiné e Maurício transferem. Benin transfere pouco. Moçambique fica no acaso para todos os modelos. A escolha prévia de Moçambique como OOD oficial caiu no pior caso, não num caso médio.

### 4.4 Hiperparâmetros e curva de aprendizado

No treino, o melhor `C` da logística ficou em 0,72 (AUC de validação 0,912). O melhor `k` foi 5 (AUC 0,863), abaixo dos 15 vizinhos do comparativo principal: com 304 linhas, uma vizinhança menor ordena melhor. A árvore prefere profundidade 4 (AUC 0,919), mais rasa que o 8 usado na tabela geral. A grade da floresta, avaliada deixando um dos quatro tipos de treino de fora, escolheu profundidade livre, metade das características por divisão e folha mínima 1, com AUC 0,845. Esse 0,845 não é o teste de Moçambique.

A curva de aprendizado, ainda só no treino, sobe até o fim da amostra:

| Imagens de treino | AUC logística | AUC floresta | AUC boosting |
|---|---:|---:|---:|
| 24 | 0,715 | 0,705 | 0,500 |
| 118 | 0,873 | 0,925 | 0,894 |
| 243 | 0,913 | 0,949 | 0,955 |

A floresta memoriza o treino (AUC de treino 1,00 em todos os tamanhos) e mesmo assim a validação continua subindo. Mais imagens dos mesmos tipos devem melhorar o número interno. Isso não corrige, por si, o fracasso em Moçambique: o problema ali é o template novo, não só o tamanho.

### 4.5 Holdout final

Treino nas 304 imagens. Limiar de custo escolhido fora do teste.

Validação ID, tipos vistos, n = 76 (34 fraudes):

| Modelo | AUC | AP | FREUID | APCER a 1% | Limiar | VN | FP | FN | VP | Custo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 0,500 | 0,447 | 1,000 | 1,000 | 0,50 | 42 | 0 | 34 | 0 | 170 |
| Naive Bayes | 0,900 | 0,910 | 0,209 | 0,294 | 0,02 | 29 | 13 | 5 | 29 | 38 |
| KNN | 0,901 | 0,916 | 0,247 | 0,353 | 0,12 | 7 | 35 | 0 | 34 | 35 |
| Regressão logística | 0,940 | 0,949 | 0,122 | 0,176 | 0,12 | 16 | 26 | 1 | 33 | 31 |
| Árvore de decisão | 0,965 | 0,964 | 0,062 | 0,088 | 0,02 | 37 | 5 | 2 | 32 | 15 |
| Random Forest | 0,965 | 0,967 | 0,129 | 0,206 | 0,19 | 22 | 20 | 0 | 34 | 20 |
| Gradient boosting | 0,978 | 0,975 | 0,124 | 0,206 | 0,02 | 33 | 9 | 0 | 34 | 9 |

No ponto de operação, o boosting zera os falsos negativos e manda 9 legítimos para conferência (custo 9). A logística deixa passar 1 fraude e marca 26 legítimos (custo 31). A árvore tem o melhor FREUID (0,062): é a que ainda pega fraude quando quase não se pode recusar legítimo. Com 76 casos, a ordem fina entre árvore, floresta e boosting não deve ser lida como ranking estável. Os três estão no mesmo patamar, longe do baseline.

OOD, Moçambique, n = 84 (33 fraudes):

| Modelo | AUC | AP | FREUID | APCER a 1% | VN | FP | FN | VP | Custo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 0,500 | 0,393 | 1,000 | 1,000 | 51 | 0 | 33 | 0 | 165 |
| Random Forest | 0,510 | 0,385 | 1,000 | 1,000 | 0 | 51 | 0 | 33 | 51 |
| KNN | 0,540 | 0,406 | 1,000 | 1,000 | 0 | 51 | 0 | 33 | 51 |
| Gradient boosting | 0,547 | 0,421 | 1,000 | 1,000 | 0 | 51 | 0 | 33 | 51 |
| Regressão logística | 0,550 | 0,471 | 0,943 | 0,970 | 11 | 40 | 2 | 31 | 50 |
| Naive Bayes | 0,562 | 0,423 | 1,000 | 1,000 | 12 | 39 | 2 | 31 | 49 |
| Árvore de decisão | 0,500 | 0,393 | 1,000 | 1,000 | 0 | 51 | 0 | 33 | 51 |

No documento novo a ordenação desaparece. O limiar herdado do treino faz a floresta, o boosting, o KNN e a árvore classificarem as 84 imagens como fraude. O custo cai de 165 para cerca de 50 só porque nenhuma fraude passa — e nenhum legítimo passa também. Isso não é triagem. É recusar o país inteiro.

### 4.6 Importância e atalhos

Na validação ID, a permutação que mais derruba a AUC da floresta está nos bins escuros dos histogramas (`hist_G_00` 0,017, `hist_B_00` 0,015, `hist_R_00` 0,010) e no desvio da saturação e no desvio do ELA (0,010 e 0,008). Somadas por família, perícia e histograma verde lideram. Nenhuma característica sozinha carrega o modelo: a queda de cada uma é pequena, como se espera com 73 colunas correlacionadas.

A checagem de atalho, no mesmo protocolo:

| Teste | Resultado |
|---|---|
| Identificadores repetidos entre splits | 0 |
| AUC usando só largura, altura e tamanho | 0,532 na validação ID; 0,567 no OOD |
| AUC usando só o tipo do documento, na validação ID | 0,487 |
| Acurácia ao prever o tipo a partir das 73 características | 1,00 (chute do tipo mais comum: 0,26) |
| Algum holdout com AUC acima de 0,98 | Não |

Não houve vazamento de identificador. Metadado de arquivo não resolve a fraude. O tipo, sozinho, também não: dentro dos países vistos, saber o país não diz se o documento é falso. As 73 características, porém, acertam o país em todas as imagens. O vetor é uma impressão digital do template. A AUC alta no teste aleatório convive com esse fato. A AUC de 0,51 em Moçambique é a consequência.

Nenhum holdout passou de 0,98. O 0,978 do boosting na validação ID é alto para 76 imagens e deve ser lido junto com o desvio da validação cruzada (0,019) e com o colapso OOD.

## 5. Discussão

O dataset serve para a disciplina. Existe `X`, existe `Y`, e os algoritmos da aula produzem uma probabilidade que, nos tipos vistos, ordena fraude acima de legítimo. A regressão logística já entrega AUC 0,94 na validação ID e permanece interpretável. A floresta e o boosting ganham alguns pontos de AUC e, no limiar de custo, zeram o falso negativo dessa amostra pequena.

O mesmo experimento mostra o limite. Um órgão que cadastra um tipo de documento ausente do treino não pode reutilizar o escore. Em Moçambique o modelo não ordena: acusa todo mundo ou, se o limiar for relaxado até o ponto da competição (1% de recusa de legítimos), quase não pega fraude (APCER entre 0,97 e 1,00). A média do leave-one-type-out (AUC 0,78 na floresta) não autoriza o uso geral. Ela é a mistura de Guiné e Maurício, que transferem, com Benin e Moçambique, que não transferem.

Para a gestão pública, o desenho honesto é este. O escore ordena uma fila de conferência humana apenas para tipos presentes no treino. O limiar sai da política de custo, não de 0,5. Um tipo novo exige amostra rotulada nova e um teste OOD antes de qualquer uso. O modelo não substitui o servidor que olha o documento.

Limitações que mudam a leitura do número:

- 464 imagens, 0,67% do treino rotulado, todas digitais. Recaptura, que é um dos três ataques da competição, não foi aprendida.
- Cinco países apenas, e o ataque é sintético. O comportamento em documento brasileiro real não foi medido.
- As características são globais. Uma edição pequena pode se perder no histograma, e o histograma também é o que identifica o país.
- A validação ID tem 76 imagens. Diferenças de 0,01 na AUC entre árvore, floresta e boosting cabem no acaso.
- A CNN com EfficientNet está escrita para o ambiente com GPU da competição e não foi executada aqui. Os números deste artigo são só dos modelos clássicos.

A licença fecha o resto. Pesquisa não comercial, citação obrigatória, sem republicar imagens, sem levar o modelo a produto. Apagar os arquivos ao fim do trabalho faz parte da condição de uso.

## 6. Conclusão

Fraude documental, neste dataset, é um problema supervisionado bem formado. No recorte local, regressão logística, árvore, Random Forest e gradient boosting separam fraude de documento legítimo quando o tipo da carteira já apareceu no treino. A melhor operação nesse recorte, pelo custo `5·FN + 1·FP`, foi o gradient boosting: AUC 0,978, nenhuma fraude perdida e nove legítimos encaminhados à revisão, em 76 imagens.

Esse desempenho não se sustenta fora dos tipos vistos. Com Moçambique inteiramente de fora, a AUC volta para cerca de 0,55 e o escore da competição desaba. As características identificam o modelo do documento com acurácia perfeita e quase não usam o tamanho do arquivo. O classificador aprendeu aparência de carteira junto com o sinal de fraude.

O trabalho entrega o que a disciplina pediu: dataset justificado, formulação `D = {(x, y)}`, técnicas da aula comparadas contra um baseline, e o relato do que o código mediu, inclusive o resultado negativo. O uso proposto é apoio à decisão humana, restrito aos tipos treinados, sob a licença acadêmica da Microblink.

## Referências

1. Relić, I. et al. *The FREUID Challenge 2026 - IJCAI-ECAI.* Kaggle, 2026. https://www.kaggle.com/competitions/the-freuid-challenge-2026-ijcai-ecai
2. Microblink Fraud Lab, Microblink LLC. Dataset FREUID, licença de pesquisa não comercial.
3. Brasil. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais.
4. Pedregosa, F. et al. Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, v. 12, p. 2825–2830, 2011.
5. UFG/IIG. Materiais de Técnicas de IA I. Fluxo supervisionado, regressão logística, árvores, Random Forest, métricas e matriz de confusão.

## Anexo — onde está cada peça

| Peça | Caminho |
|---|---|
| Estudo dos 69.352 rótulos e da amostra | `reports/analise/eda.json`, `reports/figs/eda_*.png` |
| Inventário dos 464 arquivos | `reports/analise/inventario.json` |
| Treino, holdout e atalhos | `reports/analise/modelagem.json` |
| Importância por permutação | `reports/analise/importancia_permutacao.csv` |
| Figuras do treino | `reports/figs/mod_*.png` |
| Protocolo de split | `src/protocolo.py` |
| Características | `src/features.py` |
| Modelos | `src/modelagem.py` |
| Previsões com identificadores | só em `C:\freuid\data`, fora do git |
