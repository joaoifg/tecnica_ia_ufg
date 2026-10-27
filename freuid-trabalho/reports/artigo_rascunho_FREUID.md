# Detecção automática de fraude em documentos de identidade com aprendizado de máquina: aplicação à validação cadastral na administração pública

**Autor:** João Henrique Gomes Dias  
**Curso:** Bacharelado em IA Aplicada à Gestão Pública — UFG / IIG  
**Disciplina:** Técnicas de IA I  

> Rascunho vivo: preencher números finais em *Resultados* após o treino local e o notebook Kaggle.

## Resumo
A validação de documentos de identidade é etapa crítica em cadastros públicos (conselhos profissionais, benefícios, concursos). Ataques modernos combinam manipulação física, edição por IA generativa e recaptura (*print-and-capture*). Este trabalho formula o problema como classificação binária supervisionada `D = {(x, y)}`, utilizando o dataset sintético da competição FREUID Challenge 2026 (IJCAI-ECAI / Microblink). Comparam-se regressão logística, Random Forest e uma CNN com *transfer learning* (EfficientNet-B0). A avaliação prioriza ROC-AUC e APCER a 1% de BPCER, refletindo o custo assimétrico de aceitar fraude versus rejeitar cidadão legítimo. No subset local (544 imagens, features clássicas), a regressão logística alcançou ROC-AUC **0,89** em tipos vistos; em tipo deixado de fora (OOD) o desempenho caiu (~0,69), evidenciando o desafio de generalização. O modelo é proposto como apoio à decisão humana, sob licença acadêmica não comercial.

**Palavras-chave:** fraude documental; aprendizado supervisionado; Random Forest; CNN; gestão pública; FREUID.

## 1. Introdução
Órgãos públicos e conselhos profissionais dependem da autenticidade documental para conceder direitos e emitir credenciais. Deepfakes e edições generativas elevam o risco de fraude em canais digitais. O objetivo deste trabalho é desenvolver e comparar modelos de IA capazes de estimar a probabilidade de fraude a partir da imagem do documento, discutindo limitações, viés e aderência a restrições de uso do dataset.

## 2. Referencial teórico
### 2.1 Identidade documental e prova de autenticidade
Documentos oficiais combinam elementos visuais, tipográficos e de segurança. Sistemas de verificação automatizada atuam como camada de triagem antes da análise humana.

### 2.2 Fraudes digitais e generativas
Manipulação física, edição por modelos generativos e *print-and-capture* introduzem artefatos distintos (compressão, moiré, inconsistência de fontes/hologramas).

### 2.3 Modelos utilizados
- **Regressão logística:** baseline linear interpretável sobre vetores de características.
- **Random Forest:** ensemble de árvores; robusto a não linearidades (conteúdo das aulas).
- **CNN / EfficientNet:** *transfer learning* a partir de pesos ImageNet, ajustada à tarefa binária.

### 2.4 Métricas e custo assimétrico
AuDET (≈ 1 − ROC-AUC) e APCER @ 1% BPCER capturam o trade-off entre falso positivo (rejeitar legítimo) e falso negativo (aceitar fraude). Na gestão pública, operar com BPCER baixo (ex.: 1%) é requisito operacional.

### 2.5 Aspectos legais e éticos
O dataset FREUID é **sintético** (não contém pessoas reais). Ainda assim, a licença Microblink restringe uso a pesquisa não comercial, proíbe redistribuição e publicação das imagens, e exige citação. Modelos treinados **não** devem ir a produção comercial.

## 3. Materiais e métodos
### 3.1 Dataset
Competição *The FREUID Challenge 2026 – IJCAI-ECAI*. Treino rotulado: 69.352 imagens; rótulos `label`, `is_digital`, `type`. Classes: 57,7% legítimas e 42,3% fraude; cinco tipos de documento. Quase todas as amostras de treino são digitais (`is_digital=1`); apenas 20 recapturadas.

### 3.2 Pré-processamento e subset
Como o conjunto completo é grande (~dezenas de GB), utilizou-se:
1. subset estratificado local (~2.500 imagens) para baselines clássicos;
2. notebook Kaggle com GPU para CNN sobre recorte maior do `train/`.

Caminho remoto das imagens: `train/train/<id>.jpeg` (o CSV lista `train/<id>.jpeg`).

### 3.3 Características clássicas
Histograma de cor (16 bins/canal) + estatísticas (média, desvio, extremos) + energia de gradiente — vetor compacto sem deep learning, alinhado às técnicas da disciplina.

### 3.4 Protocolo de validação
- Split **OOD:** um `type` inteiro fora do treino.
- Split **ID:** holdout agrupado por tipo entre os documentos vistos.
- Relato separado para `is_digital` quando houver amostra suficiente.

### 3.5 Modelos e hiperparâmetros
- Regressão logística: `class_weight=balanced`, `max_iter=2000`, features padronizadas.
- Random Forest: 300 árvores, `max_depth=20`, `class_weight=balanced_subsample`.
- EfficientNet-B0: fine-tuning, 384×384, AdamW, BCEWithLogits, 5 épocas (Kaggle).

## 4. Resultados

Subset local: **544** imagens; tipo OOD = `MOZAMBIQUE/DL`. Features: histograma + estatísticas (sem CNN).

| Modelo | Split | n | ROC-AUC | APCER@1%BPCER | FREUID ↓ | Recall fraude |
|---|---|---:|---:|---:|---:|---:|
| Reg. logística | ID | 109 | **0,889** | 0,393 | **0,279** | 0,821 |
| Random Forest | ID | 109 | 0,808 | 0,429 | 0,331 | 0,679 |
| Reg. logística | OOD | 41 | 0,687 | 1,000 | 1,000 | 1,000 |
| Random Forest | OOD | 41 | 0,690 | 0,700 | 0,582 | 1,000 |

CNN EfficientNet-B0: resultados a preencher após rodar `notebooks/FREUID_CNN_Kaggle.ipynb` no Kaggle (GPU).

Figuras geradas (sem imagens do dataset): `roc_compare_id.png`, `cm_*.png`, `auc_by_type_*.png`.

## 5. Discussão
- **Uso público:** o score contínuo permite calibrar o limiar conforme a política de risco do órgão (priorizar baixo APCER ou baixo BPCER).
- **Limitações:** pouquíssimos exemplos recapturados no treino; apenas cinco tipos; risco de *shortcut learning* (métricas internas altas que não generalizam).
- **Licença:** resultados podem ser publicados; imagens e pesos derivados para produto comercial, não.
- **Governança:** recomendação de humano no loop.

## 6. Conclusão
O problema de fraude documental é modelável como classificação supervisionada com dataset público de competição. Baselines clássicos oferecem referência didática; CNNs tendem a melhor capturar artefatos finos. Trabalhos futuros: ampliar tipos OOD, balancear recaptura, calibrar limiares por órgão e auditar fairness entre países/tipos.

## Referências
1. Relić, I. et al. *The FREUID Challenge 2026 - IJCAI-ECAI.* https://www.kaggle.com/competitions/the-freuid-challenge-2026-ijcai-ecai, 2026.
2. Dataset FREUID — Microblink Fraud Lab (Microblink LLC), licença de pesquisa não comercial.
3. Brasil. Lei nº 13.709/2018 (LGPD).
4. Materiais da disciplina Técnicas de IA I — UFG/IIG (regressão logística, Random Forest, avaliação de classificadores).

## Anexo
- Código: pasta `freuid-trabalho/src/`
- EDA: `reports/eda.md`
- Baselines: `reports/results.md`
- CNN: `notebooks/FREUID_CNN_Kaggle.ipynb`
