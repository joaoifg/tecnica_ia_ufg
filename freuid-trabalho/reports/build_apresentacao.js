const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = "c:/Users/style/OneDrive/tecnica_ia_ufg/freuid-trabalho/reports";
const OUT = path.join(ROOT, "apresentacao_FREUID.pptx");
const APPLY = "C:/Users/style/.claude/skills/synced/6aeb86cb-6193-4178-8d49-e84e4d2bc47d_5ef7ce20-2893-437c-b2c8-0d9bb07e9a7c/pptx/scripts/apply_theme.js";

const THEME = {
  name: "FREUID Publico",
  colors: {
    dk1: "0D3B66",
    lt1: "FFFFFF",
    dk2: "3E4E60",
    lt2: "F3F6FA",
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
pres.title = "FREUID 2026 — Detecção de fraude documental";
pres.author = "João Henrique Gomes Dias, Tiago e Micaela";
pres.subject = "Técnicas de IA I — UFG IIG";
pres.company = "UFG IIG";

const C = pres.SchemeColor;

function sh() {
  return { type: "outer", color: "0D3B66", blur: 14, opacity: 0.1, offset: 3, angle: 90 };
}
function fill(color) {
  return { color };
}
function panel(slide, x, y, w, h, color, name) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h,
    fill: fill(color || C.background2),
    rectRadius: 0.1,
    shadow: sh(),
    objectName: name || "painel",
  });
}
function tx(slide, text, opts) {
  slide.addText(text, Object.assign({
    isTextBox: true,
    margin: 0,
    fontSize: 15,
    color: C.text1,
    valign: "top",
    wrap: true,
  }, opts));
}
function kicker(slide, text) {
  tx(slide, text.toUpperCase(), {
    x: 0.52, y: 0.16, w: 12.2, h: 0.26,
    fontSize: 12, bold: true, color: C.accent1, charSpacing: 1.2, margin: 0,
  });
}
function title(slide, text) {
  slide.addText(text, { placeholder: "title" });
}
function take(slide, runs, y) {
  const top = y || 6.22;
  panel(slide, 0.52, top, 12.29, 0.78, C.background2, "destaque");
  tx(slide, runs, {
    x: 0.72, y: top + 0.12, w: 11.9, h: 0.54,
    fontSize: 16, color: C.text1, valign: "middle",
  });
}

pres.defineSlideMaster({
  title: "Capa",
  background: { color: C.accent1 },
  objects: [],
  slideNumber: { x: 12.35, y: 7.12, w: 0.5, h: 0.26, fontSize: 12, color: "C4A046", margin: 0 },
});

pres.defineSlideMaster({
  title: "Conteudo",
  background: { color: C.background1 },
  objects: [
    {
      placeholder: {
        options: {
          name: "title",
          type: "title",
          x: 0.52, y: 0.42, w: 12.29, h: 0.62,
          fontSize: 32,
          bold: true,
          color: C.text1,
          margin: 0,
          valign: "middle",
        },
        text: "",
      },
    },
  ],
  slideNumber: { x: 12.35, y: 7.12, w: 0.5, h: 0.26, fontSize: 12, color: "3E4E60", margin: 0 },
});

pres.defineSlideMaster({
  title: "Fecho",
  background: { color: C.accent1 },
  objects: [
    {
      placeholder: {
        options: {
          name: "title",
          type: "title",
          x: 0.52, y: 0.32, w: 12.29, h: 0.64,
          fontSize: 32,
          bold: true,
          color: C.background1,
          margin: 0,
          valign: "middle",
        },
        text: "",
      },
    },
  ],
  slideNumber: { x: 12.35, y: 7.12, w: 0.5, h: 0.26, fontSize: 12, color: "C4A046", margin: 0 },
});

function content(section) {
  return pres.addSlide({ masterName: "Conteudo", sectionTitle: section });
}

// ---------------------------------------------------------------------------
// 1. Capa
// ---------------------------------------------------------------------------
pres.addSection({ title: "Abertura" });
{
  const s = pres.addSlide({ masterName: "Capa", sectionTitle: "Abertura" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.7, y: 1.22, w: 4.55, h: 0.38,
    fill: fill(C.accent1),
    line: { color: "C4A046", width: 1.25 },
    rectRadius: 0.18,
    objectName: "selo",
  });
  tx(s, "TRABALHO FINAL  ·  IIG0029", {
    x: 0.7, y: 1.26, w: 4.55, h: 0.3,
    fontSize: 12, bold: true, color: C.accent2, align: "center", valign: "middle", charSpacing: 0.8,
  });
  tx(s, [
    { text: "Esse documento é", options: { breakLine: true } },
    { text: "verdadeiro?", options: { color: C.accent2 } },
  ], {
    x: 0.7, y: 1.8, w: 5.9, h: 1.85,
    fontSize: 40, bold: true, color: C.background1,
  });
  tx(s, "Classificação de fraude em documentos de identidade com o dataset do FREUID Challenge 2026, para a validação cadastral do serviço público.", {
    x: 0.7, y: 3.8, w: 5.7, h: 1.15,
    fontSize: 18, color: C.background1,
  });
  tx(s, [
    { text: "João Henrique Gomes Dias, Tiago e Micaela", options: { bold: true, breakLine: true } },
    { text: "Bacharelado em IA Aplicada à Gestão Pública", options: { breakLine: true } },
    { text: "UFG / IIG  ·  Prof. Paulo Victor dos Santos  ·  2026/2", options: { breakLine: false } },
  ], {
    x: 0.7, y: 5.35, w: 5.8, h: 1.15,
    fontSize: 15, color: C.background1,
  });
  s.addImage({
    path: path.join(ROOT, "freuid_banner.png"),
    x: 6.85, y: 2.15, w: 5.8, h: 2.9,
    objectName: "cartaz FREUID",
    shadow: sh(),
  });
  s.addNotes("Abrir com a pergunta do balcão: a foto deste documento é verdadeira? Apresentar o trio, a disciplina e o FREUID 2026 como o dataset do trabalho. A imagem é o cartaz oficial da competição, não uma foto do dataset.");
}

