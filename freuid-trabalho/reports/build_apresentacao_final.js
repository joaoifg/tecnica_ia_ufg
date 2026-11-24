const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = "c:/Users/style/OneDrive/tecnica_ia_ufg/freuid-trabalho/reports";
const OUT = path.join(ROOT, "apresentacao_FREUID_final.pptx");
const APPLY = "C:/Users/style/.claude/skills/synced/6aeb86cb-6193-4178-8d49-e84e4d2bc47d_5ef7ce20-2893-437c-b2c8-0d9bb07e9a7c/pptx/scripts/apply_theme.js";

const THEME = {
  name: "FREUID Codigo",
  colors: {
    dk1: "0D3B66",
    lt1: "FFFFFF",
    dk2: "3E4E60",
    lt2: "F4F7FB",
    accent1: "0B2F4A",
    accent2: "C4A046",
    accent3: "C0473B",
    accent4: "2C6EAF",
    accent5: "1F7A4D",
    accent6: "C47B2B",
    hlink: "164E82",
    folHlink: "8A6A12",
  },
};

const pres = new pptxgen();
pres.defineLayout({ name: "WIDE", width: 13.333, height: 7.5 });
pres.layout = "WIDE";
pres.theme = { headFontFace: "Cambria", bodyFontFace: "Calibri" };
pres.title = "FREUID 2026 — O código do trabalho final";
pres.author = "João Henrique Gomes Dias, Tiago e Micaela";
pres.subject = "Técnicas de IA I — UFG IIG";
pres.company = "UFG IIG";

const C = pres.SchemeColor;

function fill(color) {
  return { color };
}
function tx(slide, text, opts) {
  slide.addText(text, Object.assign({
    isTextBox: true,
    margin: 0,
    fontSize: 16,
    color: C.text1,
    valign: "top",
    wrap: true,
  }, opts));
}
function kicker(slide, text) {
  tx(slide, text.toUpperCase(), {
    x: 0.5, y: 0.14, w: 12.3, h: 0.24,
    fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.1,
  });
}
function title(slide, text) {
  slide.addText(text, { placeholder: "title" });
}

pres.defineSlideMaster({
  title: "Capa",
  background: { color: C.accent1 },
  objects: [],
  slideNumber: { x: 12.3, y: 7.12, w: 0.55, h: 0.26, fontSize: 12, color: "C4A046", margin: 0 },
});
pres.defineSlideMaster({
  title: "Conteudo",
  background: { color: C.background1 },
  objects: [
    {
      placeholder: {
        options: {
          name: "title", type: "title",
          x: 0.5, y: 0.36, w: 12.3, h: 0.58,
          fontSize: 30, bold: true, color: C.text1,
          margin: 0, valign: "middle", align: "left",
        },
        text: "",
      },
    },
  ],
  slideNumber: { x: 12.3, y: 7.12, w: 0.55, h: 0.26, fontSize: 12, color: "3E4E60", margin: 0 },
});
pres.defineSlideMaster({
  title: "Fecho",
  background: { color: C.accent1 },
  objects: [
    {
      placeholder: {
        options: {
          name: "title", type: "title",
          x: 0.5, y: 0.36, w: 12.3, h: 0.55,
          fontSize: 30, bold: true, color: C.background1,
          margin: 0, valign: "middle", align: "left",
        },
        text: "",
      },
    },
  ],
  slideNumber: { x: 12.3, y: 7.12, w: 0.55, h: 0.26, fontSize: 12, color: "C4A046", margin: 0 },
});

function content(section) {
  return pres.addSlide({ masterName: "Conteudo", sectionTitle: section });
}

function codeBlock(slide, code, y, h) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y, w: 12.33, h,
    fill: fill(C.background2),
    rectRadius: 0.08,
    objectName: "codigo",
  });
  tx(slide, code, {
    x: 0.7, y: y + 0.12, w: 11.95, h: h - 0.22,
    fontFace: "Courier New", fontSize: 14, color: C.text1, margin: 0,
  });
}
function outputBlock(slide, output, y, h) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y, w: 12.33, h,
    fill: fill(C.accent1),
    rectRadius: 0.08,
    objectName: "saida",
  });
  tx(slide, output, {
    x: 0.7, y: y + 0.1, w: 11.95, h: h - 0.18,
    fontFace: "Courier New", fontSize: 14, color: C.background1, margin: 0,
  });
}

