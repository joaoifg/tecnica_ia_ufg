# Resultados — FREUID, modelos clássicos

Treino executado na amostra local de **464** imagens (todas digitais). Protocolo: semente 42; Moçambique/DL inteiro fora do treino; 80/20 estratificado nos outros tipos. Números completos em `reports/analise/modelagem.json` e no artigo `reports/artigo_FREUID.md`.

Validação cruzada no treino (304 imagens, 73 características):

| Modelo | ROC-AUC |
|---|---:|
| Baseline | 0,500 ± 0,000 |
| Regressão logística | 0,913 ± 0,014 |
| Random Forest | 0,951 ± 0,024 |
| Gradient boosting | 0,956 ± 0,019 |

Holdout. ID = tipos vistos (n = 76). OOD = Moçambique (n = 84).

| Modelo | Split | ROC-AUC | FREUID | APCER @ 1% BPCER |
|---|---|---:|---:|---:|
| Regressão logística | ID | 0,940 | 0,122 | 0,176 |
| Random Forest | ID | 0,965 | 0,129 | 0,206 |
| Gradient boosting | ID | 0,978 | 0,124 | 0,206 |
| Regressão logística | OOD | 0,550 | 0,943 | 0,970 |
| Random Forest | OOD | 0,510 | 1,000 | 1,000 |
| Gradient boosting | OOD | 0,547 | 1,000 | 1,000 |

As 73 características identificam o tipo do documento com acurácia 1,00. O desempenho interno não se transfere para um tipo ausente do treino.

Figuras: `reports/figs/mod_roc_pr_id.png`, `mod_roc_pr_ood.png`, `mod_matriz_id.png`, `mod_cv_vs_loto.png`, `mod_importancia.png`.