// ---------------------------------------------------------------------------
// 2. Sumário
// ---------------------------------------------------------------------------
{
  const s = content("Abertura");
  kicker(s, "Roteiro");
  title(s, "Sumário");
  const items = [
    ["1", "Por que o FREUID", "O problema de balcão e os motivos da escolha"],
    ["2", "O dataset por dentro", "Tamanho, países, tipos de fraude e o par (X, Y)"],
    ["3", "Técnicas da aula", "Classificação, divisão dos dados, logística e Random Forest"],
    ["4", "Resultados", "Matriz de confusão e o teste com um documento novo"],
    ["5", "Conclusão", "O que os números sustentam e os próximos passos"],
  ];
  items.forEach((it, i) => {
    const y = 1.28 + i * 1.05;
    panel(s, 0.52, y, 12.29, 0.92, C.background2, "item " + it[0]);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.72, y: y + 0.16, w: 0.6, h: 0.6,
      fill: fill(i % 2 === 0 ? C.accent1 : C.accent4),
      rectRadius: 0.08,
      objectName: "numero " + it[0],
    });
    tx(s, it[0], {
      x: 0.72, y: y + 0.16, w: 0.6, h: 0.6,
      fontSize: 22, bold: true, color: C.background1, align: "center", valign: "middle",
    });
    tx(s, it[1], {
      x: 1.58, y: y + 0.12, w: 10.8, h: 0.38,
      fontSize: 20, bold: true, color: C.text1,
    });
    tx(s, it[2], {
      x: 1.58, y: y + 0.48, w: 10.8, h: 0.32,
      fontSize: 15, color: C.text2,
    });
  });
  s.addNotes("Avisar o percurso: escolha do dataset, o que tem dentro, os modelos da aula, o resultado no Egito e a queda em Moçambique. São cinco blocos, cerca de um minuto cada.");
}

// ---------------------------------------------------------------------------
// 3. Cinco motivos
// ---------------------------------------------------------------------------
pres.addSection({ title: "Por que o FREUID" });
{
  const s = content("Por que o FREUID");
  kicker(s, "Por que o FREUID");
  title(s, "Por que este dataset");
  const cards = [
    ["Serviço público", "Problema de balcão", "Conselho, benefício e concurso conferem o documento antes de abrir o cadastro.", true],
    ["X e Y", "Já vem rotulado", "Cada foto tem a resposta marcada: 0 é legítimo e 1 é fraude.", false],
    ["69.352", "Grande e equilibrado", "Imagens rotuladas, com cerca de 58% legítimas e 42% fraude.", false],
    ["0 pessoas", "Sem dado pessoal", "Os documentos são sintéticos. Nenhum rosto ou nome é real.", false],
    ["2026", "Tema atual", "Competição do IJCAI-ECAI sobre fraude feita também com IA generativa.", false],
  ];
  const gap = 0.14;
  const w = (12.29 - 4 * gap) / 5;
  cards.forEach((c, i) => {
    const x = 0.52 + i * (w + gap);
    const dark = c[3];
    panel(s, x, 1.28, w, 4.55, dark ? C.accent1 : C.background2, c[0]);
    tx(s, c[0], {
      x: x + 0.16, y: 1.5, w: w - 0.32, h: 0.9,
      fontSize: 22, bold: true, color: dark ? C.background1 : C.text1,
    });
    tx(s, c[1], {
      x: x + 0.16, y: 2.7, w: w - 0.32, h: 0.8,
      fontSize: 16, bold: true, color: dark ? C.background1 : C.text1,
    });
    tx(s, c[2], {
      x: x + 0.16, y: 3.7, w: w - 0.32, h: 1.85,
      fontSize: 15, color: dark ? C.background1 : C.text1,
    });
  });
  take(s, [
    { text: "Atende ao que a disciplina pediu: ", options: {} },
    { text: "um problema da administração pública", options: { bold: true } },
    { text: " com dados X e rótulos Y, no formato ", options: {} },
    { text: "D = {(x, y)}", options: { bold: true } },
    { text: ".", options: {} },
  ]);
  s.addNotes("Cinco motivos, nesta ordem: é problema de gestão pública, já tem X e Y, é grande, não tem dado pessoal real e é de 2026. Fechar com a fórmula D = {(x, y)} que o professor pediu.");
}

