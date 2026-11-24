# Fraude em documentos de identidade: o escore de um modelo vale para um tipo de documento novo?

**Autor:** João Henrique Gomes Dias
**Curso:** Bacharelado em IA Aplicada à Gestão Pública, UFG / IIG
**Disciplina:** Técnicas de IA I, prof. Paulo Victor dos Santos, 2026/2
**Dataset:** The FREUID Challenge 2026, IJCAI-ECAI. Dataset FREUID fornecido pelo Microblink Fraud Lab (Microblink LLC), licença de pesquisa não comercial.

As imagens e os CSVs do dataset não acompanham este texto. Nenhuma fotografia de documento, recorte ou mapa de calor sobre foto aparece aqui. Cada número traz entre colchetes o arquivo JSON de onde saiu, todos em `freuid-trabalho/reports/analise/`.

## Resumo

Órgãos públicos concedem benefícios, inscrições em conselho e posse em concurso a partir de documentos de identidade enviados por imagem. A pergunta deste trabalho é se um órgão consegue estimar P(fraude) a partir da imagem com os modelos vistos na disciplina, e se esse escore continua valendo quando o tipo de documento é novo.

O problema é tratado como classificação supervisionada `D = {(x, y)}`: `x` é a imagem resumida em 73 números (ou, na rede neural, a própria imagem), e `y = 1` indica fraude. Foram usadas 24.998 imagens da competição FREUID 2026, de cinco tipos de documento [inventario.json]. A carteira de motorista de Moçambique inteira fica fora do treino e serve de teste fora da distribuição (OOD, 4.816 imagens). Dos outros quatro tipos, 80% treinam (16.145) e 20% formam a validação dentro da distribuição (ID, 4.037) [modelagem.json].

Nos tipos vistos, a regressão logística alcança ROC-AUC 0,968 e a Random Forest 0,991, contra 0,500 do baseline [modelagem.json]. No tipo novo, as mesmas duas caem para 0,669 e 0,584, e o escore oficial da competição (FREUID, menor é melhor) sobe de 0,109 e 0,042 para 0,892 e 0,867 [modelagem.json]. A checagem de atalho explica o contraste. Não há identificador repetido entre os splits, e metadados de arquivo não separam as classes (AUC 0,55), mas as 73 características identificam o tipo do documento com acurácia de 0,9999 [modelagem.json]. O modelo aprende a fraude *dentro* de cada carteira. Esse aprendizado não se transfere para uma carteira que ele nunca viu. A EfficientNet-B0, no mesmo split, chega a AUC 0,9999 nos tipos vistos e 0,797 no tipo novo [cnn.json]. Ela ordena melhor que os clássicos no OOD (diferença de 0,127 sobre a logística, IC 95% de 0,112 a 0,143) [cnn_diagnostico.json], mas seu escore se desloca: 94% dos legítimos de Moçambique recebem P(fraude) acima de 0,5 [cnn_diagnostico.json], e o limiar escolhido nos tipos vistos manda todas as imagens para conferência.

A conclusão para a gestão pública é que o escore pode ordenar uma fila de conferência humana nos tipos de documento presentes no treino, com limiar definido pelo custo do erro. Para um tipo novo, ele não deve ser usado sem nova amostra rotulada e novo teste.

**Palavras-chave:** classificação supervisionada; regressão logística; Random Forest; transferência de aprendizado; validação fora da distribuição; fraude documental; gestão pública.

## 1. Introdução

Boa parte do acesso a direitos no setor público passa por um documento de identidade enviado como imagem. É assim no cadastro de um benefício social, na inscrição em um conselho profissional e na posse de um aprovado em concurso. Um documento falso aceito entrega um direito a quem não o tem e abre caminho para fraude em série. Um documento verdadeiro recusado trava um cidadão legítimo e gera recurso, atraso e custo de atendimento.

Os dois erros não custam o mesmo. Por isso, a pergunta útil para um órgão não é só se o modelo acerta, mas também quanto custa errar para cada lado e se o modelo continua acertando no documento que chega amanhã. Esta segunda parte é o centro do trabalho. Um órgão federal recebe carteiras de 27 unidades da federação, de várias gerações e de vários emissores. Um modelo que só funciona nos modelos de carteira que já viu tem uso limitado.

