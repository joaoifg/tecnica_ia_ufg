# FREUID 2026 — Contexto e guia de uso (trabalho Técnicas de IA / UFG-IIG)

> Documento de contexto para o agente do Cursor. Leia inteiro antes de executar qualquer comando.

---

## 1. Objetivo do trabalho

- **Disciplina:** Técnicas de IA — Bacharelado em IA Aplicada à Gestão Pública (UFG / IIG).
- **Tema:** detecção de fraude em documentos de identidade, aplicada à administração pública (identidade digital, emissão de documentos e validação cadastral de órgãos públicos e conselhos profissionais).
- **Tarefa de ML:** classificação binária de imagens.
  - `0` = documento legítimo (bona-fide)
  - `1` = documento fraudado (ataque)
  - O modelo gera um score contínuo em [0, 1], e quanto maior o score, mais provável é a fraude.

---

## 2. Fonte dos dados

| Item | Valor |
|---|---|
| Competição | The FREUID Challenge 2026 – IJCAI-ECAI |
| Slug (API) | `the-freuid-challenge-2026-ijcai-ecai` |
| Página | https://www.kaggle.com/competitions/the-freuid-challenge-2026-ijcai-ecai |
| Aba Data | https://www.kaggle.com/competitions/the-freuid-challenge-2026-ijcai-ecai/data |
| Regras | https://www.kaggle.com/competitions/the-freuid-challenge-2026-ijcai-ecai/rules |
| Site oficial | https://freuid2026.microblink.com/ |
| Organizador | Microblink LLC (Zagreb, Croácia) — Microblink Fraud Lab |
| Contato | freuid-challenge-2026@microblink.com |
| Status | Encerrada em 16/07/2026 (aberta para *Late Submission*) |
| Regras aceitas | Sim, pela conta Kaggle do João |

### 2.1 Tamanho

- **46,65 GB**, **212.186 arquivos** (JPEG + CSV).
- **NÃO baixar tudo.** Use o recorte necessário (seção 5).

### 2.2 Estrutura (Data Explorer)

```
private_test/              # sem rótulos — NÃO usar
public_test/               # sem rótulos — NÃO usar
train/                     # imagens de treino (rotuladas)
train_sample/              # recorte menor do treino — COMEÇAR POR AQUI
sample_submission.csv      # formato de submissão (142.818 linhas) — não necessário
train_labels.csv           # rótulos do train/
train_sample_labels.csv    # rótulos do train_sample/
```

### 2.3 Colunas dos rótulos

```
id,image_path,label,is_digital,type
000001,train/000001.jpg,0,0,USA/DL
000002,train/000002.jpg,1,0,SWITZERLAND/ID
000003,train/000003.jpg,1,1,CROATIA/ID
```

| Coluna | Significado |
|---|---|
| `id` | identificador da amostra |
| `image_path` | caminho relativo da imagem |
| `label` | 0 = legítimo, 1 = fraude |
| `is_digital` | 1 = totalmente digital; 0 = recapturado (impresso + fotografado) |
| `type` | `<PAÍS>/<TIPO>` (ex.: `USA/DL`, `CROATIA/ID`) |

> Confirme os nomes reais das colunas abrindo o CSV. A documentação cita `train.csv`, mas os arquivos se chamam `train_labels.csv` e `train_sample_labels.csv`.

### 2.4 Natureza dos dados

- Os dados são **sintéticos**. Nenhum documento ou pessoa é real, então não há dado pessoal sujeito à LGPD.
- Há três tipos de fraude: manipulação física, edição por IA generativa e *print-and-capture* (impressão seguida de nova fotografia).

---

## 3. Licença — REGRAS OBRIGATÓRIAS

O uso é permitido para **pesquisa científica não comercial** após o encerramento da competição (Dataset License §1 e §4). O agente deve respeitar estas regras:

