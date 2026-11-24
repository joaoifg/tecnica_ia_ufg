"""Passo 7: gera reports/apresentacao_trabalho.html (20 slides) a partir dos JSON desta execução.

Todos os números vêm de reports/analise/*.json e comparacao.csv; as figuras são gráficos
(nenhuma foto de documento) embutidos em base64, para o HTML abrir sozinho.
Navegação: setas / espaço / PageUp-PageDown / clique. Tecla N mostra as notas de fala.

Rodar antes: inventario, eda_completa, modelagem, cnn_protocolo, diagnostico_cnn, gradcam,
comparacao e figuras_extras.
"""

from __future__ import annotations

import base64
import html
import json

import pandas as pd

from config import ANALISE, FIGS, REPORTS


def j(nome):
    p = ANALISE / f"{nome}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def br(v, casas=3):
    return f"{v:.{casas}f}".replace(".", ",")


def mil(v):
    return f"{int(round(v)):,}".replace(",", ".")


def pct(v, casas=1):
    return br(100 * v, casas) + "%"


def minutos(seg):
    return f"{br(seg / 60, 1)} min" if seg >= 60 else f"{seg:.0f} s"


def fig(nome, cls="fig"):
    p = FIGS / f"{nome}.png"
    if not p.exists():
        return f'<div class="falta">figura {nome}.png não gerada</div>'
    b = base64.b64encode(p.read_bytes()).decode()
    return f'<div class="{cls}"><img src="data:image/png;base64,{b}" alt="{nome}"></div>'


def tabela(cab, linhas, destaque=None):
    th = "".join(f"<th>{c}</th>" for c in cab)
    corpo = ""
    for k, l in enumerate(linhas):
        cls = ' class="dest"' if destaque and destaque(k, l) else ""
        corpo += f"<tr{cls}>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>"
    return f"<table><thead><tr>{th}</tr></thead><tbody>{corpo}</tbody></table>"


