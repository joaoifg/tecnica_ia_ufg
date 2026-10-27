"""EDA dos rótulos FREUID — só CSVs, sem imagens."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"


def load_labels(name: str) -> pd.DataFrame:
    path = DATA / name
    if not path.exists():
        # ZIP solto ou CSV dentro de zip já extraído
        zipped = DATA / f"{name}.zip"
        if zipped.exists():
            import zipfile

            with zipfile.ZipFile(zipped) as zf:
                zf.extractall(DATA)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    return pd.read_csv(path)


def summarize(df: pd.DataFrame, titulo: str) -> str:
    lines = [f"## {titulo}", ""]
    lines.append(f"- **Linhas:** {len(df):,}")
    lines.append(f"- **Colunas:** {', '.join(df.columns.astype(str))}")
    lines.append("")

    if "label" in df.columns:
        vc = df["label"].value_counts().sort_index()
        lines.append("### Distribuição de `label`")
        lines.append("")
        lines.append("| label | significado | n | % |")
        lines.append("|---|---|---:|---:|")
        meaning = {0: "legítimo (bona-fide)", 1: "fraude (ataque)"}
        for k, n in vc.items():
            pct = 100 * n / len(df)
            lines.append(f"| {k} | {meaning.get(k, '?')} | {n:,} | {pct:.1f}% |")
        lines.append("")

    if "is_digital" in df.columns:
        vc = df["is_digital"].value_counts().sort_index()
        lines.append("### Distribuição de `is_digital`")
        lines.append("")
        lines.append("| is_digital | significado | n | % |")
        lines.append("|---|---|---:|---:|")
        meaning = {0: "recapturado (print-and-capture)", 1: "totalmente digital"}
        for k, n in vc.items():
            pct = 100 * n / len(df)
            lines.append(f"| {k} | {meaning.get(k, '?')} | {n:,} | {pct:.1f}% |")
        lines.append("")

    if "type" in df.columns:
        vc = df["type"].value_counts()
        lines.append(f"### Tipos de documento (`type`) — {vc.size} distintos")
        lines.append("")
        lines.append("| type | n | % |")
        lines.append("|---|---:|---:|")
        for k, n in vc.items():
            pct = 100 * n / len(df)
            lines.append(f"| {k} | {n:,} | {pct:.1f}% |")
        lines.append("")

        if "label" in df.columns:
            cross = pd.crosstab(df["type"], df["label"], margins=True)
            cross = cross.rename(columns={0: "legítimo", 1: "fraude", "All": "total"})
            lines.append("### `type` × `label`")
            lines.append("")
            lines.append(cross.to_markdown())
            lines.append("")

        if "is_digital" in df.columns and "label" in df.columns:
            cross2 = pd.crosstab(
                [df["is_digital"], df["type"]],
                df["label"],
                margins=False,
            )
            # resumo compacto: fraude rate por is_digital
            by_dig = df.groupby("is_digital")["label"].agg(["count", "mean"])
            lines.append("### Taxa de fraude por `is_digital`")
            lines.append("")
            lines.append("| is_digital | n | taxa fraude |")
            lines.append("|---|---:|---:|")
            for idx, row in by_dig.iterrows():
                lines.append(f"| {idx} | {int(row['count']):,} | {100 * row['mean']:.1f}% |")
            lines.append("")

    return "\n".join(lines)


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    parts = [
        "# EDA FREUID 2026 — rótulos",
        "",
        "Gerado automaticamente a partir dos CSVs (sem imagens).",
        "",
        "> Dataset: The FREUID Challenge 2026 – IJCAI-ECAI (Microblink Fraud Lab).",
        "> Uso apenas acadêmico; dados não versionados.",
        "",
    ]

    sample_name = "train_sample_labels.csv"
    full_name = "train_labels.csv"

    if (DATA / sample_name).exists() or (DATA / f"{sample_name}.zip").exists():
        sample = load_labels(sample_name)
        parts.append(summarize(sample, f"`{sample_name}` (recorte para começar)"))
    else:
        parts.append(f"## `{sample_name}`\n\nArquivo ainda não baixado.\n")

    if (DATA / full_name).exists() or (DATA / f"{full_name}.zip").exists():
        full = load_labels(full_name)
        parts.append(summarize(full, f"`{full_name}` (treino completo)"))
    else:
        parts.append(f"## `{full_name}`\n\nArquivo ainda não baixado.\n")

    out = REPORTS / "eda.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Relatório salvo em {out}")


if __name__ == "__main__":
    main()