// ---------------------------------------------------------------------------
// 4. Balcão
// ---------------------------------------------------------------------------
{
  const s = content("Por que o FREUID");
  kicker(s, "Por que o FREUID");
  title(s, "O problema no balcão");
  const steps = [
    ["1", "O cidadão envia a foto", "Carteira de motorista ou identidade, no cadastro online do órgão."],
    ["2", "O modelo dá um risco", "Um número de 0 a 1. Quanto maior, maior a chance de fraude."],
    ["3", "O servidor decide", "Risco baixo segue o fluxo. Risco alto vai para conferência manual."],
  ];
  const aw = 0.38;
  const sw = (12.29 - 2 * aw) / 3;
  steps.forEach((st, i) => {
    const x = 0.52 + i * (sw + aw);
    panel(s, x, 1.26, sw, 2.55, C.background2, "passo " + st[0]);
    s.addShape(pres.shapes.OVAL, {
      x: x + sw / 2 - 0.24, y: 1.42, w: 0.48, h: 0.48,
      fill: fill(C.accent1),
      objectName: "circulo " + st[0],
    });
    tx(s, st[0], {
      x: x + sw / 2 - 0.24, y: 1.42, w: 0.48, h: 0.48,
      fontSize: 18, bold: true, color: C.background1, align: "center", valign: "middle",
    });
    tx(s, st[1], {
      x: x + 0.18, y: 2.02, w: sw - 0.36, h: 0.6,
      fontSize: 16, bold: true, color: C.text1, align: "center",
    });
    tx(s, st[2], {
      x: x + 0.18, y: 2.64, w: sw - 0.36, h: 0.95,
      fontSize: 14, color: C.text1, align: "center",
    });
    if (i < 2) {
      tx(s, "→", {
        x: x + sw, y: 2.15, w: aw, h: 0.45,
        fontSize: 22, bold: true, color: C.accent2, align: "center", valign: "middle",
      });
    }
  });
  panel(s, 0.52, 4.05, 6.0, 1.9, C.background2, "erro grave");
  tx(s, "Erro grave: deixar a fraude passar", {
    x: 0.74, y: 4.22, w: 5.56, h: 0.38,
    fontSize: 16, bold: true, color: C.accent3,
  });
  tx(s, "O documento falso entra no cadastro. Pode surgir um profissional que não existe, ou um benefício pago para a pessoa errada.", {
    x: 0.74, y: 4.68, w: 5.56, h: 1.05,
    fontSize: 15, color: C.text1,
  });
  panel(s, 6.81, 4.05, 6.0, 1.9, C.background2, "erro menor");
  tx(s, "Erro menor: barrar quem é legítimo", {
    x: 7.03, y: 4.22, w: 5.56, h: 0.38,
    fontSize: 16, bold: true, color: C.accent6,
  });
  tx(s, "O cidadão volta para uma segunda análise. Gera atraso, e uma pessoa corrige o caso.", {
    x: 7.03, y: 4.68, w: 5.56, h: 1.05,
    fontSize: 15, color: C.text1,
  });
  take(s, [
    { text: "A IA não substitui o servidor. ", options: { bold: true } },
    { text: "Ela aponta quais documentos merecem uma segunda olhada.", options: {} },
  ]);
  s.addNotes("Contar o fluxo em três tempos: a foto chega, o modelo devolve um risco entre 0 e 1, o servidor decide. Deixar fraude passar é o erro caro. Barrar um legítimo gera fila, mas tem correção humana. A IA é filtro, não carimbo.");
}

// ---------------------------------------------------------------------------
// 5. Raio-X
// ---------------------------------------------------------------------------
pres.addSection({ title: "O dataset" });
{
  const s = content("O dataset");
  kicker(s, "O dataset por dentro");
  title(s, "Raio-X do FREUID 2026");
  const tiles = [
    ["69.352", "imagens rotuladas", "Cada uma com o rótulo 0 ou 1 no treino.", true],
    ["46,65 GB", "tamanho da competição", "212.186 arquivos JPEG e CSV.", false],
    ["5", "modelos de documento", "CNH de Egito, Guiné, Benin e Moçambique, e a identidade de Maurício.", false],
    ["3", "formas de fraude", "Manipulação física, edição por IA e foto de papel impresso.", false],
    ["0", "pessoas reais", "Rostos, nomes e números são gerados por computador.", false],
    ["5 colunas", "no arquivo de rótulos", "id, image_path, label, is_digital e type.", false],
  ];
  const gap = 0.16;
  const tw = (12.29 - 2 * gap) / 3;
  const th = 2.28;
  tiles.forEach((t, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 0.52 + col * (tw + gap);
    const y = 1.26 + row * (th + gap);
    const dark = t[3];
    panel(s, x, y, tw, th, dark ? C.accent1 : C.background2, t[0]);
    tx(s, t[0], {
      x: x + 0.22, y: y + 0.28, w: tw - 0.44, h: 0.7,
      fontSize: 32, bold: true, color: dark ? C.background1 : C.text1,
    });
    tx(s, t[1], {
      x: x + 0.22, y: y + 1.02, w: tw - 0.44, h: 0.36,
      fontSize: 16, bold: true, color: dark ? C.background1 : C.text1,
    });
    tx(s, t[2], {
      x: x + 0.22, y: y + 1.42, w: tw - 0.44, h: 0.68,
      fontSize: 14, color: dark ? C.background1 : C.text2,
    });
  });
  s.addNotes("Cravar os números: 69.352 imagens rotuladas, 46,65 GB, cinco modelos de documento, três formas de fraude, zero pessoas reais. Quem organizou foi a Microblink Fraud Lab. A competição fechou em 16 de julho de 2026, ligada ao IJCAI-ECAI em Bremen.");
}

