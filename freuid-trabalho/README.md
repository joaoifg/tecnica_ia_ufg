# FREUID 2026 — Fraude em documentos de identidade

Trabalho de **Técnicas de IA I** (UFG / IIG) — classificação binária legítimo vs fraude, aplicada à validação cadastral na administração pública.

## Status

| Etapa | Situação |
|---|---|
| EDA dos rótulos | OK → `reports/eda.md` |
| Subset local (~544 imgs no E:) | OK |
| Baselines RL + RF | OK → `reports/results.md` |
| Slides da apresentação | OK → `reports/apresentacao_FREUID.html` |
| Rascunho do artigo | OK → `reports/artigo_rascunho_FREUID.md` |
| CNN EfficientNet (Kaggle) | Pendente — subir o notebook |

## Estrutura

```
freuid-trabalho/
├── data/                 # NÃO versionar (CSVs + junction p/ imagens no E:)
├── src/                  # download, features, train, metric
├── notebooks/            # FREUID_CNN_Kaggle.ipynb
└── reports/              # eda, métricas, slides, artigo
```

## Comandos

```powershell
cd freuid-trabalho
.\.venv\Scripts\Activate.ps1
python src\eda.py
python src\download.py    # subset estratificado (retomável)
python src\train.py       # RL + RF → reports/
```

Abrir slides: `reports/apresentacao_FREUID.html` (setas / espaço).

## Licença (obrigatório)

- Dados sintéticos Microblink — **só pesquisa não comercial**
- Não publicar imagens; não versionar `data/`
- Citar Relić et al. / Microblink Fraud Lab
- Não usar o modelo em produto comercial