function codeSlide(section, meta) {
  const s = content(section);
  kicker(s, meta.kicker);
  title(s, meta.title);
  tx(s, meta.explain, {
    x: 0.5, y: 1.05, w: 12.33, h: meta.explainH || 0.85,
    fontSize: 16, color: C.text1,
  });
  const codeY = 1.05 + (meta.explainH || 0.85) + 0.1;
  const lines = meta.code.split("\n").length;
  const codeH = Math.max(1.15, lines * 0.27 + 0.28);
  codeBlock(s, meta.code, codeY, codeH);
  if (meta.output) {
    const outY = codeY + codeH + 0.12;
    const outLines = meta.output.split("\n").length;
    const outH = Math.max(0.7, outLines * 0.26 + 0.28);
    outputBlock(s, meta.output, outY, outH);
  }
  if (meta.note) s.addNotes(meta.note);
  return s;
}

// ---------------------------------------------------------------------------
pres.addSection({ title: "Abertura" });
{
  const s = pres.addSlide({ masterName: "Capa", sectionTitle: "Abertura" });
  tx(s, "TRABALHO FINAL  ·  IIG0029", {
    x: 0.7, y: 1.35, w: 11, h: 0.32,
    fontSize: 14, bold: true, color: C.accent2, charSpacing: 1.1,
  });
  tx(s, "O código, explicado\npasso a passo", {
    x: 0.7, y: 1.85, w: 11.5, h: 1.7,
    fontSize: 42, bold: true, color: C.background1,
  });
  tx(s, "Como o programa lê o FREUID, transforma a foto em números,\ntreina dois classificadores e mede o erro no Egito e em Moçambique.", {
    x: 0.7, y: 3.8, w: 11, h: 0.9,
    fontSize: 18, color: C.background1,
  });
  tx(s, "João Henrique Gomes Dias, Tiago e Micaela\nBacharelado em IA Aplicada à Gestão Pública  ·  UFG / IIG\nProf. Paulo Victor dos Santos  ·  2026/2", {
    x: 0.7, y: 5.15, w: 11, h: 1.15,
    fontSize: 16, color: C.background1,
  });
  s.addNotes("Abrir dizendo que esta versão é o trabalho final: não é só a ideia, é o código que rodou. Cada slide mostra um trecho, o que ele faz e o que apareceu na tela.");
}

{
  const s = content("Abertura");
  kicker(s, "O programa");
  title(s, "Cinco arquivos, nesta ordem");
  const files = [
    ["1", "eda.py", "Lê os rótulos e conta quantos documentos são legítimos, fraude, digitais ou impressos."],
    ["2", "download.py", "Escolhe um recorte estratificado e baixa só essas fotos, não os 46 GB."],
    ["3", "features.py", "Abre cada JPEG e troca a imagem por 64 números."],
    ["4", "train.py", "Separa treino e teste, ajusta os dois modelos e grava as métricas."],
    ["5", "metric.py", "Calcula o score da competição. Nesse score, menor é melhor."],
  ];
  files.forEach((f, i) => {
    const y = 1.15 + i * 1.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y, w: 12.33, h: 0.98,
      fill: fill(C.background2), rectRadius: 0.08, objectName: f[1],
    });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.68, y: y + 0.2, w: 0.58, h: 0.58,
      fill: fill(C.accent1), rectRadius: 0.08, objectName: "n" + f[0],
    });
    tx(s, f[0], {
      x: 0.68, y: y + 0.2, w: 0.58, h: 0.58,
      fontSize: 18, bold: true, color: C.background1, align: "center", valign: "middle",
    });
    tx(s, f[1], {
      x: 1.5, y: y + 0.12, w: 3.3, h: 0.72,
      fontFace: "Courier New", fontSize: 18, bold: true, color: C.text1, valign: "middle",
    });
    tx(s, f[2], {
      x: 4.9, y: y + 0.14, w: 7.6, h: 0.72,
      fontSize: 16, color: C.text1, valign: "middle",
    });
  });
  s.addNotes("Mostrar a ordem de execução. O professor não precisa abrir o repositório: os próximos slides percorrem esses cinco arquivos.");
}

// ---------------------------------------------------------------------------
pres.addSection({ title: "Dados" });
codeSlide("Dados", {
  kicker: "config.py",
  title: "Três constantes mandam no resto",
  explain: "O arquivo config.py não treina nada. Ele guarda os caminhos e os números que os outros arquivos importam, para o experimento poder ser repetido.",
  code: [
    "RANDOM_SEED = 42",
    "IMG_SIZE = 128",
    "SUBSET_SIZE = 600",
    "",
    "DATA = ROOT / \"data\"",
    "REPORTS = ROOT / \"reports\"",
    "SUBSET_DIR = DATA / \"images\" / \"subset\"",
  ].join("\n"),
  output: [
    "42    a semente: o sorteio do split sai igual toda vez",
    "128   cada foto é reduzida a 128 por 128 pixels",
    "600   quantas imagens o download tenta trazer",
  ].join("\n"),
  note: "A semente 42 não melhora o modelo. Ela só faz o mesmo código gerar a mesma divisão. 128 pixels é o tamanho das features clássicas. A CNN, se for feita depois, usa 384 ou 512.",
});

