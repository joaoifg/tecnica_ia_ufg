# Detecção de fraude em documentos de identidade (FREUID)
## Técnicas de IA I — UFG / IIG · João Henrique Gomes Dias

---

### 1. Problema (administração pública)
Documentos de identidade entram em cadastros públicos: conselhos profissionais, benefícios, concursos, emissão de carteiras.
Fraudes atuais: manipulação física, edição por IA generativa e *print-and-capture*.
**Objetivo:** classificar automaticamente documento **legítimo** vs **fraudado** e apoiar a validação cadastral.

---

### 2. Dataset — serve para IA?
**The FREUID Challenge 2026 – IJCAI-ECAI** (Microblink Fraud Lab / Kaggle)

| | |
|---|---|
| Amostras de treino | 69.352 imagens sintéticas |
| **X** | pixels da imagem do documento |
| **Y** | `label` ∈ {0 legítimo, 1 fraude} |
| Metadados | `is_digital`, `type` (país/tipo) |

Fórmula: **D = {(x, y)}** → aprendizado supervisionado, classificação binária.
Dados sintéticos → sem dado pessoal real (LGPD menos crítica); licença só para pesquisa.

---

### 3. EDA (rótulos)
- Classes: **57,7%** legítimo · **42,3%** fraude
- 5 tipos: Egito/DL, Guiné/DL, Benin/DL, Moçambique/DL, Maurício/ID
- Quase tudo digital; só **20** recapturados no treino → generalizar print-and-capture é difícil
- `train_sample` oficial tem só **13** imagens → usamos subset estratificado do `train/`

---

### 4. Técnicas de IA
| Modelo | Papel |
|---|---|
| Regressão logística | Baseline linear (aulas) |
| Random Forest | Baseline clássico não-linear |
| CNN (EfficientNet-B0) | Modelo principal — transfer learning (Kaggle GPU) |

**Validação:** deixar 1 tipo de documento fora do treino (teste OOD) + métricas ID.
**Métricas:** ROC-AUC, **APCER @ 1% BPCER**, score FREUID (menor = melhor), matriz de confusão.
Prioridade: não deixar passar fraude (APCER) sem rejeitar demais cidadãos (BPCER).

---

### 5. Artigo — estrutura
1. Introdução (identidade digital pública)
2. Referencial (biometria documental, GANs, RF, CNN, LGPD/ética)
3. Materiais e métodos (dataset, EDA, splits, modelos)
4. Resultados (tabelas + curvas; **sem publicar imagens** do dataset)
5. Discussão (gestão pública, viés, limitações, licença)
6. Conclusão + trabalhos futuros
Anexo: código/notebook reproduzível

---

### 6. Perguntas ao professor
1. CNN / transfer learning é aceito além dos modelos clássicos da disciplina?
2. Há modelo de formatação do artigo (SBC, ABNT…)? Qual o prazo final?
3. Posso usar competição encerrada (late submission) só como fonte de dataset acadêmico?

---

### Citação
Relić et al. *The FREUID Challenge 2026 - IJCAI-ECAI.* Kaggle, 2026. Dataset Microblink Fraud Lab — uso não comercial de pesquisa.
