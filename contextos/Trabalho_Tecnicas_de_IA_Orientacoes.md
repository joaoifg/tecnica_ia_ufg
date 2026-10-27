# Trabalho de Técnicas de IA I — alinhado ao que o professor pediu

**Aluno:** João Henrique Gomes Dias · UFG / IIG  
**Prazo da apresentação:** terça (hoje) — validar dataset e orientar  
**Escopo:** conceitos da aula (classificação, X/Y, reg. logística, Random Forest). **Não** precisa subir no Kaggle.

---

## Os 4 itens (quadro / fala do professor)

1. **Dataset** — Kaggle ligado à administração pública  
2. **Serve para IA?** — precisa ter dados **X** e rótulos **Y** → `D = {(x, y)}`  
   (exemplo dele: fraude → coluna “é fraude? sim/não”)  
3. **Quais técnicas de IA?** — quais modelos e por quê  
4. **Artigo** — **explicar tudo o que foi desenvolvido**

Entrega de terça: **apresentaçãozinha** com esses pontos (+ processo e resultado).

---

## Nossa resposta

| Item | Resposta |
|---|---|
| Dataset | FREUID 2026 — fraude em documentos de identidade |
| Serve? | **Sim.** X = imagem/features · Y = `label` 0/1 |
| Técnicas | Regressão logística + Random Forest (aulas) |
| Artigo | Intro → métodos → resultados → discussão (tudo o que o código fez) |

**Slides para hoje:**  
`freuid-trabalho/reports/apresentacao_FREUID.html`  
(abrir no Chrome/Edge · setas ou espaço)

**Resultados já rodados:** AUC 0,89 (reg. logística) no teste com tipos vistos · `reports/results.md`

---

## Checklist apresentação
- [x] Dataset escolhido e justificado (gestão pública)
- [x] Fórmula X/Y explicada
- [x] Técnicas da aula
- [x] Estratégia do artigo
- [x] Processo + resultado nos slides
- [ ] Apresentar e anotar orientação (formato do artigo etc.)