// ---------------------------------------------------------------------------
// 6. Composição
// ---------------------------------------------------------------------------
{
  const s = content("O dataset");
  kicker(s, "O dataset por dentro");
  title(s, "Legítimo e fraude, por país");
  s.addChart(pres.charts.BAR, [
    { name: "Legítimo", labels: ["Maurício", "Moçambique", "Benin", "Guiné", "Egito"], values: [8002, 8001, 8001, 8001, 8000] },
    { name: "Fraude", labels: ["Maurício", "Moçambique", "Benin", "Guiné", "Egito"], values: [5360, 5364, 5368, 5388, 7867] },
  ], {
    x: 0.35, y: 1.15, w: 8.35, h: 4.85,
    barDir: "bar",
    barGrouping: "stacked",
    barGapWidthPct: 45,
    showValue: true,
    dataLabelPosition: "ctr",
    dataLabelColor: "FFFFFF",
    dataLabelFontFace: "+mn-lt",
    dataLabelFontSize: 11,
    dataLabelFormatCode: "#,##0",
    showLegend: true,
    legendPos: "b",
    legendFontFace: "+mn-lt",
    legendFontSize: 12,
    legendColor: "1C2833",
    chartColors: ["2C6EAF", "C0473B"],
    catAxisLabelColor: "1C2833",
    valAxisLabelColor: "1C2833",
    catAxisLabelFontFace: "+mn-lt",
    valAxisLabelFontFace: "+mn-lt",
    catAxisLabelFontSize: 13,
    valAxisLabelFontSize: 11,
    valGridLine: { color: "E6EDF4", size: 0.5 },
    catGridLine: { style: "none" },
    showTitle: false,
    objectName: "barras por pais",
  });
  panel(s, 8.8, 1.4, 4.0, 4.4, C.background2, "totais");
  tx(s, "69.352", {
    x: 9.0, y: 1.6, w: 3.6, h: 0.62,
    fontSize: 32, bold: true, color: C.text1, align: "center",
  });
  tx(s, "imagens no treino", {
    x: 9.0, y: 2.22, w: 3.6, h: 0.32,
    fontSize: 14, color: C.text2, align: "center",
  });
  tx(s, "57,7%", {
    x: 9.0, y: 2.7, w: 3.6, h: 0.5,
    fontSize: 28, bold: true, color: C.accent4, align: "center",
  });
  tx(s, "legítimo", {
    x: 9.0, y: 3.2, w: 3.6, h: 0.28,
    fontSize: 14, color: C.text2, align: "center",
  });
  tx(s, "42,3%", {
    x: 9.0, y: 3.55, w: 3.6, h: 0.5,
    fontSize: 28, bold: true, color: C.accent3, align: "center",
  });
  tx(s, "fraude", {
    x: 9.0, y: 4.05, w: 3.6, h: 0.28,
    fontSize: 14, color: C.text2, align: "center",
  });
  tx(s, "Egito chega a 49,6% de fraude. Os outros ficam em torno de 40%.", {
    x: 9.05, y: 4.55, w: 3.5, h: 0.95,
    fontSize: 14, color: C.text1, align: "center",
  });
  take(s, [
    { text: "Há cerca de 8.000 legítimos em cada documento. ", options: {} },
    { text: "Só o Egito", options: { bold: true } },
    { text: " tem quase metade de fraudes, cerca de 2.500 a mais que os outros.", options: {} },
  ]);
  s.addNotes("Mostrar que o dataset não está desbalanceado de forma extrema: 58% legítimo e 42% fraude. Cada país tem cerca de 8.000 legítimos. O Egito é o diferente, quase meio a meio. Maurício é identidade; os outros quatro são carteira de motorista. Fonte: train_labels.csv.");
}

// ---------------------------------------------------------------------------
// 7. Três fraudes
// ---------------------------------------------------------------------------
{
  const s = content("O dataset");
  kicker(s, "O dataset por dentro");
  title(s, "Três formas de fraude");
  const kinds = [
    ["1", "Manipulação física", "Alguém altera o papel: cola outra foto, raspa ou cobre um dado. Deixa marca de recorte e de cor."],
    ["2", "Edição por IA generativa", "Uma IA troca nome, data ou rosto direto na imagem digital. O resultado parece limpo a olho nu."],
    ["3", "Imprimir e fotografar", "O falso é impresso e fotografado de novo com o celular. A nova foto esconde as marcas da edição."],
  ];
  const gap = 0.18;
  const w = (12.29 - 2 * gap) / 3;
  kinds.forEach((k, i) => {
    const x = 0.52 + i * (w + gap);
    panel(s, x, 1.28, w, 4.55, C.background2, k[1]);
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.24, y: 1.5, w: 0.52, h: 0.52,
      fill: fill(C.accent3),
      objectName: "numero fraude " + k[0],
    });
    tx(s, k[0], {
      x: x + 0.24, y: 1.5, w: 0.52, h: 0.52,
      fontSize: 20, bold: true, color: C.background1, align: "center", valign: "middle",
    });
    tx(s, k[1], {
      x: x + 0.24, y: 2.2, w: w - 0.48, h: 0.85,
      fontSize: 20, bold: true, color: C.text1,
    });
    tx(s, k[2], {
      x: x + 0.24, y: 3.15, w: w - 0.48, h: 2.35,
      fontSize: 16, color: C.text1,
    });
  });
  take(s, [
    { text: "No treino, 69.332 imagens são digitais e só 20 foram impressas e fotografadas. ", options: {} },
    { text: "Dessas 20, 14 são fraude (70%).", options: { bold: true } },
  ]);
  s.addNotes("Nomear as três fraudes sem entrar em como se faz cada uma. O ponto de dado: quase tudo é digital. Só 20 imagens são print-and-capture, e 14 delas são fraude. Por isso generalizar esse tipo de ataque é difícil neste recorte.");
}