codeSlide("Dados", {
  kicker: "eda.py",
  title: "O primeiro passo é abrir o CSV",
  explain: "Os rótulos vêm de train_labels.csv. Cada linha é um documento. A coluna label é o Y: 0 legítimo, 1 fraude. A imagem em si ainda não entra aqui.",
  code: [
    "def load_labels(name: str) -> pd.DataFrame:",
    "    path = DATA / name",
    "    return pd.read_csv(path)",
    "",
    "full = load_labels(\"train_labels.csv\")",
    "print(len(full))",
    "print(list(full.columns))",
  ].join("\n"),
  output: [
    "69352",
    "['id', 'image_path', 'label', 'is_digital', 'type']",
  ].join("\n"),
  note: "69.352 linhas no treino oficial. Cinco colunas. image_path aponta para o JPEG. type é o país e o tipo do documento, por exemplo EGYPT/DL.",
});

codeSlide("Dados", {
  kicker: "eda.py",
  title: "Conta quantos são 0 e quantos são 1",
  explain: "value_counts conta as linhas de cada classe. sort_index deixa o 0 antes do 1. A porcentagem é o tamanho da classe dividido pelo total.",
  code: [
    "vc = full[\"label\"].value_counts().sort_index()",
    "for k, n in vc.items():",
    "    pct = 100 * n / len(full)",
    "    print(k, n, f\"{pct:.1f}%\")",
  ].join("\n"),
  output: [
    "0  40005  57.7%     legítimo",
    "1  29347  42.3%     fraude",
  ].join("\n"),
  note: "Não é um dataset de 1% de fraude. As duas classes são grandes. Isso importa porque um modelo que chuta sempre legítimo já erraria 42% das vezes.",
});

codeSlide("Dados", {
  kicker: "eda.py",
  title: "Quase nenhuma foto foi impressa",
  explain: "is_digital vale False quando o documento foi impresso e fotografado de novo. O groupby junta essas linhas e tira a média do label. Como fraude é 1, a média é a taxa de fraude.",
  code: [
    "by = full.groupby(\"is_digital\")[\"label\"].agg(",
    "    [\"count\", \"mean\"]",
    ")",
    "print(by)",
  ].join("\n"),
  output: [
    "is_digital   count    mean",
    "False           20    0.70",
    "True         69332    0.423",
  ].join("\n"),
  note: "Só 20 imagens são print-and-capture, e 14 delas são fraude. O modelo quase não vê esse tipo de ataque. Dizer que ele detecta reimpressão seria mentir sobre o dado.",
});

codeSlide("Dados", {
  kicker: "download.py",
  title: "A amostra não joga fora os casos raros",
  explain: "Baixar 46 GB não cabe no experimento da disciplina. build_subset separa os 20 recapturados e amostra o resto em partes iguais de label e type, para nenhum país sumir do recorte.",
  code: [
    "rare = df[df[\"is_digital\"] == False]   # os 20",
    "rest = df[df[\"is_digital\"] == True]",
    "rest[\"strata\"] = (",
    "    rest[\"label\"].astype(str)",
    "    + \"|\" + rest[\"type\"].astype(str)",
    ")",
    "# amostra cada estrato e junta com os 20",
    "out = pd.concat([rare, sample])",
    "out = out.drop_duplicates(subset=[\"id\"])",
    "out.to_csv(SUBSET_MANIFEST, index=False)",
  ].join("\n"),
  output: "Alvo do config: 600 linhas em data/subset_manifest.csv",
  note: "Estratificar por label e type evita um recorte só de Egito, ou só de fraude. Os 20 impressos entram todos porque são raros demais para serem sorteados.",
});