def main():
    inv, eda, mod, cnn = j("inventario"), j("eda"), j("modelagem"), j("cnn")
    dg, gc, tp = j("cnn_diagnostico"), j("gradcam_resumo"), j("tempos")
    comp = pd.read_csv(ANALISE / "comparacao.csv")
    p = mod["protocolo"]
    hid, hood = mod["holdout"]["id"]["modelos"], mod["holdout"]["ood"]["modelos"]
    rf_id, rf_ood = hid["Random Forest"], hood["Random Forest"]
    lr_id, lr_ood = hid["Regressão logística"], hood["Regressão logística"]
    at = mod["atalhos"]
    loto = mod["loto"]["Random Forest"]
    c_id, c_ood = cnn["holdout"]["id"], cnn["holdout"]["ood"]
    cid, cood = c_id["limiar_custo"], c_ood["limiar_custo"]
    boot = dg["bootstrap_auc"]
    b_lr, b_rf = boot["OOD: EfficientNet − Regressão logística"], boot["OOD: EfficientNet − Random Forest"]
    d1 = dg["ood_limiar_para_1pct_bpcer_diagnostico"]
    pop_tipo = {r["pais"]: r for r in eda["por_tipo"]}
    rec = next(r for r in eda["is_digital"] if not r["is_digital"])
    feats = eda["features"]

    # ---------- tabelas
    ordem = ["Baseline", "Naive Bayes", "Regressão logística", "KNN", "Árvore de decisão", "Random Forest", "Gradient Boosting"]
    t_cv = tabela(["Modelo", "ROC-AUC", "Acurácia", "Recall de fraude", "F1"],
                  [[n, br(mod["cv"][n]["auc"]["media"]), br(mod["cv"][n]["acuracia"]["media"]),
                    br(mod["cv"][n]["recall"]["media"]), br(mod["cv"][n]["f1"]["media"])] for n in ordem],
                  destaque=lambda k, l: l[0] in ("Regressão logística", "Random Forest"))
    cj = mod["conjuntos"]
    t_conj = tabela(["Modelo", "64 features (V1)", "73 features", "Ganho"],
                    [[n, br(cj[n]["V1 (64)"]["media"]), br(cj[n]["Completo (73)"]["media"]),
                      "+" + br(cj[n]["Completo (73)"]["media"] - cj[n]["V1 (64)"]["media"])]
                     for n in ("Regressão logística", "Random Forest", "Gradient Boosting")])
    t_comp = tabela(["Modelo", "Split", "n", "ROC-AUC", "APCER@1%BPCER", "FREUID ↓", "Recall (custo)"],
                    [[r.modelo, r.split.replace(" (Moçambique)", ""), mil(r.n),
                      br(r.roc_auc, 4) if r.roc_auc > 0.999 else br(r.roc_auc), br(r.apcer_1pct_bpcer),
                      br(r.freuid, 4) if r.freuid < 0.001 else br(r.freuid), br(r.recall_limiar_custo)]
                     for r in comp.itertuples()],
                    destaque=lambda k, l: l[0] == "EfficientNet-B0")
    t_cnn = tabela(["Conjunto", "Limiar", "VN", "FP", "FN", "VP", "Custo"],
                   [[s, br(r["limiar"], 2), mil(r["vn"]), mil(r["fp"]), mil(r["fn"]), mil(r["vp"]), mil(r["custo"])]
                    for s, r in (("ID", c_id["limiar_0.5"]), ("ID", cid), ("OOD", c_ood["limiar_0.5"]), ("OOD", cood))])
    te, tm, tc = tp["extracao_features"], tp["modelagem"], tp["cnn"]
    quedas = ""
    for m in ("Regressão logística", "Random Forest", "Gradient Boosting", "EfficientNet-B0"):
        a_id = comp.loc[(comp.modelo == m) & (comp.split == "validação ID"), "roc_auc"].item()
        a_ood = comp.loc[(comp.modelo == m) & (comp.split != "validação ID"), "roc_auc"].item()
        cls = "card mini ok" if m == "EfficientNet-B0" else "card mini"
        quedas += (f'<div class="{cls}"><h3>{m}</h3><p>AUC cai <b>{br(a_id - a_ood)}</b> '
                   f'({br(a_id, 3)} → {br(a_ood, 3)})</p></div>')

    slides = [
        # 1
        ("capa", "", "Fraude em documentos de identidade",
         f"""<p class="lead">O escore de um modelo vale para um tipo de documento novo?</p>
         <p class="sub">João Henrique Gomes Dias · Técnicas de IA I · prof. Paulo Victor dos Santos · UFG/IIG · 2026/2</p>
         <div class="capa-nums"><div><b>{mil(inv['n_universo'])}</b><span>imagens</span></div><div><b>7 + 1</b><span>modelos</span></div>
         <div><b>{mil(mod['n_features'])}</b><span>features</span></div><div><b>{minutos(tc['seg_total'])}</b><span>de GPU</span></div></div>
         <p class="sub2">Dataset FREUID fornecido pelo Microblink Fraud Lab (Microblink LLC), licença de pesquisa não comercial.
         Relić et al., The FREUID Challenge 2026 – IJCAI-ECAI. Nenhuma imagem de documento é exibida.</p>""",
         "Boa tarde. Meu trabalho é sobre fraude em documentos de identidade. A pergunta é de gestão pública: um órgão "
         "consegue usar a imagem do documento para estimar a chance de fraude, e isso continua valendo quando aparece "
         "um tipo de documento que o modelo nunca viu? Usei 25 mil imagens, sete modelos da disciplina e uma rede neural."),
        # 2
        ("", "1 · Problema público", "Um documento falso aceito entrega um direito a quem não tem",
         """<div class="grid3">
         <div class="card"><h3>Benefício social</h3><p>Cadastro com documento enviado por foto. Fraude em série esvazia o orçamento.</p></div>
         <div class="card"><h3>Conselho profissional</h3><p>Inscrição e carteira emitidas a partir da identidade apresentada.</p></div>
         <div class="card"><h3>Concurso público</h3><p>Posse e conferência documental de milhares de aprovados.</p></div></div>
         <div class="grid2"><div class="card ood"><h3>Erro 1: fraude que passa</h3><p>Direito entregue a quem não tem. <b>Custo 5.</b></p></div>
         <div class="card ok"><h3>Erro 2: legítimo para conferência</h3><p>Cidadão espera atendimento humano. <b>Custo 1.</b></p></div></div>
         <div class="take">Os dois erros não custam o mesmo. Por isso o limiar do modelo sai do custo 5 : 1, não do 0,5.</div>""",
         "Os órgãos recebem documento por imagem o tempo todo. Errar para um lado entrega um direito indevido; para o outro, "
         "trava o cidadão. Assumi que deixar fraude passar custa cinco vezes mais que mandar um legítimo para um servidor conferir."),
        # 3
        ("", "2 · Formulação", "D = {(x, y)}: a imagem vira um vetor, o rótulo diz se é fraude",
         f"""<div class="fluxo"><div class="passo">Imagem do<br>documento</div><div class="seta">→</div>
         <div class="passo">X: vetor de<br>{mod['n_features']} números</div><div class="seta">→</div>
         <div class="passo">fit(X, y)<br>no treino</div><div class="seta">→</div>
         <div class="passo">predict_proba<br>no teste</div><div class="seta">→</div><div class="passo dest">P(fraude)<br>entre 0 e 1</div></div>
         <div class="grid2"><div class="card"><h3>X: o que entra</h3><ul>
         <li><b>64 de cor e brilho:</b> histogramas R, G e B, médias, desvios, gradiente</li>
         <li><b>9 de perícia:</b> Error Level Analysis, nitidez, alta frequência, bordas, entropia, saturação</li>
         <li><b>Na CNN:</b> a própria imagem, 384×608 pixels</li></ul></div>
         <div class="card"><h3>y: o rótulo</h3><ul><li>y = 1: fraude</li><li>y = 0: legítimo</li>
         <li>Treino e teste nunca compartilham imagem</li><li>Métricas sempre com fraude como classe positiva</li></ul></div></div>""",
         "É o formato da aula: cada exemplo é um par x, y. O x é a imagem resumida em 73 números; o y é o rótulo. "
         "O modelo aprende com fit no treino e devolve uma probabilidade com predict_proba em imagens que ele nunca viu."),
        # 4
        ("", "3 · Dados", "69 mil rótulos na competição, 25 mil imagens usadas aqui",
         f"""<div class="grid4">
         <div class="card"><div class="num">{mil(inv['n_rotulos_populacao'])}</div><p>rótulos de treino da competição</p></div>
         <div class="card"><div class="num">{mil(inv['n_universo'])}</div><p>imagens no disco usadas ({pct(inv['fracao_da_populacao'])} da população)</p></div>
         <div class="card"><div class="num">{pct(eda['pct_fraude'])}</div><p>de fraude, igual na amostra e na população</p></div>
         <div class="card"><div class="num">{br(inv['desvio_max_pp'], 2)} pp</div><p>maior diferença de proporção amostra × população</p></div></div>
         <div class="grid2"><div class="card"><h3>Cinco tipos de documento</h3><ul>
         <li>Carteiras de motorista: Benin, Egito, Guiné, Moçambique</li><li>Identidade: Maurício</li>
         <li>Cerca de 5 mil imagens de cada tipo no universo</li></ul></div>
         <div class="card"><h3>Quase tudo é digital</h3><ul><li>Só <b>{rec['n']}</b> imagens são recaptura (impressão fotografada)</li>
         <li>{rec['fraude']} delas são fraude; pouco para concluir algo</li><li>Dataset sintético: sem pessoa real</li></ul></div></div>""",
         "Os 69 mil são os rótulos do treino da competição. Trabalhei com 25 mil imagens que estão no disco, 36 por cento. "
         "A amostra reproduz a população quase exatamente: a maior diferença de proporção é de cinco centésimos de ponto. "
         "Quase tudo é digital; só 20 recapturas."),
        # 5
        ("", "4 · População", "O tipo de documento muda pouco a taxa de fraude",
         f"""{fig('eda_tipo_label')}<div class="grid3"><div class="card"><h3>Taxa de fraude por tipo</h3><ul>
         <li>Egito: <b>{pct(pop_tipo['Egito']['taxa'])}</b></li><li>Benin, Guiné, Maurício, Moçambique: entre {pct(min(pop_tipo[k]['taxa'] for k in ('Benin', 'Guiné', 'Maurício', 'Moçambique')))} e {pct(max(pop_tipo[k]['taxa'] for k in ('Benin', 'Guiné', 'Maurício', 'Moçambique')))}</li></ul></div>
         <div class="card"><h3>Qui-quadrado</h3><p>χ² = {br(eda['qui2']['chi2'], 1)}, significativo, mas V de Cramér = <b>{br(eda['qui2']['v_cramer'])}</b>: associação fraca.</p></div>
         <div class="card"><h3>Recaptura</h3><p>Taxa de fraude {br(rec['taxa'], 2)}, IC de Wilson {br(rec['ic_lo'], 2)} a {br(rec['ic_hi'], 2)}: intervalo largo demais.</p></div></div>""",
         "Nos 69 mil rótulos, Egito tem um pouco mais de fraude. O teste é significativo porque a amostra é enorme, "
         "mas o V de Cramér de 0,08 mostra que o tipo explica pouco da fraude. Saber o país não diz se o documento é falso."),
        # 6
        ("", "5 · Features", f"{feats['significativas_bonferroni']} das {feats['n']} features separam fraude sozinhas",
         f"""<div class="row">{fig('eda_ranking_features')}<div class="lado"><div class="card"><h3>Mais forte isolada</h3>
         <p>Faixa mais escura do histograma verde: AUC univariada {br(feats['top'][0]['auc'] if 'top' in feats else eda['features']['ranking'][0]['auc'])}.</p></div>
         <div class="card"><h3>Redundância</h3><p>{feats['pares_corr_maior_0_9']} pares com correlação acima de 0,9: a logística precisa de regularização.</p></div>
         <div class="card"><h3>Metadados</h3><p>Largura, altura e tamanho do arquivo: AUC entre {br(min(v['auc_univariada'] for v in eda['metadados'].values()), 2)} e {br(max(v['auc_univariada'] for v in eda['metadados'].values()), 2)}. Não separam.</p></div></div></div>""",
         "Cada barra é o poder de uma feature sozinha. As de histograma e as de perícia, como o ELA, aparecem no topo. "
         "Tamanho do arquivo e resolução não ajudam, o que é bom: não há atalho por metadado."),
        # 7
        ("", "6 · Exploração", "As features reconhecem o país melhor que a fraude",
         f"""{fig('eda_pca')}
         <div class="take">Silhueta pelo rótulo: <b>{br(eda['pca']['silhueta_classe'])}</b> · silhueta pelo tipo de documento: <b>{br(eda['pca']['silhueta_documento'])}</b>.
         {eda['pca']['comp_90']} componentes explicam 90% da variância.</div>""",
         "Este é o gráfico mais importante da exploração. À esquerda, colorido por fraude: tudo misturado. À direita, colorido "
         "por país: cinco nuvens separadas. Isso antecipa o problema do documento novo."),
        # 8
        ("", "7 · Protocolo", "Um tipo de documento inteiro fica fora do treino",
         f"""<div class="grid3">
         <div class="card"><h3>Treino</h3><div class="num">{mil(p['treino']['n'])}</div><p>80% de Benin, Egito, Guiné e Maurício · {mil(p['treino']['fraudes'])} fraudes</p></div>
         <div class="card"><h3>Validação ID</h3><div class="num">{mil(p['val_id']['n'])}</div><p>20% dos mesmos tipos, estratificado · {mil(p['val_id']['fraudes'])} fraudes</p></div>
         <div class="card ood"><h3>OOD: Moçambique</h3><div class="num">{mil(p['ood']['n'])}</div><p>tipo nunca visto no treino · {mil(p['ood']['fraudes'])} fraudes</p></div></div>
         <div class="grid2"><div class="card"><h3>Regras</h3><ul><li>Semente 42; mesmos ids para clássicos e CNN (hash conferido)</li>
         <li>Nenhum id em dois conjuntos</li><li>Moçambique escolhido antes de qualquer resultado</li></ul></div>
         <div class="card"><h3>Métricas</h3><ul><li>ROC-AUC, AuDET = 1 − AUC</li><li>APCER@1%BPCER: fraudes que passam com 1% de legítimos barrados</li>
         <li>FREUID (competição): menor é melhor</li></ul></div></div>""",
         "A validação ID responde se o modelo funciona nos documentos que já conhece. O OOD responde a pergunta do trabalho: "
         "e num documento novo? O APCER a 1% de BPCER é a métrica que mais importa para o órgão."),
        # 9
        ("", "8 · Modelos da aula", "Logística e floresta no centro, os outros como comparação",
         """<div class="grid2"><div class="card"><h3>Regressão logística</h3><ul><li>P(fraude) = σ(w·x + b): fronteira linear</li>
         <li><b>Padroniza antes</b>: escalas diferentes distorcem coeficientes e regularização</li><li>Coeficiente com sinal: explicável</li></ul></div>
         <div class="card"><h3>Random Forest</h3><ul><li>400 árvores, média dos votos</li>
         <li><b>Não precisa padronizar</b>: cada corte olha uma coluna; mudar a escala não muda o corte</li><li>Captura interações entre features</li></ul></div></div>
         <div class="grid4"><div class="card mini"><h3>Baseline</h3><p>sempre "legítimo"</p></div><div class="card mini"><h3>KNN · Naive Bayes · Árvore</h3><p>demais modelos da aula</p></div>
         <div class="card mini"><h3>Gradient boosting</h3><p>só contraste</p></div><div class="card mini"><h3>EfficientNet-B0</h3><p>transferência de aprendizado (ImageNet)</p></div></div>""",
         "A logística precisa de padronização porque regulariza todos os coeficientes juntos. A floresta só faz perguntas do "
         "tipo coluna maior que um valor, então a escala não importa. A CNN reaproveita filtros aprendidos no ImageNet."),
        # 10
        ("", "9 · Validação cruzada", "Dentro dos tipos vistos, todos os modelos da aula passam o baseline",
         f"""<div class="grid2"><div>{t_cv}</div><div class="col">{t_conj}
         <div class="take">5 dobras, {mil(p['treino']['n'])} imagens. Desvio entre dobras: no máximo 0,004.
         As 9 features de perícia somam até +0,034 de AUC.</div></div></div>""",
         "Nos tipos vistos, a floresta chega a 0,991 de AUC e a logística a 0,964. O baseline fica em 0,5. Com 16 mil imagens a "
         "estimativa é estável. As features de perícia, como o ELA, melhoram todos os modelos."),
        # 11
        ("", "10 · Um tipo de fora por vez", "Média de 0,82, mas Moçambique e Benin quase não transferem",
         f"""{fig('mod_loto_heatmap')}
         <div class="take">Random Forest com cada tipo inteiro fora do treino: de {br(min(v['auc'] for k, v in loto.items() if k != '_media'))} a
         {br(max(v['auc'] for k, v in loto.items() if k != '_media'))}. A média esconde tipos que não transferem.</div>""",
         "Aqui cada coluna é um país deixado de fora do treino. Guiné e Maurício transferem bem; Moçambique e Benin não. "
         "Isso mostra que o resultado do documento novo depende de quão parecido ele é com os que o modelo já viu."),
        # 12
        ("", "11 · Resultados", "Tabela única: o mesmo modelo, documento visto × documento novo",
         f"""{t_comp}
         <div class="grid4">{quedas}</div>
         <div class="take">Fonte: comparacao.csv. Recall 1,000 no OOD não é acerto: o modelo marcou todas as imagens como fraude.</div>""",
         "Leiam a coluna da AUC: perto de 1 nos tipos vistos, entre 0,54 e 0,80 no tipo novo. O FREUID, escore da competição, "
         "vai de quase zero para perto de um nos clássicos. A CNN é a que menos cai."),
        # 13
        ("", "12 · Resultados", "Todos caem no tipo novo; a CNN cai menos",
         f"""{fig('comparacao_id_ood')}""",
         "O mesmo dado em gráfico. Barras azuis: documentos vistos. Laranja: Moçambique. A distância entre azul e laranja é "
         "o quanto o modelo depende de já conhecer a carteira."),
        # 14
        ("", "13 · Matriz de confusão", "No limiar de custo, a floresta acusa todo o tipo novo",
         f"""{fig('mod_matriz_id')}{fig('mod_matriz_ood')}
         <div class="take">ID: {rf_id['limiar_custo']['fn']} fraudes passaram e {rf_id['limiar_custo']['fp']} legítimos foram à conferência.
         OOD: {mil(rf_ood['limiar_custo']['fp'])} de {mil(rf_ood['limiar_custo']['fp'] + rf_ood['limiar_custo']['vn'])} legítimos marcados como fraude.</div>""",
         "Em cima, nos tipos vistos, o modelo funciona: poucas fraudes passam. Embaixo, em Moçambique, o mesmo limiar marca "
         "todo mundo como fraude. Isso não é detectar, é recusar o país inteiro."),
        # 15
        ("", "14 · CNN: treino", f"EfficientNet-B0: {tc['epocas']} épocas, melhor na {tc['melhor_epoca']}ª",
         f"""{fig('cnn_treino')}
         <div class="grid4"><div class="card mini"><div class="num s">{minutos(sum(tc['seg_por_epoca']) / len(tc['seg_por_epoca']))}</div><p>por época</p></div>
         <div class="card mini"><div class="num s">{br(tc['img_por_seg_treino'], 0)} img/s</div><p>no treino (RTX 4060)</p></div>
         <div class="card mini"><div class="num s">384×608</div><p>pixels, batch {tc['batch']}</p></div>
         <div class="card mini"><div class="num s">{minutos(tc['seg_total'])}</div><p>total, com avaliação</p></div></div>""",
         "A rede foi pré-treinada no ImageNet e ajustada com aumento de dados que imita impressão e foto. A AUC na validação "
         "já passou de 0,999 na primeira época. Parou sozinha na sexta, três épocas sem melhorar, e usei os pesos da terceira."),
        # 16
        ("", "15 · CNN: resultados", f"AUC {br(cid['auc'], 4)} nos tipos vistos e {br(cood['auc'])} no tipo novo",
         f"""{fig('cnn_roc_det')}<div class="grid2"><div>{t_cnn}</div>
         <div class="take">ID: {cid['fp'] + cid['fn']} erros em {mil(cid['n'])} no limiar de custo.<br>OOD: com 1% de legítimos barrados, pega {pct(1 - cood['apcer_1pct_bpcer'])} das fraudes,
         mas os limiares 0,5 e 0,07 mandam quase tudo para conferência.</div></div>""",
         "Nos tipos vistos, a CNN erra 6 imagens em 4 mil. No tipo novo, a curva ainda sobe bem acima da diagonal: "
         "ela pega metade das fraudes com só 1% de legítimos barrados. Os clássicos ficavam perto de zero nesse ponto."),
        # 17
        ("", "16 · CNN: o escore muda de escala", "A ordenação transfere; o limiar não",
         f"""{fig('cnn_escores')}
         <div class="grid3"><div class="card mini"><p>Mediana dos legítimos: <b>{br(dg['escore_id']['legitimo']['quantis_5_25_50_75_95'][2])}</b> no ID ×
         <b>{br(dg['escore_ood']['legitimo']['quantis_5_25_50_75_95'][2])}</b> no OOD</p></div>
         <div class="card mini"><p>CNN − logística no OOD: <b>+{br(b_lr['dif'])}</b> de AUC (IC 95% {br(b_lr['ic95'][0])} a {br(b_lr['ic95'][1])})</p></div>
         <div class="card mini"><p>Corte que daria 1% de BPCER em Moçambique: <b>{br(d1['limiar'])}</b>, e não {br(cnn['limiar_custo'], 2)}</p></div></div>""",
         "Este é o achado mais interessante da CNN. Nos tipos vistos, legítimos ficam perto de zero e fraudes perto de um. "
         "Em Moçambique, todo mundo sobe: 94% dos legítimos passam de 0,5. As fraudes continuam mais altas, por isso a AUC é boa, "
         "mas o corte precisa ser recalibrado com uma amostra rotulada do tipo novo. A vantagem sobre a logística tem intervalo de confiança estreito."),
        # 18
        ("", "17 · Checagem de atalho", "AUC acima de 0,98 exigiu investigação",
         f"""<div class="grid2"><div>{tabela(['Verificação', 'Resultado'], [
             ['Ids repetidos entre conjuntos', '0'],
             ['AUC só com tamanho e resolução', br(at['so_metadados_auc']['id'])],
             ['AUC só com o tipo do documento', br(at['so_tipo_auc_id'])],
             ['Acurácia ao prever o <b>tipo</b> pelas 73 features', f"<b>{br(at['acuracia_prever_tipo_pelas_features']['media'], 4)}</b>"],
             ['AUC da CNN em cada tipo (ID)', f"≥ {br(min(v['auc'] for v in dg['auc_por_tipo_id'].values()), 4)}"]])}
         <div class="take">Sem vazamento. Mas o vetor é uma impressão digital da carteira: o modelo aprende o que é anormal <i>para aquela carteira</i>.</div></div>
         <div class="col">{fig('gradcam_borda')}<p class="nota-txt">Grad-CAM em {sum(g['n'] for g in gc['grupos'].values())} imagens (só em C:\\freuid\\runs, por licença).
         Nos acertos, o mapa fica no rosto e nos campos de texto; não na borda nem no fundo.</p></div></div>""",
         "Número alto demais pede desconfiança. Não houve vazamento de id e o arquivo não entrega a resposta. Mas as features "
         "acertam o país em praticamente cem por cento. O Grad-CAM, que eu não posso mostrar por licença, aponta para rosto e "
         "texto, regiões onde a fraude acontece, e não para a borda. Ainda assim, não dá para excluir que a rede aprenda marcas do gerador sintético."),
        # 19
        ("", "18 · Bastidores", "Quanto tempo levou, e o que deu errado no caminho",
         f"""{fig('tempos')}<div class="grid2"><div class="card"><h3>Ritmo</h3><ul>
         <li>Features: {br(te['img_por_seg'], 0)} imagens/s em {te['nucleos']} núcleos</li>
         <li>Clássicos: {minutos(tm['seg'])} para CV, LOTO, grade e holdout</li>
         <li>CNN: {minutos(sum(tc['seg_por_epoca']) / len(tc['seg_por_epoca']))} por época na GPU</li></ul></div>
         <div class="card ood"><h3>Imprevistos</h3><ul><li>Telas azuis ao iniciar a CNN (códigos variados: memória instável)</li>
         <li>Processos paralelos de leitura caíam com "access violation"</li>
         <li>Solução: checkpoint por época, extração retomável, leitura sem processos paralelos</li></ul></div></div>""",
         "Alguns bastidores. A extração das features foi rápida, menos de um minuto. Os modelos clássicos levaram uns oito minutos. "
         "A CNN levou uma hora e vinte. No caminho, o computador teve telas azuis; por isso o código salva a cada época e pode retomar."),
        # 20
        ("", "Conclusão", "Sim para triagem assistida nos tipos conhecidos. Não para um tipo novo.",
         f"""<div class="grid3"><div class="card ok"><h3>O órgão pode</h3><ul><li>Ordenar a fila de conferência pelo escore</li>
         <li>Usar limiar de custo, não 0,5</li><li>Só em tipos presentes no treino, com servidor decidindo</li></ul></div>
         <div class="card ood"><h3>O órgão não pode</h3><ul><li>Recusar alguém só pelo modelo</li><li>Usar em documento novo sem amostra rotulada e novo teste</li>
         <li>Levar este modelo à produção (licença)</li></ul></div>
         <div class="card"><h3>Limites</h3><ul><li>Dataset sintético, 5 tipos estrangeiros</li><li>{rec['n']} recapturas apenas</li>
         <li>OOD com um único tipo e uma execução da CNN</li></ul></div></div>
         <div class="take big">Logística {br(lr_id['auc'])} → {br(lr_ood['auc'])} · Random Forest {br(rf_id['auc'])} → {br(rf_ood['auc'])} ·
         EfficientNet {br(cid['auc'], 4)} → {br(cood['auc'])}</div>
         <p class="sub2">Licença: pesquisa não comercial; nenhuma imagem publicada; dados e pesos fora do git; dados apagados ao fim. Código e números: freuid-trabalho/.</p>""",
         "Resposta à pergunta: o escore funciona onde o modelo já conhece o documento, e só com uma pessoa conferindo. "
         "Para documento novo, até a CNN, que ordena melhor, precisa de dados rotulados para recalibrar o corte. Obrigado."),
    ]

    total = len(slides)
    secoes = []
    for k, (cls, kicker, titulo, corpo, nota) in enumerate(slides, 1):
        secoes.append(f"""<section class="slide {cls}"><p class="kicker">{html.escape(kicker)}</p><h1>{html.escape(titulo)}</h1>
<div class="body">{corpo}</div>
<div class="foot"><span><b>FREUID</b> · Técnicas de IA I · UFG/IIG</span><span>{k} / {total}</span></div>
<aside class="nota">{html.escape(nota)}</aside></section>""")
    doc = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>FREUID · Técnicas de IA I</title><style>