// ---------------------------------------------------------------------------
// 8. X e Y
// ---------------------------------------------------------------------------
{
  const s = content("O dataset");
  kicker(s, "O dataset por dentro");
  title(s, "Tem X e tem Y");
  tx(s, [
    { text: "D  =  { ( ", options: {} },
    { text: "x", options: { italic: true, color: C.accent4 } },
    { text: " , ", options: {} },
    { text: "y", options: { italic: true, color: C.accent5 } },
    { text: " ) }", options: {} },
  ], {
    x: 0.52, y: 1.16, w: 12.29, h: 0.62,
    fontSize: 32, align: "center", color: C.text1,
  });
  tx(s, "x  =  a imagem do documento          y  =  0 legítimo  ·  1 fraude", {
    x: 0.52, y: 1.78, w: 12.29, h: 0.32,
    fontSize: 15, align: "center", color: C.text2,
  });
  function cellOpts(extra) {
    return Object.assign({
      align: "center", valign: "middle", color: "0D3B66",
      margin: [4, 6, 4, 6],
    }, extra || {});
  }
  function headOpts(color) {
    return {
      bold: true, color: "FFFFFF", align: "center", valign: "middle",
      margin: [6, 6, 6, 6], fill: fill(color),
    };
  }
  function row(id, img, label, digital, type) {
    return [
      { text: id, options: cellOpts() },
      { text: img, options: cellOpts() },
      { text: label, options: cellOpts({ bold: true, color: "1F7A4D" }) },
      { text: digital, options: cellOpts() },
      { text: type, options: cellOpts() },
    ];
  }
  s.addTable([
    [
      { text: "id", options: headOpts("0D3B66") },
      { text: "image_path  →  X", options: headOpts("2C6EAF") },
      { text: "label  →  Y", options: headOpts("1F7A4D") },
      { text: "is_digital", options: headOpts("0D3B66") },
      { text: "type", options: headOpts("0D3B66") },
    ],
    row("000184", "train/000184.jpeg", "0", "True", "EGYPT/DL"),
    row("004902", "train/004902.jpeg", "1", "True", "GUINEA/DL"),
    row("011330", "train/011330.jpeg", "0", "True", "BENIN/DL"),
    row("028441", "train/028441.jpeg", "1", "False", "MOZAMBIQUE/DL"),
    row("033102", "train/033102.jpeg", "1", "True", "MAURITIUS/ID"),
  ], {
    x: 0.52, y: 2.22, w: 12.29, h: 2.35,
    colW: [1.7, 3.5, 2.2, 2.2, 2.69],
    border: [{ pt: 0.5, color: "E6EDF4" }, { pt: 0.5, color: "E6EDF4" }, { pt: 0.5, color: "E6EDF4" }, { pt: 0.5, color: "E6EDF4" }],
    fontSize: 14,
    color: "0D3B66",
    valign: "middle",
    objectName: "tabela XY",
  });
  tx(s, "Linhas de exemplo, no formato do train_labels.csv. A licença não permite mostrar as imagens.", {
    x: 0.52, y: 4.62, w: 12.29, h: 0.28,
    fontSize: 12, color: C.text2,
  });
  s.addImage({
    path: path.join(ROOT, "aula/aula5_fluxo_supervisionado.png"),
    x: 0.9, y: 5.0, w: 11.5, h: 1.21,
    objectName: "fluxo da aula 5",
  });
  tx(s, "O mesmo fluxo da Aula 5: (X, y) → split → fit → predict → métricas. Fonte: Prof. Paulo Victor dos Santos.", {
    x: 0.52, y: 6.28, w: 12.29, h: 0.55,
    fontSize: 14, color: C.text2,
  });
  s.addNotes("Bater na fórmula. X é a imagem, Y é 0 ou 1. A tabela mostra as colunas reais. As linhas são exemplo de formato: a licença da Microblink não deixa publicar foto do dataset. Ligar com o fluxo da Aula 5, que está na figura.");
}

// ---------------------------------------------------------------------------
// 9. Features
// ---------------------------------------------------------------------------
pres.addSection({ title: "Técnicas da aula" });
{
  const s = content("Técnicas da aula");
  kicker(s, "Técnicas da aula");
  title(s, "A foto vira 64 números");
  const steps = [
    ["Foto", "JPEG do documento, em tamanhos variados"],
    ["128 × 128", "Todas as fotos ficam do mesmo tamanho"],
    ["64 números", "Cor, brilho, contraste e bordas"],
    ["0 ou 1", "fit no treino, predict no teste"],
  ];
  const aw = 0.64;
  const bw = (12.29 - 3 * aw) / 4;
  steps.forEach((st, i) => {
    const x = 0.52 + i * (bw + aw);
    panel(s, x, 1.26, bw, 1.72, i === 3 ? C.accent1 : C.background2, st[0]);
    tx(s, st[0], {
      x: x + 0.1, y: 1.4, w: bw - 0.2, h: 0.48,
      fontSize: 18, bold: true, color: i === 3 ? C.background1 : C.text1, align: "center",
    });
    tx(s, st[1], {
      x: x + 0.12, y: 1.92, w: bw - 0.24, h: 0.88,
      fontSize: 14, color: i === 3 ? C.background1 : C.text2, align: "center",
    });
    if (i < 3) {
      tx(s, "→", {
        x: x + bw, y: 1.88, w: aw, h: 0.42,
        fontSize: 20, bold: true, color: C.accent2, align: "center", valign: "middle",
      });
    }
  });
  const feats = [
    ["48", "Histograma", "Quantos pixels caem em 16 faixas de tom, no vermelho, no verde e no azul."],
    ["12", "Estatísticas", "Média, desvio, mínimo e máximo de cada cor."],
    ["2", "Brilho", "Média e desvio da imagem em tons de cinza."],
    ["2", "Gradiente", "Quanto um pixel muda em relação ao vizinho, na horizontal e na vertical."],
  ];
  const fg = 0.16;
  const fw = (12.29 - 3 * fg) / 4;
  feats.forEach((f, i) => {
    const x = 0.52 + i * (fw + fg);
    panel(s, x, 3.2, fw, 2.55, C.background2, f[1]);
    tx(s, f[0], {
      x: x + 0.18, y: 3.38, w: fw - 0.36, h: 0.5,
      fontSize: 28, bold: true, color: C.accent4,
    });
    tx(s, f[1], {
      x: x + 0.18, y: 3.92, w: fw - 0.36, h: 0.36,
      fontSize: 16, bold: true, color: C.text1,
    });
    tx(s, f[2], {
      x: x + 0.18, y: 4.36, w: fw - 0.36, h: 1.4,
      fontSize: 15, color: C.text1,
    });
  });
  take(s, [
    { text: "Edição, colagem e reimpressão deixam marca na cor e nas bordas. ", options: {} },
    { text: "Esses 64 números tentam capturar essa marca, sem rede neural.", options: { bold: true } },
  ]);
  s.addNotes("Explicar por que a foto não entra direto na regressão logística: ela vira um vetor de 64 números. 48 do histograma de cor, 12 de estatística, 2 de brilho e 2 de gradiente. A hipótese é que a fraude deixa marca nessas medidas.");
}