codeSlide("Dados", {
  kicker: "train.py",
  title: "Imagem que não baixou não entra no fit",
  explain: "O manifesto lista o que foi pedido. load_ready_manifest fica só com a linha cujo JPEG existe na pasta. Se sobrar menos de 100 arquivos, o script para, em vez de treinar com quase nada.",
  code: [
    "mf = pd.read_csv(SUBSET_MANIFEST)",
    "exists = mf[\"image_path\"].map(",
    "    lambda p: (SUBSET_DIR / Path(p).name).exists()",
    ")",
    "ready = mf[exists].copy()",
    "print(len(mf), len(ready))",
    "if len(ready) < 100:",
    "    raise RuntimeError(\"Poucas imagens baixadas.\")",
  ].join("\n"),
  output: "Imagens usadas no treino e no teste: 544",
  note: "544 é 0,8% das 69.352. É o recorte em que os números deste trabalho foram calculados. Não é o placar da competição.",
});

// ---------------------------------------------------------------------------
pres.addSection({ title: "Features" });
codeSlide("Features", {
  kicker: "features.py",
  title: "A foto vira um vetor antes do modelo",
  explain: "A regressão logística não recebe pixels soltos. extract_one abre o JPEG, força RGB, reduz para 128 por 128 e junta o histograma com as estatísticas.",
  code: [
    "def extract_one(path, size=128):",
    "    with Image.open(path) as im:",
    "        im = im.convert(\"RGB\").resize(",
    "            (size, size), Image.BILINEAR",
    "        )",
    "        arr = np.asarray(im, dtype=np.uint8)",
    "    return np.concatenate([",
    "        _hist_features(arr),",
    "        _stat_features(arr),",
    "    ])",
  ].join("\n"),
  output: "Uma foto  →  vetor de 64 números  (48 de cor + 16 de brilho e borda)",
  note: "BILINEAR só redimensiona. Não é um filtro para esconder fraude. RGB garante três canais mesmo se alguma foto vier em cinza.",
});

codeSlide("Features", {
  kicker: "features.py",
  title: "48 números contam a cor",
  explain: "Para cada canal, vermelho, verde e azul, o histograma reparte os pixels em 16 faixas de tom. density=True transforma a contagem em proporção, então o tamanho da foto não infla o número.",
  code: [
    "def _hist_features(arr, bins=16):",
    "    feats = []",
    "    for c in range(3):          # R, G, B",
    "        h, _ = np.histogram(",
    "            arr[:, :, c],",
    "            bins=bins,",
    "            range=(0, 256),",
    "            density=True,",
    "        )",
    "        feats.append(h)",
    "    return np.concatenate(feats)",
  ].join("\n"),
  output: "3 canais  ×  16 faixas  =  48 números",
  note: "A hipótese é simples: colagem e edição mudam a distribuição de cor. O histograma não vê o que está escrito no documento. Ele vê se o tom da foto foge do padrão.",
});

codeSlide("Features", {
  kicker: "features.py",
  title: "16 números medem brilho e borda",
  explain: "Em cada canal o código tira média, desvio, mínimo e máximo. Depois monta um cinza e mede o quanto um pixel muda para o vizinho. Essa mudança é o gradiente, um jeito simples de ver emenda e recompressão.",
  code: [
    "for c in range(3):",
    "    x = ch[:, :, c]",
    "    stats.extend([",
    "        x.mean(), x.std(), x.min(), x.max()",
    "    ])",
    "gray = (",
    "    0.299 * ch[:, :, 0]",
    "    + 0.587 * ch[:, :, 1]",
    "    + 0.114 * ch[:, :, 2]",
    ")",
    "gx = np.abs(np.diff(gray, axis=1)).mean()",
    "gy = np.abs(np.diff(gray, axis=0)).mean()",
  ].join("\n"),
  output: "12 do RGB  +  média e desvio do cinza  +  gx e gy  =  16",
  note: "gx é a variação na horizontal, gy na vertical. Junto com o histograma, o vetor fecha em 64. É isso que entra como X.",
});

// ---------------------------------------------------------------------------
pres.addSection({ title: "Treino" });
codeSlide("Treino", {
  kicker: "train.py  ·  split_data",
  title: "Moçambique não entra no fit",
  explain: "sorted põe os tipos em ordem alfabética. O último é MOZAMBIQUE/DL. Esse tipo vai inteiro para o teste OOD. O modelo nunca vê uma carteira de Moçambique durante o treino.",
  code: [
    "types = sorted(df[\"type\"].unique())",
    "heldout = types[-1]",
    "train_df = df[df[\"type\"] != heldout]",
    "test_ood = df[df[\"type\"] == heldout]",
    "print(heldout, len(test_ood))",
  ].join("\n"),
  output: "MOZAMBIQUE/DL    41 imagens no teste OOD",
  note: "OOD quer dizer fora da distribuição de treino. Se o modelo só aprendeu a cara dos outros documentos, Moçambique é a prova. Não é um teste misturado com o treino.",
});

