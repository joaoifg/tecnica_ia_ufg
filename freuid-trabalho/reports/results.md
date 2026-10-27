# Resultados — baselines FREUID

- Subset local: **544** imagens
- Tipo deixado de fora (OOD): `MOZAMBIQUE/DL`

| model               | split   |   n |   roc_auc |   audet |   apcer@1%bpcer |   freuid_score |   accuracy |   f1_fraude |   recall_fraude |
|:--------------------|:--------|----:|----------:|--------:|----------------:|---------------:|-----------:|------------:|----------------:|
| logistic_regression | id      | 109 |    0.8889 |  0.1111 |          0.3929 |         0.2785 |     0.7064 |      0.5897 |          0.8214 |
| logistic_regression | ood     |  41 |    0.6869 |  0.3131 |          1      |         1      |     0.5122 |      0.6667 |          1      |
| random_forest       | id      | 109 |    0.8082 |  0.1918 |          0.4286 |         0.3305 |     0.8165 |      0.6552 |          0.6786 |
| random_forest       | ood     |  41 |    0.6905 |  0.3095 |          0.7    |         0.5817 |     0.5122 |      0.6667 |          1      |

Gráficos: `roc_compare_id.png`, `cm_*.png`, `auc_by_type_*.png`.