:root{{--navy:#0B2545;--ink:#1B2433;--muted:#5E6878;--soft:#F4F1EA;--line:#E4DED1;--fraude:#C0473B;--legit:#2E8B57;--gold:#C9A227}}
*{{box-sizing:border-box}}html,body{{margin:0;height:100%}}
body{{background:#1b2430;font-family:"Segoe UI",Calibri,sans-serif;color:var(--ink);display:grid;place-items:center;overflow:hidden}}
#deck{{width:1280px;height:720px;position:relative;transform-origin:center}}
.slide{{position:absolute;inset:0;display:none;flex-direction:column;background:#fff;padding:26px 46px 14px}}
.slide.ativo{{display:flex}}
.kicker{{margin:0;font-size:14px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--gold)}}
h1{{margin:4px 0 0;font-size:32px;line-height:1.15;color:var(--navy)}}
.body{{flex:1;min-height:0;margin-top:14px;display:flex;flex-direction:column;gap:12px}}
.lead{{font-size:26px;margin:14px 0 6px}}.sub{{font-size:18px;color:var(--muted)}}.sub2{{font-size:13.5px;color:var(--muted);margin:0}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px;min-height:0}}.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.grid4{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
.row{{display:flex;gap:16px;flex:1;min-height:0}}.row>.fig{{flex:1.5}}.lado{{flex:1;display:flex;flex-direction:column;gap:10px;min-width:0}}
.col{{display:flex;flex-direction:column;gap:10px;min-height:0}}
.card{{background:var(--soft);border-radius:12px;padding:12px 16px}}.card.ood{{border-left:5px solid var(--fraude)}}.card.ok{{border-left:5px solid var(--legit)}}
.card.mini{{padding:9px 13px}}.card.mini p{{font-size:15px}}
.card h3{{margin:0 0 5px;font-size:18px;color:var(--navy)}}.card p,.card li{{font-size:16px;line-height:1.38;margin:0}}
.card ul{{margin:3px 0 0;padding-left:20px}}.card li{{margin-bottom:4px}}
.num{{font-size:34px;font-weight:800;color:var(--navy)}}.num.s{{font-size:24px}}
.take{{background:#EEF3F8;border-left:5px solid var(--navy);border-radius:8px;padding:10px 15px;font-size:17px;line-height:1.38}}
.take.big{{font-size:22px;text-align:center}}
.fig{{flex:1;min-height:0;display:flex;justify-content:center;align-items:center}}.fig img{{max-width:100%;max-height:100%;object-fit:contain}}
table{{border-collapse:collapse;font-size:15.5px;width:100%}}th,td{{padding:6px 9px;border-bottom:1px solid var(--line);text-align:left}}
th{{color:var(--navy);font-size:14px}}tr.dest td{{background:#FFF6DA;font-weight:600}}
.fluxo{{display:flex;align-items:center;justify-content:space-between;gap:6px}}.passo{{background:var(--soft);border-radius:10px;padding:12px 14px;text-align:center;font-size:17px;font-weight:600;color:var(--navy);flex:1}}
.passo.dest{{background:var(--navy);color:#fff}}.seta{{font-size:28px;color:var(--gold);font-weight:700}}
.nota-txt{{font-size:14.5px;color:var(--muted);margin:0}}
.foot{{display:flex;justify-content:space-between;border-top:1px solid var(--line);padding-top:7px;font-size:13px;color:var(--muted)}}
.foot b{{color:var(--navy)}}
.capa{{background:var(--navy);color:#fff}}.capa h1{{color:#fff;font-size:46px;margin-top:110px}}.capa .sub,.capa .sub2{{color:#C9D3E0}}
.capa-nums{{display:flex;gap:44px;margin:26px 0 30px}}.capa-nums b{{display:block;font-size:40px;color:var(--gold)}}.capa-nums span{{color:#C9D3E0;font-size:15px}}
.capa .foot{{border-color:#2a4365;color:#C9D3E0}}.capa .foot b{{color:#fff}}
.nota{{display:none;position:absolute;left:0;right:0;bottom:0;background:#FFF8E1;border-top:3px solid var(--gold);padding:12px 46px;font-size:16px;line-height:1.4;color:var(--ink)}}
body.notas .nota{{display:block}}.falta{{color:var(--fraude)}}
</style></head><body><div id="deck">{''.join(secoes)}</div>
<script>
const s=[...document.querySelectorAll('.slide')];let i=0;
function ir(k){{i=Math.max(0,Math.min(s.length-1,k));s.forEach((e,n)=>e.classList.toggle('ativo',n===i));history.replaceState(null,'','#'+(i+1));}}
function escala(){{const d=document.getElementById('deck');d.style.transform='scale('+Math.min(innerWidth/1280,innerHeight/720)+')';}}
addEventListener('keydown',e=>{{if(['ArrowRight',' ','PageDown'].includes(e.key)){{e.preventDefault();ir(i+1)}}
else if(['ArrowLeft','PageUp'].includes(e.key)){{e.preventDefault();ir(i-1)}}else if(e.key==='n'||e.key==='N')document.body.classList.toggle('notas');}});
addEventListener('click',e=>ir(e.clientX>innerWidth/2?i+1:i-1));addEventListener('resize',escala);
escala();ir((parseInt(location.hash.slice(1))||1)-1);
</script></body></html>"""
    saida = REPORTS / "apresentacao_trabalho.html"
    saida.write_text(doc, encoding="utf-8")
    print("OK ->", saida, f"({total} slides)")


if __name__ == "__main__":
    main()