A competição FREUID 2026, organizada pelo Microblink Fraud Lab, oferece imagens sintéticas de documentos legítimos e fraudados de cinco tipos, com rótulo binário. O teste privado da competição inclui tipos de documento que não aparecem no treino, o que torna a pergunta deste trabalho a mesma pergunta da competição. Aqui o objetivo não é o leaderboard, e nenhuma submissão foi feita. O objetivo é medir, com os modelos da disciplina e um protocolo honesto, o que o escore permite afirmar.

O professor pediu quatro itens: um dataset ligado à administração pública, a verificação de que há entradas `X` e rótulos `Y`, as técnicas de IA com justificativa, e um artigo que explique o que foi feito. A resposta curta é: FREUID 2026; sim, `X` é a imagem e `Y` é `label`; regressão logística e Random Forest como núcleo, com os demais modelos da aula e uma rede convolucional como contraste; e este texto.

## 2. Referencial

**Aprendizado supervisionado.** O fluxo da aula se repete para todos os modelos: transformar cada imagem em um vetor `X`, separar treino e teste, ajustar com `fit` só no treino, prever com `predict_proba` no teste e medir. A matriz de confusão separa verdadeiro negativo (VN), falso positivo (FP, legítimo marcado como fraude), falso negativo (FN, fraude aceita) e verdadeiro positivo (VP).

**Regressão logística.** Modela `P(y = 1 | x) = σ(w·x + b)`. Ela é sensível à escala: uma coluna medida em milhares domina o gradiente e a regularização penaliza os coeficientes de forma desigual. Por isso as colunas são padronizadas (média 0, desvio 1) dentro de um `Pipeline`, com a média e o desvio calculados só no treino. O coeficiente de cada característica tem sinal e tamanho, o que ajuda a explicar o modelo.

**Árvore e Random Forest.** A árvore divide o espaço com perguntas do tipo "esta coluna é maior que um valor?". Como cada divisão olha uma coluna de cada vez, multiplicar uma coluna por uma constante não muda nenhuma divisão, e padronizar não é necessário. A Random Forest treina centenas de árvores em amostras e subconjuntos de colunas diferentes e tira a média, o que reduz a variância de uma árvore isolada. KNN (voto dos vizinhos, depende de distância e portanto de padronização), Naive Bayes gaussiano e gradient boosting completam a comparação. O boosting entra como contraste e não substitui o núcleo da disciplina.

**Transferência de aprendizado.** Uma rede convolucional pré-treinada no ImageNet já sabe detectar bordas, texturas e formas. O ajuste fino reaproveita esses filtros e treina a rede para a nova tarefa com muito menos dados do que um treino do zero. Aqui foi usada a EfficientNet-B0.

**APCER, BPCER e o escore FREUID.** Na norma ISO/IEC 30107-3, APCER é a fração de ataques (fraudes) aceitos e BPCER é a fração de apresentações legítimas recusadas. A competição mede o APCER no ponto em que só 1% dos legítimos é recusado (APCER@1%BPCER), e também a AuDET, a área sob a curva DET, aproximada por `1 − ROC-AUC`. O escore FREUID é `1 − média harmônica(AUC, 1 − APCER@1%BPCER)`, e quanto menor, melhor. Um modelo que só pega fraude recusando muitos legítimos fica com FREUID perto de 1 mesmo com AUC razoável.

## 3. Materiais

**População rotulada.** O treino da competição tem 69.352 imagens rotuladas, sem identificador duplicado e sem valor ausente [eda.json]. São 40.005 legítimas (57,7%) e 29.347 fraudes (42,3%) [eda.json]. Os cinco tipos são as carteiras de motorista de Benin, Egito, Guiné e Moçambique e a identidade de Maurício. Egito tem mais fraude (49,6%, intervalo de Wilson de 95% entre 48,8% e 50,4%) do que os outros quatro (40,1% a 40,2%) [eda.json]. A diferença é estatisticamente significativa (qui-quadrado 444,9 com 4 graus de liberdade), mas a associação é fraca (V de Cramér 0,080) [eda.json]. Quase tudo é imagem digital: só 20 são recaptura (impressão fotografada), 14 delas fraude, com taxa de 0,70 e intervalo de Wilson de 0,48 a 0,85 [eda.json]. Vinte casos não sustentam conclusão sobre recaptura.