codeSlide("Treino", {
  kicker: "train.py  ·  GroupShuffleSplit",
  title: "O teste principal também é um país inteiro",
  explain: "Entre os tipos que sobraram, o split não sorteia foto por foto. groups=type manda um país inteiro para o teste. Com a semente 42, esse país foi o Egito. O restante fica no treino.",
  code: [
    "gss = GroupShuffleSplit(",
    "    n_splits=1,",
    "    test_size=0.2,",
    "    random_state=42,",
    ")",
    "tr, te = next(gss.split(",
    "    idx,",
    "    train_df[\"label\"],",
    "    groups=train_df[\"type\"],",
    "))",
  ].join("\n"),
  output: [
    "treino     394    Benin, Guiné e Maurício",
    "teste ID   109    Egito      (28 fraudes, 81 legítimos)",
    "teste OOD   41    Moçambique",
  ].join("\n"),
  note: "ID aqui significa documento novo, mas do mesmo desenho de experimento: um type que não entrou no fit. O Egito é o teste que usamos para comparar os dois modelos. Moçambique é o teste mais duro.",
});

codeSlide("Treino", {
  kicker: "train.py  ·  fit_models",
  title: "A logística passa por um scaler",
  explain: "Pipeline amarra dois passos. O StandardScaler calcula média e desvio só no fit, portanto só nas 394 imagens de treino. A logística recebe os 64 números já na mesma escala e devolve uma chance.",
  code: [
    "Pipeline([",
    "    (\"scaler\", StandardScaler()),",
    "    (\"clf\", LogisticRegression(",
    "        max_iter=2000,",
    "        class_weight=\"balanced\",",
    "        random_state=42,",
    "    )),",
    "])",
  ].join("\n"),
  output: "class_weight=\"balanced\"  aumenta o peso da classe menor no fit",
  note: "Sem o scaler, um número grande, como um máximo de cor perto de 255, dominaria a soma. balanced existe porque 42% de fraude ainda não é meio a meio dentro do treino. max_iter=2000 só garante que a otimização termina.",
});

codeSlide("Treino", {
  kicker: "train.py  ·  fit_models",
  title: "A floresta é um voto de 300 árvores",
  explain: "Cada árvore faz perguntas do tipo: este gradiente passou do corte? A classe da floresta é a que recebe mais votos. Ela não usa scaler, porque um corte numa árvore não depende da escala.",
  code: [
    "RandomForestClassifier(",
    "    n_estimators=300,",
    "    max_depth=20,",
    "    min_samples_leaf=2,",
    "    class_weight=\"balanced_subsample\",",
    "    n_jobs=-1,",
    "    random_state=42,",
    ")",
  ].join("\n"),
  output: "300 árvores  ·  profundidade máxima 20  ·  folha com pelo menos 2 fotos",
  note: "min_samples_leaf=2 impede uma folha de decorar uma única imagem. balanced_subsample reequilibra dentro de cada árvore, não no conjunto inteiro. n_jobs=-1 só usa os núcleos da máquina.",
});

codeSlide("Treino", {
  kicker: "train.py",
  title: "O fit só olha o treino",
  explain: "X já é a matriz 544 por 64. O iloc do split devolve as linhas de treino. fit ajusta os pesos da logística e as árvores da floresta. Egito e Moçambique não participam desta chamada.",
  code: [
    "X = extract_matrix(df[\"image_path\"].tolist())",
    "y = df[\"label\"].to_numpy().astype(int)",
    "",
    "X_train = X[train_df.index]",
    "y_train = y[train_df.index]",
    "",
    "for name, model in models.items():",
    "    print(\"Treinando\", name)",
    "    model.fit(X_train, y_train)",
  ].join("\n"),
  output: [
    "Treinando logistic_regression",
    "Treinando random_forest",
    "X_train.shape  →  (394, 64)",
  ].join("\n"),
  note: "394 linhas, 64 colunas. Se alguém passar o teste para o fit, a métrica deixa de ser teste. O código não faz isso: fit recebe só train_df.index.",
});

codeSlide("Treino", {
  kicker: "train.py  ·  evaluate",
  title: "A chance vira classe no corte 0,5",
  explain: "predict_proba devolve duas colunas: chance de 0 e chance de 1. A coluna 1 é a chance de fraude. No corte 0,5, chance maior ou igual a meio vira a classe fraude.",
  code: [
    "score = model.predict_proba(X)[:, 1]",
    "pred = (score >= 0.5).astype(int)",
    "",
    "out = freuid_breakdown(y, score)",
    "out[\"accuracy\"] = float((pred == y).mean())",
  ].join("\n"),
  output: "score é contínuo, de 0 a 1.   pred é 0 ou 1.",
  note: "A matriz de confusão usa pred, o corte seco. A ROC e o score FREUID usam score, a chance, porque elas variam o corte em vez de fixar 0,5. São duas leituras do mesmo modelo.",
});