// ---------------------------------------------------------------------------
// 10. Classificação x regressão
// ---------------------------------------------------------------------------
{
  const s = content("Técnicas da aula");
  kicker(s, "Técnicas da aula");
  title(s, "É classificação, não regressão");
  panel(s, 0.52, 1.24, 6.05, 4.78, C.background2, "classificacao");
  tx(s, "Classificação  ·  qual classe?", {
    x: 0.72, y: 1.36, w: 5.65, h: 0.36,
    fontSize: 16, bold: true, color: C.accent3,
  });
  s.addImage({
    path: path.join(ROOT, "aula/aula6_cinco_fronteiras.png"),
    x: 0.78, y: 1.8, w: 5.55, h: 3.38,
    objectName: "fronteiras aula 6",
    sizing: { type: "contain", x: 0.78, y: 1.8, w: 5.55, h: 3.38 },
  });
  tx(s, "Aula 6. A saída é uma classe. Usamos a logística e a árvore.", {
    x: 0.72, y: 5.28, w: 5.65, h: 0.55,
    fontSize: 14, color: C.text2,
  });
  panel(s, 6.76, 1.24, 6.05, 4.78, C.background2, "regressao");
  tx(s, "Regressão  ·  qual valor?", {
    x: 6.96, y: 1.36, w: 5.65, h: 0.36,
    fontSize: 16, bold: true, color: C.accent6,
  });
  s.addImage({
    path: path.join(ROOT, "aula/aula5_reta_regressao.png"),
    x: 7.05, y: 1.85, w: 5.5, h: 3.3,
    objectName: "reta aula 5",
    sizing: { type: "contain", x: 7.05, y: 1.85, w: 5.5, h: 3.3 },
  });
  tx(s, "Aula 5. A saída é um número. Métricas: MAE, MSE, R².", {
    x: 6.96, y: 5.28, w: 5.65, h: 0.55,
    fontSize: 14, color: C.text2,
  });
  take(s, [
    { text: "No FREUID, Y só vale 0 ou 1. ", options: { bold: true } },
    { text: "A avaliação usa a matriz de confusão, não o MAE.", options: {} },
  ]);
  s.addNotes("Contrastar as duas tarefas com as figuras das aulas. Classificação responde qual classe. Regressão responde qual valor. O Y do FREUID é binário, então é classificação. Não vamos falar de MAE aqui.");
}

// ---------------------------------------------------------------------------
// 11. Split
// ---------------------------------------------------------------------------
{
  const s = content("Técnicas da aula");
  kicker(s, "Técnicas da aula");
  title(s, "Como dividimos as 544 fotos");
  tx(s, "O modelo treina em três documentos e é testado em dois que ele nunca viu.", {
    x: 0.52, y: 1.18, w: 12.29, h: 0.36,
    fontSize: 16, color: C.text1,
  });
  const parts = [
    { w: 8.9, fill: "0B2F4A", color: "FFFFFF", label: "394  ·  treino" },
    { w: 2.46, fill: "C4A046", color: "0D3B66", label: "109  ·  Egito" },
    { w: 0.93, fill: "C0473B", color: "FFFFFF", label: "41" },
  ];
  let px = 0.52;
  parts.forEach((p) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: px, y: 1.66, w: p.w, h: 0.62,
      fill: fill(p.fill),
      rectRadius: 0.06,
      objectName: p.label,
    });
    tx(s, p.label, {
      x: px, y: 1.66, w: p.w, h: 0.62,
      fontSize: p.w < 1.2 ? 12 : 15, bold: true, color: p.color, align: "center", valign: "middle",
    });
    px += p.w;
  });
  const cards = [
    ["Treino  ·  394", "Benin, Guiné e Maurício. O fit acontece aqui. O StandardScaler também calcula média e desvio só com estas fotos.", "0B2F4A"],
    ["Teste A  ·  Egito  ·  109", "28 fraudes e 81 legítimos. Documento novo para o modelo. É o teste principal.", "C4A046"],
    ["Teste B  ·  Moçambique  ·  41", "Outro documento novo, separado de propósito. Mostra se o que foi aprendido vale em outro país.", "C0473B"],
  ];
  cards.forEach((c, i) => {
    const x = 0.52 + i * 4.15;
    panel(s, x, 2.55, 3.99, 2.7, C.background2, c[0]);
    tx(s, c[0], {
      x: x + 0.22, y: 2.78, w: 3.55, h: 0.85,
      fontSize: 18, bold: true, color: C.text1,
    });
    tx(s, c[1], {
      x: x + 0.22, y: 3.68, w: 3.55, h: 1.4,
      fontSize: 15, color: C.text1,
    });
  });
  take(s, [
    { text: "544 imagens são 0,8% do dataset. ", options: { bold: true } },
    { text: "Bastam para comparar os modelos da aula. Não bastam para disputar o placar da competição.", options: {} },
  ]);
  s.addNotes("Deixar claro o desenho do teste. Treino em Benin, Guiné e Maurício. Egito é o teste principal, com 109 fotos. Moçambique fica de fora de propósito, para ver generalização. 544 fotos são menos de 1% das 69.352. É um recorte de aula, não uma submissão do Kaggle.");
}

