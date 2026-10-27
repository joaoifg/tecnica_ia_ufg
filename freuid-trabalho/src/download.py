"""Download estratificado e retomável das imagens do train/."""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
from sklearn.model_selection import train_test_split
from tqdm import tqdm

from config import (
    COMPETITION,
    DATA,
    N_JOBS_DOWNLOAD,
    RANDOM_SEED,
    REMOTE_TRAIN_PREFIX,
    SUBSET_DIR,
    SUBSET_MANIFEST,
    SUBSET_SIZE,
)

LOG = DATA / "download_errors.log"
logging.basicConfig(filename=LOG, level=logging.INFO, format="%(asctime)s %(message)s")


def build_subset(n: int = SUBSET_SIZE) -> pd.DataFrame:
    """Amostra estratificada por label + type (e is_digital quando possível)."""
    df = pd.read_csv(DATA / "train_labels.csv")
    # is_digital=False é raro (~20); inclui todos os recapturados
    rare = df[df["is_digital"] == False].copy()  # noqa: E712
    rest = df[df["is_digital"] == True].copy()  # noqa: E712
    n_rest = max(0, n - len(rare))
    # estratifica pelo par label|type
    rest["strata"] = rest["label"].astype(str) + "|" + rest["type"].astype(str)
    # se algum estrato for muito pequeno, cai para label
    counts = rest["strata"].value_counts()
    if (counts < 2).any() or n_rest < len(counts) * 2:
        sample, _ = train_test_split(
            rest,
            train_size=min(n_rest, len(rest)),
            stratify=rest["label"],
            random_state=RANDOM_SEED,
        )
    else:
        frac = n_rest / len(rest)
        parts = []
        for _, g in rest.groupby("strata"):
            k = max(1, int(round(len(g) * frac)))
            k = min(k, len(g))
            parts.append(g.sample(n=k, random_state=RANDOM_SEED))
        sample = pd.concat(parts, ignore_index=True)
        if len(sample) > n_rest:
            sample = sample.sample(n=n_rest, random_state=RANDOM_SEED)
        elif len(sample) < n_rest:
            missing = n_rest - len(sample)
            leftover = rest.drop(index=sample.index, errors="ignore")
            if len(leftover) >= missing:
                sample = pd.concat(
                    [sample, leftover.sample(n=missing, random_state=RANDOM_SEED)],
                    ignore_index=True,
                )
    out = pd.concat([rare, sample], ignore_index=True).drop_duplicates(subset=["id"])
    if len(out) > n:
        # preserva todos os rare
        keep_rare = out[out["is_digital"] == False]  # noqa: E712
        keep_rest = out[out["is_digital"] == True].sample(  # noqa: E712
            n=n - len(keep_rare), random_state=RANDOM_SEED
        )
        out = pd.concat([keep_rare, keep_rest], ignore_index=True)
    out = out.drop(columns=["strata"], errors="ignore")
    SUBSET_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(SUBSET_MANIFEST, index=False)
    return out


def _remote_name(image_path: str) -> str:
    # CSV: train/<id>.jpeg → remoto: train/train/<id>.jpeg
    name = Path(image_path).name
    return f"{REMOTE_TRAIN_PREFIX}{name}"


def _local_path(image_path: str) -> Path:
    name = Path(image_path).name
    return SUBSET_DIR / name


def _download_one(image_path: str) -> tuple[str, bool, str]:
    dest = _local_path(image_path)
    if dest.exists() and dest.stat().st_size > 0:
        return image_path, True, "exists"
    dest.parent.mkdir(parents=True, exist_ok=True)
    remote = _remote_name(image_path)
    # pasta tmp exclusiva por arquivo (threads)
    tmp_dir = dest.parent / "_tmp" / Path(image_path).stem
    tmp_dir.mkdir(parents=True, exist_ok=True)
    last = ""
    for attempt in range(3):
        try:
            api = KaggleApi()
            api.authenticate()
            api.competition_download_file(
                COMPETITION,
                remote,
                path=str(tmp_dir),
                quiet=True,
                force=True,
            )
            name = Path(image_path).name
            candidates = list(tmp_dir.rglob(name))
            if not candidates:
                candidates = [p for p in tmp_dir.rglob("*") if p.is_file()]
            if not candidates:
                raise FileNotFoundError(f"download vazio: {remote}")
            src = candidates[0]
            if dest.exists():
                dest.unlink()
            src.replace(dest)
            for p in tmp_dir.rglob("*"):
                if p.is_file():
                    p.unlink(missing_ok=True)
            try:
                tmp_dir.rmdir()
            except OSError:
                pass
            return image_path, True, "ok"
        except Exception as exc:  # noqa: BLE001
            wait = 1.5 * (attempt + 1)
            logging.info("retry %s attempt=%s err=%s", remote, attempt, exc)
            time.sleep(wait)
            last = str(exc)
    logging.info("FAIL %s %s", remote, last)
    return image_path, False, last


def download_manifest(manifest: pd.DataFrame | None = None) -> None:
    if manifest is None:
        if SUBSET_MANIFEST.exists():
            manifest = pd.read_csv(SUBSET_MANIFEST)
        else:
            manifest = build_subset()
    paths = manifest["image_path"].tolist()
    ok = fail = 0
    with ThreadPoolExecutor(max_workers=N_JOBS_DOWNLOAD) as ex:
        futs = {ex.submit(_download_one, p): p for p in paths}
        for fut in tqdm(as_completed(futs), total=len(futs), desc="download"):
            _, success, _ = fut.result()
            if success:
                ok += 1
            else:
                fail += 1
    print(f"Download concluido: ok={ok} fail={fail} -> {SUBSET_DIR}")
    print(f"Falhas em {LOG}" if fail else "Sem falhas.")


def main() -> None:
    print(f"Montando subset de {SUBSET_SIZE} imagens...")
    mf = build_subset()
    print(mf["label"].value_counts().to_string())
    print("is_digital:\n", mf["is_digital"].value_counts().to_string())
    print("types:", mf["type"].nunique())
    download_manifest(mf)


if __name__ == "__main__":
    main()