**Universo usado.** O manifesto local (`amostra.csv`) lista 24.998 imagens, todas presentes no disco e com tamanho maior que zero, o que corresponde a 36,0% da população [inventario.json]. A amostra reproduz a população: a maior diferença de proporção entre universo e população, considerando rótulo, tipo e recaptura, é de 0,05 ponto percentual [inventario.json]. A taxa de fraude é 42,3% nos dois conjuntos [inventario.json]. As 20 imagens recapturadas estão no universo [inventario.json].

**Características.** Cada imagem vira 73 números [modelagem.json]. O bloco V1 (64) tem histograma de 16 faixas em cada canal R, G e B, média, desvio, mínimo e máximo de cada canal, e brilho e gradiente da luminância, com a imagem reduzida a 128×128. O bloco de perícia (9) aproxima o que um perito olha: média, desvio e percentil 99 do Error Level Analysis (diferença ao recomprimir um recorte central em JPEG), variância do laplaciano (nitidez), energia de alta frequência, densidade de bordas, entropia do cinza e média e desvio da saturação. Largura, altura e tamanho do arquivo não entram no vetor; são usados só para procurar atalhos.

## 4. Métodos

**Protocolo único.** Clássicos e CNN usam exatamente os mesmos identificadores, definidos em `src/protocolo.py` com semente 42:

1. Moçambique/DL inteiro vai para o teste OOD: 4.816 imagens, 1.933 fraudes [modelagem.json]. O corte foi fixado antes de qualquer resultado, para comparar com o experimento anterior.
2. Dos outros quatro tipos, 20% estratificados pelo rótulo formam a validação ID (4.037 imagens, 1.730 fraudes) e 80% o treino (16.145, 6.919 fraudes) [modelagem.json].
3. Nenhum identificador aparece em dois splits [modelagem.json]. Os ids ficam fora do git. Os JSON guardam contagens e um hash de cada split (treino `850957fbd3c9c7ec`, validação ID `4cb990bdc3b272dc`, OOD `580593bf35d8daeb`) [modelagem.json], e o JSON da CNN repete os mesmos hashes [cnn.json].

**Experimentos com os modelos clássicos** (`src/modelagem.py`). Validação cruzada estratificada em 5 dobras dentro do treino; V1 contra as 73 características; leave-one-type-out (cada tipo vira, uma vez, o documento nunca visto, usando o universo inteiro); curvas de validação de hiperparâmetros e busca em grade da Random Forest com um tipo de fora; curva de aprendizado; importância por permutação; calibração; limiar por custo; e erros por tipo. O holdout final treina nas 16.145 imagens de treino e avalia na validação ID e no OOD.

**Limiar por custo.** Deixar uma fraude passar custa 5 e mandar um legítimo para conferência custa 1. O limiar minimiza `5·FN + 1·FP` em uma grade de 0,02 a 0,98. Nos clássicos, ele é escolhido com previsões out-of-fold dentro do próprio treino, sem olhar a validação nem o OOD [modelagem.json]. O limiar 0,5 também é reportado.