// ---------------------------------------------------------------------------
// 12. Modelos
// ---------------------------------------------------------------------------
{
  const s = content("Técnicas da aula");
  kicker(s, "Técnicas da aula");
  title(s, "Dois modelos da aula");
  panel(s, 0.52, 1.24, 6.05, 4.78, C.background2, "logistica");
  tx(s, "Regressão logística", {
    x: 0.74, y: 1.4, w: 5.6, h: 0.4,
    fontSize: 20, bold: true, color: C.accent4,
  });
  tx(s, [
    { text: "p  =  1 / (1 + e", options: {} },
    { text: "−z", options: { superscript: true } },
    { text: ")", options: {} },
  ], {
    x: 0.74, y: 1.9, w: 5.6, h: 0.5,
    fontSize: 22, bold: true, color: C.text1,
  });
  tx(s, "Soma os 64 números com pesos. A sigmoide transforma essa soma numa chance entre 0 e 1. Acima de 0,5, a foto é chamada de fraude.", {
    x: 0.74, y: 2.55, w: 5.6, h: 1.35,
    fontSize: 16, color: C.text1,
  });
  tx(s, "StandardScaler antes do fit.\nclass_weight = balanced, porque as classes não têm o mesmo tamanho.", {
    x: 0.74, y: 4.1, w: 5.6, h: 1.5,
    fontSize: 15, color: C.text2,
  });
  panel(s, 6.76, 1.24, 6.05, 4.78, C.background2, "floresta");
  tx(s, "Random Forest", {
    x: 6.98, y: 1.4, w: 5.6, h: 0.38,
    fontSize: 20, bold: true, color: C.accent6,
  });
  s.addImage({
    path: path.join(ROOT, "aula/aula6_arvore_decisao.png"),
    x: 7.05, y: 1.85, w: 5.5, h: 2.15,
    objectName: "arvore aula 6",
    sizing: { type: "contain", x: 7.05, y: 1.85, w: 5.5, h: 2.15 },
  });
  tx(s, "300 árvores votam. A classe com mais votos ganha. Cada árvore pergunta se um dos 64 números passa de um corte.", {
    x: 6.98, y: 4.1, w: 5.6, h: 1.05,
    fontSize: 15, color: C.text1,
  });
  tx(s, "Profundidade até 20  ·  sem scaler", {
    x: 6.98, y: 5.2, w: 5.6, h: 0.4,
    fontSize: 14, color: C.text2,
  });
  take(s, [
    { text: "Os dois seguem o fluxo do Scikit-Learn: ", options: {} },
    { text: "fit(X_treino, y_treino)  →  predict(X_teste).", options: { bold: true } },
  ]);
  s.addNotes("Logística: uma soma com pesos passa pela sigmoide e vira probabilidade. O corte usado foi 0,5. Floresta: 300 árvores, profundidade máxima 20, voto da maioria. A figura é uma árvore da Aula 6, só para lembrar a ideia. A floresta é muitas árvores dessas.");
}

// ---------------------------------------------------------------------------
// 13. Matriz
// ---------------------------------------------------------------------------
pres.addSection({ title: "Resultados" });
{
  const s = content("Resultados");
  kicker(s, "Resultados");
  title(s, "Matriz de confusão no Egito");
  tx(s, "109 imagens  ·  28 fraudes e 81 legítimos. O modelo nunca treinou neste documento.", {
    x: 0.52, y: 1.14, w: 12.29, h: 0.32,
    fontSize: 15, color: C.text2,
  });

  function matrix(slide, x, name, colorName, cells, metrics) {
    tx(slide, name, {
      x, y: 1.5, w: 5.7, h: 0.36,
      fontSize: 18, bold: true, color: colorName,
    });
    tx(slide, "previu fraude", {
      x: x + 1.45, y: 1.92, w: 1.95, h: 0.32,
      fontSize: 12, bold: true, color: C.text2, align: "center",
    });
    tx(slide, "previu legítimo", {
      x: x + 3.5, y: 1.92, w: 1.95, h: 0.32,
      fontSize: 12, bold: true, color: C.text2, align: "center",
    });
    const rows = [
      ["é fraude\n(28)", cells[0], cells[1]],
      ["é legítimo\n(81)", cells[2], cells[3]],
    ];
    rows.forEach((r, ri) => {
      const y = 2.3 + ri * 1.22;
      tx(slide, r[0], {
        x, y, w: 1.35, h: 1.1,
        fontSize: 13, bold: true, color: C.text2, align: "center", valign: "middle",
      });
      [r[1], r[2]].forEach((cell, ci) => {
        const cx = x + 1.45 + ci * 2.05;
        panel(slide, cx, y, 1.95, 1.1, cell.fill, cell.label);
        tx(slide, String(cell.n), {
          x: cx, y: y + 0.08, w: 1.95, h: 0.55,
          fontSize: 28, bold: true, color: cell.tc, align: "center",
        });
        tx(slide, cell.label, {
          x: cx + 0.08, y: y + 0.64, w: 1.79, h: 0.36,
          fontSize: 12, color: cell.tc, align: "center",
        });
      });
    });
    metrics.forEach((m, i) => {
      const mx = x + i * 1.9;
      tx(slide, m[0], {
        x: mx, y: 4.82, w: 1.8, h: 0.24,
        fontSize: 12, color: C.text2, align: "center",
      });
      tx(slide, m[1], {
        x: mx, y: 5.04, w: 1.8, h: 0.4,
        fontSize: 22, bold: true, color: C.text1, align: "center",
      });
    });
  }

  const soft = C.background2;
  const ink = C.text1;
  const white = C.background1;
  matrix(s, 0.52, "Regressão logística", C.accent4, [
    { n: 23, label: "fraude pega", fill: soft, tc: C.accent5 },
    { n: 5, label: "fraude que passou", fill: C.accent3, tc: white },
    { n: 27, label: "alarme falso", fill: soft, tc: C.accent6 },
    { n: 54, label: "legítimo aceito", fill: soft, tc: C.accent4 },
  ], [["Acurácia", "0,71"], ["Precisão", "0,46"], ["Revocação", "0,82"]]);

  matrix(s, 6.9, "Random Forest", C.accent6, [
    { n: 19, label: "fraude pega", fill: soft, tc: C.accent5 },
    { n: 9, label: "fraude que passou", fill: C.accent3, tc: white },
    { n: 11, label: "alarme falso", fill: soft, tc: C.accent6 },
    { n: 70, label: "legítimo aceito", fill: soft, tc: C.accent4 },
  ], [["Acurácia", "0,82"], ["Precisão", "0,63"], ["Revocação", "0,68"]]);

  take(s, [
    { text: "A logística deixa passar menos fraude (5 contra 9). ", options: {} },
    { text: "A floresta dá menos alarme falso (11 contra 27). ", options: {} },
    { text: "No balcão, a fraude que passa é o erro mais caro.", options: { bold: true } },
  ]);
  s.addNotes("Ler a matriz da esquerda para a direita. Logística: 23 fraudes pegas, 5 que passaram, 27 alarmes falsos. Floresta: 19 pegas, 9 que passaram, 11 alarmes falsos. Acurácia maior da floresta não significa que ela é melhor para o órgão. O erro caro é a fraude que passa, e aí a logística vai melhor: revocação 0,82 contra 0,68.");
}