// ---------------------------------------------------------------------------
pres.addSection({ title: "Resultados" });
{
  const s = content("Resultados");
  kicker(s, "train.py  ·  teste do Egito, 109 fotos");
  title(s, "O que o corte 0,5 errou");
  tx(s, "A linha de cima é o que a foto era. A coluna é o que o modelo disse. O número em vermelho é a fraude que passou: o erro mais caro no balcão.", {
    x: 0.5, y: 1.05, w: 12.33, h: 0.6, fontSize: 16,
  });
  function matrix(slide, x, name, colorName, cells) {
    tx(slide, name, {
      x, y: 1.75, w: 5.8, h: 0.36,
      fontSize: 18, bold: true, color: colorName,
    });
    tx(slide, "disse fraude", {
      x: x + 1.55, y: 2.18, w: 1.9, h: 0.28,
      fontSize: 13, bold: true, color: C.text2, align: "center",
    });
    tx(slide, "disse legítimo", {
      x: x + 3.55, y: 2.18, w: 1.9, h: 0.28,
      fontSize: 13, bold: true, color: C.text2, align: "center",
    });
    const rows = [
      ["é fraude", cells[0], cells[1]],
      ["é legítimo", cells[2], cells[3]],
    ];
    rows.forEach((r, ri) => {
      const y = 2.55 + ri * 1.25;
      tx(slide, r[0], {
        x, y, w: 1.4, h: 1.1,
        fontSize: 14, bold: true, color: C.text2, align: "right", valign: "middle",
      });
      [r[1], r[2]].forEach((cell, ci) => {
        const cx = x + 1.55 + ci * 2.0;
        slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
          x: cx, y, w: 1.88, h: 1.12,
          fill: fill(cell.fill), rectRadius: 0.08, objectName: cell.label,
        });
        tx(slide, String(cell.n), {
          x: cx, y: y + 0.08, w: 1.88, h: 0.55,
          fontSize: 28, bold: true, color: cell.tc, align: "center",
        });
        tx(slide, cell.label, {
          x: cx, y: y + 0.64, w: 1.88, h: 0.36,
          fontSize: 13, color: cell.tc, align: "center",
        });
      });
    });
  }
  const soft = C.background2;
  const white = C.background1;
  matrix(s, 0.45, "Regressão logística", C.accent4, [
    { n: "23", label: "fraude pega", fill: soft, tc: C.accent5 },
    { n: "5", label: "passou", fill: C.accent3, tc: white },
    { n: "27", label: "alarme falso", fill: soft, tc: C.accent6 },
    { n: "54", label: "aceito", fill: soft, tc: C.accent4 },
  ]);
  matrix(s, 6.85, "Random Forest", C.accent6, [
    { n: "19", label: "fraude pega", fill: soft, tc: C.accent5 },
    { n: "9", label: "passou", fill: C.accent3, tc: white },
    { n: "11", label: "alarme falso", fill: soft, tc: C.accent6 },
    { n: "70", label: "aceito", fill: soft, tc: C.accent4 },
  ]);
  tx(s, "Revocação da fraude:  23/28 = 0,82 na logística    e    19/28 = 0,68 na floresta.", {
    x: 0.5, y: 5.25, w: 12.33, h: 0.35, fontSize: 16, bold: true,
  });
  tx(s, "A floresta tem acurácia maior (0,82 contra 0,71) porque aceita mais legítimos. No cadastro, as 5 fraudes que a logística deixou passar pesam mais do que os alarmes falsos.", {
    x: 0.5, y: 5.65, w: 12.33, h: 0.85, fontSize: 16,
  });
  s.addNotes("Ler os vermelhos primeiro. Logística deixou passar 5 fraudes e disparou 27 alarmes. Floresta deixou passar 9 e disparou 11. Acurácia maior não escolhe o modelo do órgão. O erro caro é a fraude que entra.");
}