1. **Nunca commitar dados no git.** Imagens e CSVs do dataset vão para `data/`, e essa pasta fica no `.gitignore`.
2. **Não compartilhar** os dados com ninguém, nem por Drive, nem por GitHub, nem com colegas ou com o professor. Cada pessoa precisa aceitar as regras com a própria conta.
3. **Não publicar imagens do dataset** no relatório, nos slides ou no repositório sem autorização escrita da Microblink. Use apenas métricas, tabelas e gráficos.
4. **Não criar dataset derivado** para distribuição. Pré-processamento e augmentation são permitidos apenas durante o treino.
5. **Não remover** marcas d'água nem metadados EXIF das imagens.
6. **Uso apenas acadêmico.** O modelo treinado não pode ser usado em produto comercial nem colocado em produção (inclusive no CFO ou no Credentia).
7. **Citar o dataset e a Microblink** no trabalho (seção 8).
8. **Apagar os dados** ao final do trabalho.

---

## 4. Configuração do acesso (Windows)

### 4.1 Token da API

1. Acesse https://www.kaggle.com/settings, vá em **API** e clique em **Create New Token**.
2. Se o Kaggle baixar um `kaggle.json`, salve em:
   ```
   C:\Users\<usuario>\.kaggle\kaggle.json
   ```
3. Se o Kaggle mostrar um token em texto (formato novo), defina a variável de ambiente:
   ```powershell
   setx KAGGLE_API_TOKEN "<token>"
   ```
   Depois reabra o terminal ou o Cursor.

> Nunca commitar o `kaggle.json` nem o token.

### 4.2 Instalação

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade kaggle pandas numpy scikit-learn pillow tqdm
```

### 4.3 Teste de acesso

```powershell
kaggle competitions files -c the-freuid-challenge-2026-ijcai-ecai
```

Se retornar **403**, as regras não foram aceitas por essa conta ou o token está errado.

---

## 5. Download (ordem recomendada)

### 5.1 Rótulos primeiro (pequenos)

```powershell
mkdir data
kaggle competitions download -c the-freuid-challenge-2026-ijcai-ecai -f train_sample_labels.csv -p data
kaggle competitions download -c the-freuid-challenge-2026-ijcai-ecai -f train_labels.csv -p data
```

Arquivos grandes podem chegar como `.zip`. Nesse caso, extraia em `data/`.

### 5.2 Analisar antes de baixar imagens

Antes de baixar qualquer imagem, o agente deve:
- contar as linhas de `train_sample_labels.csv` e de `train_labels.csv`;
- ver a distribuição de `label`, `is_digital` e `type`;
- listar os arquivos de `train_sample/` com o tamanho de cada um:
  ```powershell
  kaggle competitions files -c the-freuid-challenge-2026-ijcai-ecai --page-size 200
  ```
  Use `--page-token` para paginar e salve a lista em `data/file_list.csv`.

### 5.3 Imagens do `train_sample/`

A CLI baixa **um arquivo por vez** com `-f` e não baixa pastas inteiras. Escreva um script Python que:
- leia `train_sample_labels.csv`;
- baixe cada imagem com a API, pulando as que já existem (o script deve poder ser retomado):
  ```python
  from kaggle.api.kaggle_api_extended import KaggleApi
  api = KaggleApi(); api.authenticate()
  api.competition_download_file(
      "the-freuid-challenge-2026-ijcai-ecai",
      "train_sample/<arquivo>.jpg",
      path="data/train_sample",
      quiet=True,
  )
  ```
- use paralelismo moderado (4 a 8 threads) com retry, para não sofrer rate limit;
- registre as falhas em `data/download_errors.log`.

Alternativa manual: no Data Explorer, clique na pasta `train_sample` e use o ícone de download.

### 5.4 Se precisar de mais dados

Baixe um **subconjunto estratificado** do `train/` (por `label`, `is_digital` e `type`), por exemplo de 10 a 20 mil imagens. Não baixe o `train/` completo.

### 5.5 Alternativa sem download: Kaggle Notebook

Na aba *Code*, clique em *New Notebook*. Os dados ficam montados em:
```
/kaggle/input/the-freuid-challenge-2026-ijcai-ecai/
```
O Kaggle oferece GPU gratuita (cerca de 30 h por semana; ative em *Settings → Accelerator*). É a opção indicada para treinar com o `train/` completo.

---

## 6. Estrutura do projeto

```
freuid-trabalho/
├── .gitignore            # data/, .venv/, *.pt, kaggle.json
├── FREUID_CONTEXTO.md
├── data/                 # NÃO versionar
│   ├── train_sample/
│   ├── train_sample_labels.csv
│   └── train_labels.csv
├── src/
│   ├── download.py
│   ├── eda.py
│   ├── dataset.py
│   ├── train.py
│   └── metric.py
├── reports/              # gráficos e métricas (sem imagens do dataset)
└── requirements.txt
```

`.gitignore` mínimo:
```
data/
.venv/
*.pt
*.pth
kaggle.json
__pycache__/
```

---

## 7. Metodologia

### 7.1 Validação

O teste da competição mede **generalização fora da distribuição**: tipos de documento novos e mais exemplos recapturados. Para reproduzir isso:
- **Split principal:** separe por `type`, deixando 2 ou 3 tipos de documento totalmente fora do treino (GroupKFold por `type`).
- **Split secundário:** compare o desempenho em `is_digital = 1` e em `is_digital = 0`.
- **Atenção:** há relatos de **shortcut learning**, com métricas internas perto de 100% (AUC ~0,9999) que não generalizam. Se o resultado for bom demais, desconfie e analise.

### 7.2 Baseline sugerido

1. Backbone pré-treinado (EfficientNet ou ConvNeXt via `timm`) com fine-tuning binário.
2. Resolução de 384 a 512 px, porque os artefatos de fraude são finos.
3. Augmentation leve: compressão JPEG, blur e variação de cor. Evite augmentation que destrua artefatos físicos.

### 7.3 Métrica FREUID (menor é melhor)

- **AuDET:** área sob a curva DET, equivalente a `1 − ROC-AUC`.
- **APCER @ 1% BPCER:** taxa de fraudes não detectadas quando apenas 1% dos documentos legítimos é marcado como fraude.

```python
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve

def freuid_score(y_true, y_score):
    auc = roc_auc_score(y_true, y_score)          # g_audet = 1 - AuDET
    fpr, tpr, _ = roc_curve(y_true, y_score)
    tpr_at_1 = tpr[fpr <= 0.01].max()             # 1 - APCER@1%BPCER
    g_audet, g_apcer = auc, tpr_at_1
    if g_audet + g_apcer == 0:
        return 1.0
    return 1 - 2 * g_audet * g_apcer / (g_audet + g_apcer)
```

Reporte também ROC-AUC, APCER@1%BPCER e a matriz de confusão, separando os resultados por `is_digital` e por tipos de documento não vistos no treino.

### 7.4 Ligação com a gestão pública (para o relatório)

- Validação de documentos em cadastros públicos (inscrição em conselhos profissionais, benefícios, concursos).
- Custo assimétrico dos erros: rejeitar um cidadão legítimo (BPCER) tem custo diferente de aceitar uma fraude (APCER). Isso justifica operar com 1% de BPCER.
- Fraudes geradas por IA generativa e por recaptura são ameaças atuais à identidade digital.

---

## 8. Citação

> Ivan Relić, Vincenzo D'Elia, Stefano Bortoli, Radu Tudoran, Hristina Nedyalkova, Mihaela Bošnjak, Stanislav Pavlić, Tin Mavračić, Darin Dašić, Marin Kačan, Jerko Šegvić, Paolo Čerić, Filip Šoprun, Matej Miočić, Marin Oršić, Lorenzo Vaiani, and Paolo Garza. *The FREUID Challenge 2026 - IJCAI-ECAI.* https://www.kaggle.com/competitions/the-freuid-challenge-2026-ijcai-ecai, 2026. Kaggle.

Também inclua: "Dataset FREUID fornecido pelo Microblink Fraud Lab (Microblink LLC), usado sob licença de pesquisa não comercial."

---

## 9. Prompt inicial para o agente do Cursor

```
Leia FREUID_CONTEXTO.md inteiro e siga as regras da seção 3 sem exceção.
1. Crie a estrutura da seção 6 e o .gitignore.
2. Configure o venv e as dependências (seção 4.2) e teste o acesso (4.3).
3. Baixe apenas os CSVs de rótulos (5.1) e faça a EDA (5.2): contagens por label,
   is_digital e type. Salve o resumo em reports/eda.md. Pare e me mostre o resultado.
4. Só depois da minha confirmação, implemente src/download.py (5.3) para o train_sample.
```