// ---------------------------------------------------------------------------
// 14. Generalização
// ---------------------------------------------------------------------------
{
  const s = content("Resultados");
  kicker(s, "Resultados");
  title(s, "Funciona no Egito, cai fora");
  s.addImage({
    path: path.join(ROOT, "roc_compare_id.png"),
    x: 0.4, y: 1.2, w: 5.7, h: 4.75,
    objectName: "curva ROC",
    sizing: { type: "contain", x: 0.4, y: 1.2, w: 5.7, h: 4.75 },
  });
  tx(s, "Curva ROC no Egito. A diagonal tracejada é o chute.", {
    x: 0.52, y: 5.95, w: 5.6, h: 0.4,
    fontSize: 13, color: C.text2,
  });
  s.addChart(pres.charts.BAR, [
    { name: "Logística", labels: ["Egito", "Moçambique"], values: [0.889, 0.687] },
    { name: "Floresta", labels: ["Egito", "Moçambique"], values: [0.808, 0.691] },
  ], {
    x: 6.35, y: 1.15, w: 6.55, h: 4.15,
    barDir: "col",
    barGrouping: "clustered",
    barGapWidthPct: 50,
    showValue: true,
    dataLabelPosition: "outEnd",
    dataLabelColor: "0D3B66",
    dataLabelFontFace: "+mn-lt",
    dataLabelFontSize: 12,
    dataLabelFormatCode: "0.00",
    showLegend: true,
    legendPos: "b",
    legendFontFace: "+mn-lt",
    legendFontSize: 12,
    legendColor: "1C2833",
    showTitle: true,
    title: "AUC  ·  0,50 é o chute e 1,00 é o perfeito",
    titleFontFace: "+mn-lt",
    titleFontSize: 13,
    titleColor: "0D3B66",
    chartColors: ["2C6EAF", "C47B2B"],
    catAxisLabelColor: "1C2833",
    valAxisLabelColor: "1C2833",
    catAxisLabelFontFace: "+mn-lt",
    valAxisLabelFontFace: "+mn-lt",
    catAxisLabelFontSize: 13,
    valAxisLabelFontSize: 11,
    valAxisMinValue: 0,
    valAxisMaxValue: 1.15,
    valGridLine: { color: "E6EDF4", size: 0.5 },
    catGridLine: { style: "none" },
    objectName: "auc por teste",
  });
  panel(s, 6.55, 5.5, 6.2, 1.15, C.background2, "nota mocambique");
  tx(s, "Em Moçambique a acurácia dos dois cai para 0,51. Eles acham as fraudes porque passam a chamar quase tudo de fraude.", {
    x: 6.75, y: 5.66, w: 5.85, h: 0.85,
    fontSize: 14, color: C.text1, valign: "middle",
  });
  s.addNotes("A curva ROC do Egito fica bem acima da diagonal: AUC 0,89 na logística e 0,81 na floresta. Em Moçambique os dois caem para cerca de 0,69. A acurácia de 0,51 engana: o modelo marca quase tudo como fraude, então pega as fraudes e também os legítimos. Cor e textura aprendem o documento visto, não um detector universal.");
}

// ---------------------------------------------------------------------------
// 15. Fecho
// ---------------------------------------------------------------------------
pres.addSection({ title: "Conclusão" });
{
  const s = pres.addSlide({ masterName: "Fecho", sectionTitle: "Conclusão" });
  tx(s, "CONCLUSÃO", {
    x: 0.52, y: 0.08, w: 12.2, h: 0.24,
    fontSize: 12, bold: true, color: C.accent2, charSpacing: 1.2, margin: 0,
  });
  title(s, "O que este dataset mostrou");
  const cols = [
    ["Por que o FREUID", [
      "Problema do serviço público: validar o documento no cadastro.",
      "Tem X (a imagem) e Y (0 ou 1).",
      "69.352 imagens, sem dado pessoal real.",
    ]],
    ["O que os números sustentam", [
      "No Egito, AUC de 0,81 a 0,89, acima do chute.",
      "A logística pega mais fraude. A floresta erra menos legítimos.",
      "Com 109 imagens não há um vencedor definitivo.",
      "Em outro documento, Moçambique, o resultado cai.",
    ]],
    ["Próximos passos", [
      "Treinar com mais imagens do dataset completo.",
      "Testar uma CNN que olhe a foto inteira.",
      "Ajustar o corte de 0,5 pelo custo de cada erro.",
    ]],
  ];
  cols.forEach((col, i) => {
    const x = 0.52 + i * 4.2;
    panel(s, x, 1.2, 4.02, 4.15, C.background1, col[0]);
    tx(s, col[0], {
      x: x + 0.2, y: 1.36, w: 3.62, h: 0.7,
      fontSize: 16, bold: true, color: C.text1,
    });
    tx(s, col[1].map((line, idx) => ({
      text: line,
      options: { bullet: true, breakLine: idx < col[1].length - 1 },
    })), {
      x: x + 0.2, y: 2.1, w: 3.62, h: 3.0,
      fontSize: 14, color: C.text1, paraSpaceAfter: 8, valign: "top",
    });
  });
  tx(s, "A IA entra como filtro de risco antes do servidor. Ela não carimba nada sozinha.", {
    x: 0.52, y: 5.5, w: 12.29, h: 0.45,
    fontSize: 18, bold: true, color: C.accent2,
  });
  tx(s, "Microblink Fraud Lab. The FREUID Challenge 2026 – IJCAI-ECAI. Kaggle, 2026. Uso acadêmico, sem redistribuir as imagens.", {
    x: 0.52, y: 6.1, w: 12.29, h: 0.7,
    fontSize: 13, color: C.background1,
  });
  s.addNotes("Fechar em três colunas: por que o dataset serve, o que os números realmente sustentam, e o que viria depois. Não declarar um modelo vencedor. Repetir a frase final: a IA filtra risco e o servidor decide. Citar Microblink e o uso acadêmico se sobrar tempo para pergunta.");
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
