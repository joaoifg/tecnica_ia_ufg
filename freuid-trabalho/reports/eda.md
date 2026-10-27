# EDA FREUID 2026 — rótulos

Gerado automaticamente a partir dos CSVs (sem imagens).

> Dataset: The FREUID Challenge 2026 – IJCAI-ECAI (Microblink Fraud Lab).
> Uso apenas acadêmico; dados não versionados.

## `train_sample_labels.csv` (recorte para começar)

- **Linhas:** 13
- **Colunas:** id, image_path, label, is_digital, type

### Distribuição de `label`

| label | significado | n | % |
|---|---|---:|---:|
| 0 | legítimo (bona-fide) | 10 | 76.9% |
| 1 | fraude (ataque) | 3 | 23.1% |

### Distribuição de `is_digital`

| is_digital | significado | n | % |
|---|---|---:|---:|
| False | recapturado (print-and-capture) | 6 | 46.2% |
| True | totalmente digital | 7 | 53.8% |

### Tipos de documento (`type`) — 5 distintos

| type | n | % |
|---|---:|---:|
| MAURITIUS/ID | 3 | 23.1% |
| MOZAMBIQUE/DL | 3 | 23.1% |
| GUINEA/DL | 3 | 23.1% |
| BENIN/DL | 2 | 15.4% |
| EGYPT/DL | 2 | 15.4% |

### `type` × `label`

| type          |   legítimo |   fraude |   total |
|:--------------|-----------:|---------:|--------:|
| BENIN/DL      |          2 |        0 |       2 |
| EGYPT/DL      |          2 |        0 |       2 |
| GUINEA/DL     |          2 |        1 |       3 |
| MAURITIUS/ID  |          2 |        1 |       3 |
| MOZAMBIQUE/DL |          2 |        1 |       3 |
| All           |         10 |        3 |      13 |

### Taxa de fraude por `is_digital`

| is_digital | n | taxa fraude |
|---|---:|---:|
| False | 6 | 16.7% |
| True | 7 | 28.6% |

## `train_labels.csv` (treino completo)

- **Linhas:** 69,352
- **Colunas:** id, image_path, label, is_digital, type

### Distribuição de `label`

| label | significado | n | % |
|---|---|---:|---:|
| 0 | legítimo (bona-fide) | 40,005 | 57.7% |
| 1 | fraude (ataque) | 29,347 | 42.3% |

### Distribuição de `is_digital`

| is_digital | significado | n | % |
|---|---|---:|---:|
| False | recapturado (print-and-capture) | 20 | 0.0% |
| True | totalmente digital | 69,332 | 100.0% |

### Tipos de documento (`type`) — 5 distintos

| type | n | % |
|---|---:|---:|
| EGYPT/DL | 15,867 | 22.9% |
| GUINEA/DL | 13,389 | 19.3% |
| BENIN/DL | 13,369 | 19.3% |
| MOZAMBIQUE/DL | 13,365 | 19.3% |
| MAURITIUS/ID | 13,362 | 19.3% |

### `type` × `label`

| type          |   legítimo |   fraude |   total |
|:--------------|-----------:|---------:|--------:|
| BENIN/DL      |       8001 |     5368 |   13369 |
| EGYPT/DL      |       8000 |     7867 |   15867 |
| GUINEA/DL     |       8001 |     5388 |   13389 |
| MAURITIUS/ID  |       8002 |     5360 |   13362 |
| MOZAMBIQUE/DL |       8001 |     5364 |   13365 |
| All           |      40005 |    29347 |   69352 |

### Taxa de fraude por `is_digital`

| is_digital | n | taxa fraude |
|---|---:|---:|
| False | 20 | 70.0% |
| True | 69,332 | 42.3% |