**CNN** (`src/cnn_protocolo.py`). EfficientNet-B0 pré-treinada no ImageNet, entrada de 384×608 (proporção de um cartão ID-1), AdamW, OneCycle, precisão mista, batch de 16 e aumento de dados que imita recaptura (perspectiva, rotação, variação de cor, desfoque, recompressão JPEG e ruído). Até 10 épocas, com early stopping pela ROC-AUC da validação ID (paciência de 3). Como a validação ID também escolhe a época, o limiar de custo da CNN é escolhido nela, e os números ID da CNN no limiar de custo são otimistas; os OOD não são afetados [cnn.json]. Pesos, previsões e log ficam em `C:\freuid\runs\ood_efficientnet_b0\`, fora do repositório.

**Métricas.** Sempre com `y = 1` sendo fraude: ROC-AUC, AuDET, APCER@1%BPCER, FREUID, matriz de confusão, F1 e recall de fraude.

**Regra contra números altos demais.** Se a AUC passar de 0,98, o resultado só é aceito depois de procurar vazamento de identificador, atalho por metadado de arquivo e características que codificam o tipo do documento (Seção 5.5).

## 5. Resultados

### 5.1 Exploração

No espaço das 73 características, a análise de componentes principais precisa de 10 componentes para explicar 90% da variância [eda.json]. A silhueta calculada pelo rótulo é 0,017, e pelo tipo de documento é 0,477 [eda.json]. No gráfico dos dois primeiros componentes (`reports/figs/eda_pca.png`), os cinco países formam nuvens separadas, e fraude e legítimo se misturam dentro de cada nuvem. Das 73 características, 57 passam no teste univariado com correção de Bonferroni [eda.json]. A mais forte isoladamente é a faixa mais escura do histograma verde (`hist_G_00`, AUC univariada 0,767) [eda.json]. Largura, altura e tamanho têm AUC univariada entre 0,48 e 0,50 [eda.json].

### 5.2 Validação cruzada no treino

Cinco dobras, 16.145 imagens [modelagem.json]:

| Modelo | ROC-AUC | Acurácia | Recall de fraude | F1 |
|---|---:|---:|---:|---:|
| Baseline (classe majoritária) | 0,500 | 0,571 | 0,000 | 0,000 |
| Naive Bayes | 0,878 | 0,822 | 0,727 | 0,778 |
| Regressão logística | 0,964 | 0,919 | 0,855 | 0,901 |
| KNN | 0,973 | 0,922 | 0,826 | 0,901 |
| Árvore de decisão | 0,979 | 0,953 | 0,909 | 0,944 |
| Random Forest | 0,991 | 0,964 | 0,921 | 0,957 |
| Gradient boosting | 0,993 | 0,965 | 0,930 | 0,958 |

O desvio entre dobras é de no máximo 0,004 na AUC [modelagem.json]. Com 16 mil imagens a estimativa é estável. As nove características de perícia acrescentam informação: a AUC sobe de 0,930 para 0,964 na logística e de 0,957 para 0,991 na Random Forest quando se passa de V1 para as 73 [modelagem.json]. A curva de aprendizado da Random Forest começa em 0,985 com 1.291 imagens e chega a 0,991 com 12.916 [modelagem.json]: mais imagens dos mesmos tipos já quase não mudam o número interno. A Random Forest tem AUC de treino 1,00 em todos os tamanhos, ou seja, memoriza o treino, e ainda assim a validação se mantém [modelagem.json].

### 5.3 Um tipo de documento de fora de cada vez

AUC de cada modelo quando o tipo da coluna fica inteiramente fora do treino [modelagem.json]:

| Modelo | Benin | Egito | Guiné | Maurício | Moçambique | Média |
|---|---:|---:|---:|---:|---:|---:|
| Regressão logística | 0,500 | 0,859 | 0,496 | 0,635 | 0,670 | 0,632 |
| KNN | 0,500 | 0,674 | 0,821 | 0,738 | 0,595 | 0,665 |
| Naive Bayes | 0,724 | 0,815 | 0,859 | 0,635 | 0,535 | 0,714 |
| Árvore de decisão | 0,500 | 0,715 | 0,500 | 0,618 | 0,500 | 0,567 |
| Random Forest | 0,743 | 0,827 | 0,966 | 0,967 | 0,603 | 0,821 |
| Gradient boosting | 0,756 | 0,827 | 0,985 | 0,883 | 0,591 | 0,808 |

A média esconde a variação. A Random Forest transfere bem para Guiné e Maurício (0,97), razoavelmente para Egito, mal para Benin e quase nada para Moçambique. A logística chega a 0,500 em Benin e 0,496 em Guiné, o que equivale ao acaso. A busca em grade da Random Forest com um tipo de fora (18 combinações) escolheu profundidade 12, `sqrt` das colunas por divisão e folha mínima 8, com AUC média de 0,875 [modelagem.json]. Esse valor ainda está bem abaixo dos 0,991 do sorteio aleatório.

### 5.4 Holdout final, ID e OOD

**Tabela única de comparação**, gerada por `src/comparacao.py` a partir de `modelagem.json` e `cnn.json` [comparacao.csv]:

| Modelo | Split | n | ROC-AUC | AuDET | APCER@1%BPCER | FREUID | Recall no limiar de custo |
|---|---|---:|---:|---:|---:|---:|---:|
| Regressão logística | validação ID | 4.037 | 0,968 | 0,032 | 0,175 | 0,109 | 0,935 |
| Random Forest | validação ID | 4.037 | 0,991 | 0,009 | 0,073 | 0,042 | 0,964 |
| Gradient Boosting | validação ID | 4.037 | 0,993 | 0,007 | 0,069 | 0,039 | 0,967 |
| Regressão logística | OOD (Moçambique) | 4.816 | 0,669 | 0,331 | 0,942 | 0,892 | 0,323 |
| Random Forest | OOD (Moçambique) | 4.816 | 0,584 | 0,416 | 0,925 | 0,867 | 1,000 |
| Gradient Boosting | OOD (Moçambique) | 4.816 | 0,541 | 0,459 | 1,000 | 1,000 | 1,000 |
| EfficientNet-B0 | validação ID | 4.037 | 0,9999 | 0,0001 | 0,001 | 0,0003 | 0,998 |
| EfficientNet-B0 | OOD (Moçambique) | 4.816 | 0,796 | 0,203 | 0,501 | 0,387 | 1,000 |

O gradient boosting aparece só como contraste. Recall de 1,000 no OOD significa que o modelo marcou todas as imagens como fraude no limiar de custo herdado; não é acerto.

Matriz de confusão no limiar de custo, holdout dos clássicos [modelagem.json]:

| Modelo | Split | Limiar | VN | FP | FN | VP | Custo |
|---|---|---:|---:|---:|---:|---:|---:|
| Regressão logística | ID | 0,26 | 1.845 | 462 | 113 | 1.617 | 1.027 |
| Random Forest | ID | 0,22 | 2.062 | 245 | 62 | 1.668 | 555 |
| Regressão logística | OOD | 0,26 | 2.421 | 462 | 1.308 | 625 | 7.002 |
| Random Forest | OOD | 0,22 | 0 | 2.883 | 0 | 1.933 | 2.883 |

No limiar 0,5 a Random Forest tem, na validação ID, recall de fraude de 0,920 e apenas 5 falsos positivos em 2.307 legítimos [modelagem.json]. O limiar de custo (0,22) troca 240 alarmes falsos a mais por 76 fraudes a menos passando, e o custo total cai [modelagem.json]. No OOD o mesmo limiar marca as 4.816 imagens de Moçambique como fraude: recall 1,00 e nenhum legítimo aceito [modelagem.json]. Isso não é detecção, é recusar o país inteiro. A regressão logística, no OOD, deixa passar 1.308 das 1.933 fraudes (recall 0,323) [modelagem.json].

O erro de calibração da Random Forest é 0,017 na validação ID e 0,500 no OOD [modelagem.json]: a probabilidade estimada deixa de significar probabilidade no tipo novo. Na validação ID, os erros também não são uniformes por tipo: com o limiar de custo, a Random Forest deixa passar 15,0% das fraudes de Benin e manda para conferência 38,4% dos legítimos de Benin, contra menos de 1% nos dois indicadores em Guiné e Maurício [modelagem.json].

**CNN.** O treino parou na época 6 por early stopping. A melhor AUC da validação ID foi na época 3, e esses pesos foram usados [cnn.json]. Cada época levou cerca de 13 minutos na RTX 4060 [cnn.json].

| EfficientNet-B0 | Limiar | VN | FP | FN | VP | Recall | Custo |
|---|---:|---:|---:|---:|---:|---:|---:|
| Validação ID | 0,50 | 2.306 | 1 | 8 | 1.722 | 0,995 | 41 |
| Validação ID | 0,07 (custo) | 2.304 | 3 | 3 | 1.727 | 0,998 | 18 |
| OOD (Moçambique) | 0,50 | 162 | 2.721 | 19 | 1.914 | 0,990 | 2.816 |
| OOD (Moçambique) | 0,07 (custo) | 0 | 2.883 | 0 | 1.933 | 1,000 | 2.883 |

Fonte: [cnn.json]. Nos tipos vistos, a CNN erra 6 de 4.037 imagens no limiar de custo. A AUC é de pelo menos 0,9999 em cada um dos quatro tipos separadamente [cnn_diagnostico.json]. No tipo novo ela ordena melhor que os clássicos: AUC 0,797, FREUID 0,387 e APCER@1%BPCER de 0,501 [cnn.json]. A diferença de AUC em relação à regressão logística, com bootstrap pareado de 1.000 reamostragens dos mesmos ids, é de 0,127 (IC 95% de 0,112 a 0,143), e em relação à Random Forest é de 0,212 (IC 95% de 0,195 a 0,231) [cnn_diagnostico.json].

O escore, porém, não se transfere com a mesma escala. Na validação ID, a mediana de P(fraude) dos legítimos é 0,013; em Moçambique é 0,786, e 94,4% dos legítimos ficam acima de 0,5 [cnn_diagnostico.json]. Por isso, tanto o limiar 0,5 quanto o limiar de custo (0,07) mandam quase todas as imagens do tipo novo para conferência (Figura `reports/figs/cnn_matriz.png`). A ordenação existe, mas o ponto de corte precisa ser outro. Como diagnóstico, e usando rótulos do próprio OOD (fora do protocolo), o corte que daria 1% de BPCER em Moçambique seria 0,964, e nele a CNN pegaria 49,9% das fraudes [cnn_diagnostico.json]. Um órgão só chegaria a esse corte com uma amostra rotulada do tipo novo. As curvas ROC e DET estão em `reports/figs/cnn_roc_det.png`.

### 5.5 Checagem de atalho

Três AUCs passaram de 0,98 na validação ID: árvore (0,981), Random Forest (0,991) e gradient boosting (0,993) [modelagem.json]. A regra do protocolo manda procurar a causa:

| Verificação | Resultado |
|---|---|
| Identificadores repetidos entre treino, validação ID e OOD | 0, 0 e 0 |
| AUC usando só largura, altura e tamanho do arquivo | 0,550 (ID) e 0,534 (OOD) |
| AUC usando só o tipo do documento (ID) | 0,534 |
| Acurácia ao prever o tipo a partir das 73 características | 0,9999 (chance: 0,229) |

Fonte: [modelagem.json]. Não houve vazamento de identificador nem de arquivo, e o tipo do documento sozinho não prevê fraude. O número alto, portanto, não é truque de split. Mas as 73 características são uma impressão digital do modelo de carteira. Dentro de cada carteira, o histograma e o ELA de uma imagem fraudada se afastam do padrão daquela carteira, e o modelo aprende esse desvio. A importância por permutação aponta para o desvio do ELA (queda de AUC de 0,021) e para as faixas escuras dos histogramas [importancia_permutacao.csv]. O desvio aprendido só existe em relação a um padrão conhecido. Em Moçambique o padrão é outro, e a referência desaparece.

**A CNN também passou de 0,98 no ID.** Os identificadores são os mesmos dos clássicos, conferidos pelo hash de cada split [cnn.json], e não há sobreposição entre conjuntos [modelagem.json]. A AUC fica acima de 0,9999 em cada tipo isoladamente [cnn_diagnostico.json], então o resultado não vem de reconhecer o tipo e usar a taxa de fraude do tipo. O que não dá para excluir é que a fraude sintética da competição deixe marcas regulares de geração dentro de cada modelo de carteira, que a rede aprende muito bem e que mudam quando o modelo de carteira muda. A queda para 0,797 no OOD é compatível com essa leitura.

**Onde a CNN olha (Grad-CAM).** O Grad-CAM da última camada convolucional foi calculado em 30 imagens: 8 acertos sorteados e os únicos 6 erros da validação ID, e 8 acertos e 8 erros do OOD, no limiar de custo. As sobreposições ficam apenas em `C:\freuid\runs\ood_efficientnet_b0\gradcam\`, por causa da licença. Nos acertos da validação ID, o mapa se concentra em regiões do rosto, como o retrato secundário pequeno de segurança e a base do retrato principal, e em blocos de campos de texto. Essas são regiões plausíveis de troca de rosto e de edição de dados. Nos casos de Moçambique, o mapa é mais espalhado pela carteira, com alguma ênfase na base do retrato e numa faixa de texto inferior. A fração do mapa na borda externa de 10% da imagem foi de 0,38 nos acertos ID, 0,44 nos erros ID e 0,35 e 0,34 no OOD, contra 0,36 se o mapa fosse uniforme [gradcam_resumo.json]. Não há sinal de que a rede se apoie na borda ou no fundo da foto. Com 30 imagens, isso é descrição qualitativa. Não prova que a rede detecta o artefato da fraude em vez de uma assinatura do gerador do dataset.

## 6. Discussão

**Por que o OOD cai.** Os dados mostram três coisas ao mesmo tempo. Dentro dos tipos vistos, as características separam fraude de legítimo muito bem (AUC 0,991 na Random Forest). As mesmas características identificam o tipo com acurácia de 0,9999. E, quando o tipo é novo, a ordenação se perde (AUC 0,584) [modelagem.json]. A leitura mais simples é que o modelo aprende "o que é anormal para esta carteira". Para uma carteira nova, com outro fundo, outras cores e outro leiaute, tudo é anormal, ou nada é. O leave-one-type-out mostra que a transferência depende de quão parecida é a carteira nova com as do treino: Guiné e Maurício se beneficiam, Moçambique e Benin não [modelagem.json].

**Por que 1% de BPCER é o ponto que importa.** Um órgão que recebe 100 mil cadastros com 1% de legítimos barrados já manda mil cidadãos para atendimento presencial. Esse é o limite operacional plausível. Nesse ponto, a Random Forest deixa passar 7,3% das fraudes nos tipos vistos e 92,5% no tipo novo [modelagem.json]. A AUC sozinha esconde essa diferença: uma AUC de 0,58 parece "melhor que o acaso", mas, no ponto em que o órgão pode operar, quase todas as fraudes passam.

**Humano no loop.** O uso defensável é ordenar a fila de conferência: o servidor olha primeiro os casos com escore mais alto, e o limiar de custo decide quantos casos vão para a fila. O modelo não deve recusar ninguém sozinho. Isso vale ainda mais para um tipo de documento ausente do treino: ali a probabilidade calculada deixa de significar probabilidade (erro de calibração de 0,500), e a decisão volta inteira para a pessoa.

**Limites.**
- O dataset é sintético e tem cinco tipos estrangeiros. O comportamento em documentos brasileiros reais não foi medido.
- Recaptura (impressão fotografada) tem 20 exemplos. Um dos ataques que a competição destaca não pode ser aprendido nem avaliado aqui.
- O teste OOD é um único tipo. A variação do leave-one-type-out (de 0,60 a 0,97 na Random Forest) mostra que outro tipo novo poderia dar um número muito diferente.
- A CNN foi treinada uma vez, com uma semente e uma configuração. Com 4.816 imagens no OOD, a vantagem de ordenação da EfficientNet sobre os clássicos tem intervalo de confiança estreito [cnn_diagnostico.json], mas vale para este tipo e esta execução. Ela não autoriza afirmar que a CNN generaliza para qualquer tipo novo. O limiar de custo da CNN foi escolhido na validação ID, que também escolheu a época, então seus números ID no limiar de custo são otimistas.
- As características são globais. Uma edição pequena em uma região do documento pode se diluir no histograma.
- Os experimentos anteriores deste trabalho são registro histórico e não entram nas tabelas acima. O primeiro chegou a AUC de 0,889 na regressão logística com 109 imagens de validação [reports/metrics.csv]. O segundo usou 464 imagens, com 76 na validação ID e 84 no OOD, e obteve AUC de 0,940 (ID) e 0,550 (OOD) na logística [historico_n464/results.md]. Com amostras desse tamanho, nenhuma diferença fina entre modelos podia ser afirmada, mas a queda no OOD já aparecia. Com 24.998 a estimativa interna é estável, mas a conclusão sobre OOD continua apoiada em um único tipo.

**Licença.** O dataset é de uso acadêmico e não comercial. Nenhuma imagem foi publicada, nenhum dado foi redistribuído, os pesos do modelo ficam fora do repositório, e o modelo não pode ser usado em produção, inclusive em sistemas de órgãos públicos. Os dados devem ser apagados ao fim do trabalho.

## 7. Conclusão

Com os modelos da disciplina, um órgão público consegue estimar P(fraude) a partir da imagem do documento nos tipos de documento presentes no treino. A regressão logística, interpretável e simples, chega a AUC 0,968, e a Random Forest a 0,991, ambas avaliadas em 4.037 imagens que não participaram do ajuste [modelagem.json]. Com limiar definido pelo custo do erro, a Random Forest deixa passar 62 de 1.730 fraudes e manda 245 de 2.307 legítimos para conferência [modelagem.json].

Esse escore não vale para um tipo de documento novo. Com Moçambique inteiro fora do treino, a AUC cai para 0,669 e 0,584, o escore FREUID fica perto de 0,9 e a calibração se perde [modelagem.json]. A checagem de atalho mostra por quê: as características identificam a carteira, e o modelo aprende o desvio em relação a cada carteira conhecida. A EfficientNet-B0 reduz a queda: no tipo novo, ela ainda ordena (AUC 0,797, cerca de metade das fraudes pegas a 1% de BPCER) [cnn.json], mas a escala do escore muda tanto que o limiar dos tipos conhecidos deixa de servir [cnn_diagnostico.json].

A resposta à pergunta do trabalho, portanto, é: sim para triagem assistida nos tipos conhecidos, com pessoa conferindo; não para um tipo novo sem nova amostra rotulada e novo teste fora da distribuição.

## Referências

1. RELIĆ, I.; D'ELIA, V.; BORTOLI, S.; TUDORAN, R.; NEDYALKOVA, H.; BOŠNJAK, M.; PAVLIĆ, S.; MAVRAČIĆ, T.; DAŠIĆ, D.; KAČAN, M.; ŠEGVIĆ, J.; ČERIĆ, P.; ŠOPRUN, F.; MIOČIĆ, M.; ORŠIĆ, M.; VAIANI, L.; GARZA, P. *The FREUID Challenge 2026 – IJCAI-ECAI.* Kaggle, 2026. https://www.kaggle.com/competitions/the-freuid-challenge-2026-ijcai-ecai
2. Dataset FREUID fornecido pelo Microblink Fraud Lab (Microblink LLC), licença de pesquisa não comercial.
3. ISO/IEC 30107-3:2023. *Information technology — Biometric presentation attack detection — Part 3: Testing and reporting.*
4. TAN, M.; LE, Q. EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks. *Proceedings of ICML*, 2019.
5. BREIMAN, L. Random Forests. *Machine Learning*, v. 45, p. 5–32, 2001.
6. PEDREGOSA, F. et al. Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, v. 12, p. 2825–2830, 2011.
7. SELVARAJU, R. R. et al. Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization. *Proceedings of ICCV*, 2017.
8. BRASIL. Lei nº 13.709, de 14 de agosto de 2018. Lei Geral de Proteção de Dados Pessoais.
9. UFG/IIG. Materiais de Técnicas de IA I: fluxo supervisionado, regressão logística, árvores, Random Forest, métricas e matriz de confusão.

## Anexo: origem de cada número

| Peça | Arquivo |
|---|---|
| Inventário, universo e split | `reports/analise/inventario.json` (script `src/inventario.py`) |
| População e exploração das imagens | `reports/analise/eda.json`, `reports/figs/eda_*.png` (`src/eda_completa.py`) |
| Modelos clássicos | `reports/analise/modelagem.json`, `importancia_permutacao.csv`, `reports/figs/mod_*.png` (`src/modelagem.py`) |
| CNN | `reports/analise/cnn.json`, `reports/figs/cnn_*.png` (`src/cnn_protocolo.py`) |
| Grad-CAM (só números) | `reports/analise/gradcam_resumo.json` (`src/gradcam.py`) |
| Tabela de comparação | `reports/analise/comparacao.csv`, `reports/figs/comparacao_id_ood.png` (`src/comparacao.py`) |
| Experimento anterior (n = 464) | `reports/historico_n464/` |
