# FREUID 2026: fraude em documentos de identidade

Trabalho final de **Técnicas de IA I** (UFG / IIG, prof. Paulo Victor dos Santos, 2026/2). Aluno: João Henrique Gomes Dias.

Pergunta: um órgão público consegue usar a imagem do documento para estimar P(fraude) com os modelos da disciplina, e esse escore ainda vale quando o tipo de documento é novo?

**As imagens, os CSVs do dataset, `features.csv`, as previsões e os pesos `.pt` ficam fora do git**, em `C:\freuid\` (licença Microblink: pesquisa não comercial, sem redistribuição). O repositório guarda código, JSON com números agregados, gráficos sem foto de documento e a lista de caminhos das imagens usadas.

## Ambiente

| Item | Onde |
|---|---|
| Código | `freuid-trabalho/` (este diretório) |
| Dados | `C:\freuid\data` (variável `FREUID_DATA`) |
| Imagens | `C:\freuid\data\dataset_completo\...\train\train` (procurada por `src/config.py`; `FREUID_IMAGES` sobrepõe) |
| Python | `C:\freuid\.venv\Scripts\python.exe` (torch com CUDA) |
| Saídas da CNN | `C:\freuid\runs\ood_efficientnet_b0\` (log, pesos, previsões, Grad-CAM) |
| Núcleos de CPU | `FREUID_JOBS` (padrão 8; a máquina teve telas azuis sob carga total) |

## Como reproduzir

Rodar de dentro de `src/`, nesta ordem:

```powershell
cd freuid-trabalho\src
$py = "C:\freuid\.venv\Scripts\python.exe"
& $py inventario.py      # 1. conta JPEGs, monta o universo e o split → reports/analise/inventario.json
& $py eda_completa.py    # 2. população (69.352 rótulos) + imagens do universo → eda.json, figs/eda_*.png
& $py modelagem.py       # 3. sete modelos clássicos, CV, LOTO, holdout ID/OOD → modelagem.json, figs/mod_*.png
& $py cnn_protocolo.py --epocas 10 --paciencia 3 --bs 16 --workers 0   # 4. EfficientNet-B0 → cnn.json, figs/cnn_*.png
& $py diagnostico_cnn.py # 4b. AUC por tipo, deslocamento do escore, bootstrap → cnn_diagnostico.json
& $py gradcam.py --n 8   # 4c. Grad-CAM só em C:\freuid\runs; no repo só gradcam_resumo.json (números)
& $py comparacao.py      # 5. tabela única → comparacao.csv, figs/comparacao_id_ood.png
& $py figuras_extras.py  # 7a. tempos.json + figuras cnn_treino, cnn_escores, gradcam_borda, tempos
& $py apresentacao.py    # 7b. slides → reports/apresentacao_trabalho.html
```

- A extração das 73 características roda na primeira chamada de `eda_completa.py` e fica em cache em `C:\freuid\data\features.csv`. Ela grava blocos em `features_parcial\` e retoma se for interrompida.
- A CNN salva `ultimo.pt` a cada época. Se a máquina cair, repita o comando com `--retomar`.
- Use `--workers 0` na CNN nesta máquina: com processos auxiliares do DataLoader, eles caíram com `access violation` (ver abaixo).

## O que cada script gera

| Script | Saída no repositório | Saída fora do git |
|---|---|---|
| `src/protocolo.py` | (usado por todos) contagens e hash dos splits nos JSON | `C:\freuid\data\split_protocolo.csv` |
| `src/inventario.py` | `reports/analise/inventario.json` | |
| `src/eda_completa.py` | `reports/analise/eda.json`, `ranking_features.csv`, `reports/figs/eda_*.png` | `features.csv` |
| `src/modelagem.py` | `reports/analise/modelagem.json`, `importancia_permutacao.csv`, `reports/figs/mod_*.png` | `previsoes_classicos.csv` |
| `src/cnn_protocolo.py` | `reports/analise/cnn.json`, `reports/figs/cnn_roc_det.png`, `cnn_matriz.png` | pesos, log, `previsoes_validacao.csv` |
| `src/diagnostico_cnn.py` | `reports/analise/cnn_diagnostico.json` | |
| `src/gradcam.py` | `reports/analise/gradcam_resumo.json` (só números) | sobreposições em `runs\...\gradcam\` |
| `src/comparacao.py` | `reports/analise/comparacao.csv`, `reports/figs/comparacao_id_ood.png` | |
| `src/figuras_extras.py` | `reports/analise/tempos.json`, `reports/figs/cnn_treino.png`, `cnn_escores.png`, `gradcam_borda.png`, `tempos.png` | |
| `src/apresentacao.py` | `reports/apresentacao_trabalho.html` (20 slides; tecla N mostra as notas) | |

Artigo: `reports/artigo_FREUID.md`. Os números do artigo saem desses JSON. O experimento anterior com 464 imagens está em `reports/historico_n464/` e não se mistura com a tabela nova.

Scripts antigos mantidos: `src/train.py`, `src/eda.py`, `src/cnn.py` (versão Kaggle), `src/download*.py`, `src/baixar_imagens.py`.

## Protocolo

Semente 42. Universo = `amostra.csv` ∩ JPEGs existentes com tamanho > 0 (24.998). MOZAMBIQUE/DL inteiro é o teste OOD. Os outros quatro tipos se dividem em 80/20, estratificado por rótulo (treino / validação ID). Clássicos e CNN usam os mesmos ids. Limiar operacional por custo: fraude que passa = 5, legítimo enviado à conferência = 1.

## Observação sobre a máquina (24/11/2026)

A primeira tentativa de treinar a CNN derrubou o Windows (telas azuis com códigos variados: 0x0A, 0x3B, 0x50, 0xF7). Depois disso, processos Python auxiliares caíram com `access violation` ao importar bibliotecas padrão. O quadro sugere instabilidade de hardware, provavelmente memória. Recomenda-se um teste de memória e rever XMP/overclock. Por isso há checkpoint por época, extração retomável e `FREUID_JOBS`.

## Licença (obrigatório)

- Relić, I. et al. *The FREUID Challenge 2026 – IJCAI-ECAI.* Kaggle, 2026.
- Dataset FREUID fornecido pelo Microblink Fraud Lab (Microblink LLC), licença de pesquisa não comercial.
- Não versionar imagens, CSVs do dataset, `features.csv`, pesos nem `kaggle.json`.
- `reports/analise/imagens_utilizadas.csv` lista só o `id` e o caminho das 24.998 imagens usadas, dentro do zip da competição (`train/train/<id>.jpeg`). Não traz a foto nem o rótulo. O dataset está em https://www.kaggle.com/competitions/the-freuid-challenge-2026-ijcai-ecai
- Não publicar foto, recorte ou Grad-CAM sobre documento em artigo, slide ou git.
- Não usar o modelo em produto ou produção. Apagar os dados ao fim do trabalho.