codeSlide("Resultados", {
  kicker: "train.py  ·  plot_roc",
  title: "A ROC não usa o corte 0,5",
  explain: "roc_curve testa vários cortes e desenha a taxa de fraude pega contra a taxa de legítimo barrado. A diagonal é o chute. A área sob a curva é o AUC: 0,5 é chute, 1 é separação perfeita.",
  code: [
    "for name, s in scores.items():",
    "    fpr, tpr, _ = roc_curve(y, s)",
    "    auc = roc_auc_score(y, s)",
    "    plt.plot(fpr, tpr, label=f\"{name} (AUC={auc:.3f})\")",
    "plt.plot([0, 1], [0, 1], \"k--\")",
    "plt.xlabel(\"FPR (BPCER)\")",
    "plt.ylabel(\"TPR (1 - APCER)\")",
  ].join("\n"),
  output: [
    "Egito, 109 fotos",
    "logistic_regression   AUC = 0.889",
    "random_forest         AUC = 0.808",
  ].join("\n"),
  note: "Os dois ficam acima do chute no Egito. A logística separa melhor quando o corte pode variar. Isso não contradiz a matriz: a matriz é um corte só, o de 0,5.",
});

codeSlide("Resultados", {
  kicker: "metric.py",
  title: "O score oficial pede pouco alarme falso",
  explain: "A competição não olha a acurácia. Ela mede o AUC e, além disso, quanta fraude ainda é pega quando no máximo 1% dos legítimos é barrado. O score publicado é 1 menos a média harmônica desses dois. Menor é melhor.",
  code: [
    "auc = roc_auc_score(y_true, y_score)",
    "fpr, tpr, _ = roc_curve(y_true, y_score)",
    "tpr_at_1 = tpr[fpr <= 0.01].max()",
    "harm = 2 * auc * tpr_at_1 / (auc + tpr_at_1)",
    "return 1 - harm",
  ].join("\n"),
  output: [
    "Egito     logística  score 0.2785     floresta  score 0.3305",
    "Moçambique  logística  score 1.000    floresta  score 0.5817",
    "No Egito, a logística fica mais perto de zero. Menor é melhor.",
  ].join("\n"),
  note: "APCER a 1% de BPCER é 1 menos aquele TPR. No Egito a logística tem APCER 0,39: mesmo no corte exigente, ainda deixa passar cerca de 39% das fraudes. Em Moçambique a logística vai a 1, o pior valor, porque não acha um corte que barre fraude sem barrar legítimo.",
});

{
  const s = content("Resultados");
  kicker(s, "reports/metrics.csv");
  title(s, "A tabela que o script gravou");
  tx(s, "O final de train.py arredonda as métricas e grava metrics.csv. ID é o Egito. OOD é Moçambique. Esta é a tabela inteira da rodada, sem número novo.", {
    x: 0.5, y: 1.05, w: 12.33, h: 0.6, fontSize: 16,
  });
  const head = (text) => ({
    text,
    options: {
      fill: fill("0B2F4A"), color: "FFFFFF", bold: true, align: "center", valign: "middle",
      margin: [4, 3, 4, 3],
    },
  });
  const cell = (text, extra) => ({
    text,
    options: Object.assign({
      fill: fill("F4F7FB"), color: "0D3B66", align: "center", valign: "middle",
      margin: [4, 3, 4, 3],
    }, extra || {}),
  });
  const rows = [
    ["modelo", "teste", "n", "AUC", "acurácia", "revocação", "score"].map(head),
    ["logística", "Egito", "109", "0,889", "0,71", "0,82", "0,279"].map((t) => cell(t)),
    ["logística", "Moçambique", "41", "0,687", "0,51", "1,00", "1,000"].map((t) => cell(t)),
    ["floresta", "Egito", "109", "0,808", "0,82", "0,68", "0,331"].map((t) => cell(t)),
    ["floresta", "Moçambique", "41", "0,691", "0,51", "1,00", "0,582"].map((t) => cell(t)),
  ];
  s.addTable(rows, {
    x: 0.5, y: 1.8, w: 12.33, h: 2.6,
    colW: [2.1, 2.3, 1.3, 1.5, 1.7, 1.8, 1.63],
    border: [
      { pt: 0.5, color: "E6EDF4" },
      { pt: 0.5, color: "E6EDF4" },
      { pt: 0.5, color: "E6EDF4" },
      { pt: 0.5, color: "E6EDF4" },
    ],
    fontSize: 15,
    valign: "middle",
    objectName: "metrics",
  });
  tx(s, "Revocação 1,00 em Moçambique não é vitória. A acurácia 0,51 mostra que os dois passaram a chamar quase tudo de fraude: pegam as fraudes e também os legítimos.", {
    x: 0.5, y: 4.7, w: 12.33, h: 0.9, fontSize: 16,
  });
  tx(s, "No Egito os dois passam do chute (AUC 0,50). Entre eles, a logística deixa passar menos fraude. A floresta incomoda menos o cidadão legítimo. Com 109 fotos não há um vencedor definitivo.", {
    x: 0.5, y: 5.65, w: 12.33, h: 0.9, fontSize: 16,
  });
  s.addNotes("Não escolher um campeão. Ler a tabela em duas linhas: no Egito funciona acima do chute; em Moçambique a acurácia cai para 0,51 e a revocação 1 é um artefato de chamar tudo de fraude.");
}

