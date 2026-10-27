"""Baixa apenas os CSVs de rótulos do FREUID (sem imagens)."""

from __future__ import annotations

import zipfile
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

COMPETITION = "the-freuid-challenge-2026-ijcai-ecai"
FILES = ("train_sample_labels.csv", "train_labels.csv")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def _unzip_if_needed(path: Path) -> None:
    zips = list(DATA.glob("*.zip"))
    for z in zips:
        with zipfile.ZipFile(z) as zf:
            zf.extractall(DATA)
        z.unlink(missing_ok=True)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    api = KaggleApi()
    api.authenticate()

    for name in FILES:
        target = DATA / name
        if target.exists():
            print(f"Já existe: {target}")
            continue
        print(f"Baixando {name} ...")
        api.competition_download_file(
            COMPETITION,
            name,
            path=str(DATA),
            quiet=False,
        )
        _unzip_if_needed(target)
        # A CLI às vezes salva como name.zip
        maybe_zip = DATA / f"{name}.zip"
        if maybe_zip.exists() and not target.exists():
            with zipfile.ZipFile(maybe_zip) as zf:
                zf.extractall(DATA)
            maybe_zip.unlink(missing_ok=True)
        print(f"OK: {target if target.exists() else 'verifique data/'}")


if __name__ == "__main__":
    main()
