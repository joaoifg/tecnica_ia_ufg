# FREUID 2026 — Fraude em documentos de identidade

Trabalho de **Técnicas de IA I** (UFG / IIG) — classificação binária legítimo vs fraude, aplicada à validação cadastral na administração pública.

## Status

| Etapa | Situação |
|---|---|
| EDA dos 69.352 rótulos e da amostra de 464 imagens | OK → `reports/analise/eda.json` |
| Treino clássico (7 modelos, ID e OOD) | OK → `reports/results.md` |
| Artigo | OK → `reports/artigo_FREUID.md` |
| Slides da apresentação | OK → `reports/apresentacao_FREUID.html` |
| CNN EfficientNet (Kaggle) | Código em `src/cnn.py`; não executada neste ambiente |

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
python src\download.py       # subset estratificado (retomável)
python src\eda_completa.py   # estudo dos rótulos e da amostra local
python src\modelagem.py      # treino clássico → reports/analise e reports/figs
```

Abrir slides: `reports/apresentacao_FREUID.html` (setas / espaço).

## Licença (obrigatório)

- Dados sintéticos Microblink — **só pesquisa não comercial**
- Não publicar imagens; não versionar `data/`
- Citar Relić et al. / Microblink Fraud Lab
- Não usar o modelo em produto comercial