{
  const s = content("Resultados");
  kicker(s, "O que o código sustenta");
  title(s, "Três frases que os números aguentam");
  const cards = [
    ["1", "No documento visto de lado, os 64 números separam.", "No Egito, que não entrou no fit, o AUC ficou em 0,89 e 0,81. Os dois modelos ficam acima de um sorteio."],
    ["2", "O erro caro e o erro barato não apontam o mesmo modelo.", "A logística deixa passar 5 fraudes e gera 27 alarmes. A floresta deixa passar 9 e gera 11 alarmes."],
    ["3", "Um país novo derruba o resultado.", "Em Moçambique a acurácia dos dois vai a 0,51. Cor e borda aprenderam os documentos do treino, não um detector universal."],
  ];
  cards.forEach((c, i) => {
    const y = 1.15 + i * 1.85;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y, w: 12.33, h: 1.7,
      fill: fill(C.background2), rectRadius: 0.08, objectName: "frase " + c[0],
    });
    s.addShape(pres.shapes.OVAL, {
      x: 0.72, y: y + 0.5, w: 0.62, h: 0.62,
      fill: fill(C.accent1), objectName: "bola " + c[0],
    });
    tx(s, c[0], {
      x: 0.72, y: y + 0.5, w: 0.62, h: 0.62,
      fontSize: 20, bold: true, color: C.background1, align: "center", valign: "middle",
    });
    tx(s, c[1], {
      x: 1.6, y: y + 0.16, w: 10.9, h: 0.5,
      fontSize: 18, bold: true, color: C.text1,
    });
    tx(s, c[2], {
      x: 1.6, y: y + 0.72, w: 10.9, h: 0.75,
      fontSize: 16, color: C.text1,
    });
  });
  s.addNotes("Fechar a parte de resultado com essas três frases e parar. Não extrapolar para produção, nem para o placar do Kaggle.");
}

// ---------------------------------------------------------------------------
pres.addSection({ title: "Conclusao" });
{
  const s = pres.addSlide({ masterName: "Fecho", sectionTitle: "Conclusao" });
  tx(s, "O QUE O CÓDIGO NÃO FAZ", {
    x: 0.55, y: 0.28, w: 12, h: 0.28,
    fontSize: 13, bold: true, color: C.accent2, charSpacing: 1.1,
  });
  title(s, "Limite honesto do experimento");
  const items = [
    ["544 fotos", "São 0,8% do treino oficial. O número serve para comparar os modelos da aula, não para disputar a competição."],
    ["64 números", "Histograma e borda não leem o nome nem a foto do rosto. Uma CNN olharia a imagem inteira. Este código não treinou CNN."],
    ["Corte 0,5", "Foi uma escolha fixa. No balcão, o corte deveria mudar conforme o custo de deixar a fraude passar."],
    ["Uso acadêmico", "Dataset sintético da Microblink. As imagens não podem ser republicadas. O modelo não vai para produção."],
  ];
  items.forEach((it, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.55 + col * 6.35;
    const y = 1.25 + row * 2.15;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x, y, w: 6.1, h: 2.0,
      fill: fill(C.background1), rectRadius: 0.08, objectName: it[0],
    });
    tx(s, it[0], {
      x: x + 0.25, y: y + 0.2, w: 5.6, h: 0.45,
      fontSize: 20, bold: true, color: C.text1,
    });
    tx(s, it[1], {
      x: x + 0.25, y: y + 0.75, w: 5.6, h: 1.05,
      fontSize: 15, color: C.text1,
    });
  });
  tx(s, "Microblink Fraud Lab. The FREUID Challenge 2026 – IJCAI-ECAI. Kaggle, 2026.", {
    x: 0.55, y: 5.7, w: 12.2, h: 0.35, fontSize: 14, color: C.background1,
  });
  s.addNotes("Encerrar no limite, não numa promessa. Se perguntarem o próximo passo: mais imagens do mesmo dataset e, só então, uma CNN. O corte de 0,5 pode ser recalculado pelo custo de cada erro.");
}

async function main() {
  const { applyTheme } = require(APPLY);
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log(OUT);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
