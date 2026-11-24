"""Kaggle (CPU): exporta amostra estratificada de 25 mil imagens de treino,
reduzidas para lado maior de 960 px, num único zip para uso local.
(Download arquivo-a-arquivo pela API é bloqueado por limite de taxa.)"""
import os, zipfile, io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pandas as pd
from PIL import Image

def _achar_csv():
    for d, ds, fs in os.walk("/kaggle/input", followlinks=True):
        if d.count("/") <= 6: print("DIR", d, ds[:5], [f for f in fs if not f.endswith(".jpeg")][:8], flush=True)
        if "train_labels.csv" in fs: return Path(d)
        ds[:] = [x for x in ds if x not in ("train", "public_test", "private_test", "test")]
    raise FileNotFoundError("train_labels.csv")
raiz = _achar_csv()
df = pd.read_csv(raiz / "train_labels.csv")
idx = {}
for d, _, fs in os.walk(raiz / "train", followlinks=True):
    for f in fs:
        idx[f[:-5]] = os.path.join(d, f)
raros = df[~df.is_digital]
resto = df[df.is_digital]
frac = (25000 - len(raros)) / len(resto)
am = pd.concat([raros, resto.groupby(["type", "label"], group_keys=False).sample(frac=frac, random_state=42)])
am = am.sample(frac=1, random_state=42).reset_index(drop=True)
print(len(am), am.groupby(["type", "label"]).size())

def reduzir(i):
    im = Image.open(idx[i]); w, h = im.size
    im.draft("RGB", (960, 960)); im = im.convert("RGB"); im.thumbnail((960, 960), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=93)
    return i, b.getvalue(), w, h, os.path.getsize(idx[i])

out = []
with zipfile.ZipFile("/kaggle/working/amostra_960.zip", "w", zipfile.ZIP_STORED) as z, ThreadPoolExecutor(8) as ex:
    for k, (i, dados, w, h, kb) in enumerate(ex.map(reduzir, am.id)):
        z.writestr(f"train/{i}.jpeg", dados)
        out.append((i, w, h, kb / 1024))
        if k % 2000 == 0: print(k, flush=True)
    orig = pd.DataFrame(out, columns=["id", "largura_orig", "altura_orig", "kb_orig"])
    z.writestr("amostra.csv", am.merge(orig, on="id").to_csv(index=False))
print("ok", os.path.getsize("/kaggle/working/amostra_960.zip") / 1e9, "GB")
