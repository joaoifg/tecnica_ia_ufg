import sys
"""CNN para detecção de fraude documental (FREUID 2026).

O mesmo script roda no PC (amostra local) e no Kaggle (dataset completo).

Ideias principais (explicadas no notebook):
  1. Transfer learning: EfficientNet pré-treinada no ImageNet, ajuste fino.
  2. Validação fora de distribuição (OOD): um tipo de documento inteiro fica
     de fora do treino, simulando os "dois tipos novos" do teste privado.
  3. Aumento de dados que imita recaptura (impressão + foto): perspectiva,
     desfoque, ruído, variação de cor e recompressão JPEG. O treino é quase
     todo digital, mas o teste privado enfatiza documentos capturados.

Uso:
  python src/cnn.py --modo ood   --holdout MOZAMBIQUE/DL   # avalia generalização
  python src/cnn.py --modo final --prever-teste           # treina tudo + submissão
"""

from __future__ import annotations

import argparse
import io
import json
import os
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import timm
import torch
import torch.nn as nn
from PIL import Image, ImageFilter
from sklearn.metrics import roc_auc_score, roc_curve
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms as T

NO_KAGGLE = Path("/kaggle/input").exists()
H, W = 384, 608  # proporção de um documento ID-1 (~1,58 : 1)
MEDIA, DESVIO = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)


# ---------------------------------------------------------------- métrica
def tpr_em_fpr(y, p, alvo: float = 0.01) -> float:
    """Recall de fraude quando só 1% dos legítimos é barrado (1 - APCER@1%BPCER)."""
    fpr, tpr, _ = roc_curve(y, p)
    return float(tpr[fpr <= alvo].max()) if (fpr <= alvo).any() else 0.0


def metricas(y, p) -> dict:
    y, p = np.asarray(y), np.asarray(p)
    if len(np.unique(y)) < 2:
        return {"n": int(len(y)), "acuracia@0.5": float(((p > 0.5) == y).mean())}
    auc = roc_auc_score(y, p)
    tpr1 = tpr_em_fpr(y, p)
    return {
        "n": int(len(y)),
        "roc_auc": float(auc),
        "audet": float(1 - auc),
        "apcer@1%bpcer": float(1 - tpr1),
        "freuid_aprox": float(1 - 2 * auc * tpr1 / (auc + tpr1 + 1e-12)),  # menor = melhor
        "acuracia@0.5": float(((p > 0.5) == y).mean()),
    }


# ---------------------------------------------------------------- dados
def achar_raiz() -> Path:
    if NO_KAGGLE:
        return next(Path("/kaggle/input").rglob("train_labels.csv")).parent
    return Path(os.environ.get("FREUID_DATA", r"C:\freuid\data"))


def indexar_jpegs(raiz: Path) -> dict[str, str]:
    """id -> caminho, varrendo todas as pastas de imagens (train/, public_test/, private_test/)."""
    idx: dict[str, str] = {}
    pilha = [raiz]
    while pilha:
        d = pilha.pop()
        with os.scandir(d) as it:
            for e in it:
                if e.is_dir():
                    pilha.append(e.path)
                elif e.name.endswith(".jpeg"):
                    idx[e.name[:-5]] = e.path
    return idx


class Recaptura:
    """Simula 'imprimir e fotografar' com probabilidade p."""

    def __init__(self, p: float = 0.5):
        self.p = p

    def __call__(self, im: Image.Image) -> Image.Image:
        if random.random() > self.p:
            return im
        if random.random() < 0.5:
            im = im.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 1.5)))
        if random.random() < 0.7:  # recompressão JPEG
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=random.randint(40, 90))
            im = Image.open(buf).convert("RGB")
        if random.random() < 0.4:  # ruído de sensor
            a = np.asarray(im, dtype=np.float32)
            a += np.random.normal(0, random.uniform(2, 8), a.shape)
            im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        return im


def transformacoes(treino: bool):
    base = [T.ToTensor(), T.Normalize(MEDIA, DESVIO)]
    if not treino:
        return T.Compose([T.Resize((H, W))] + base)
    return T.Compose(
        [
            T.RandomResizedCrop((H, W), scale=(0.8, 1.0), ratio=(1.4, 1.75)),
            T.RandomPerspective(distortion_scale=0.15, p=0.4),
            T.RandomRotation(4),
            T.ColorJitter(0.3, 0.3, 0.3, 0.03),
            Recaptura(p=0.5),
        ]
        + base
        + [T.RandomErasing(p=0.2, scale=(0.01, 0.05))]
    )


class Docs(Dataset):
    def __init__(self, caminhos, rotulos, treino: bool):
        self.c, self.y, self.tf = list(caminhos), np.asarray(rotulos, np.float32), transformacoes(treino)

    def __len__(self):
        return len(self.c)

    def __getitem__(self, i):
        try:
            im = Image.open(self.c[i])
            im.draft("RGB", (W * 2, H * 2))  # decodifica JPEG já reduzido: bem mais rápido
            im = im.convert("RGB")
        except Exception:  # arquivo corrompido: imagem cinza (raríssimo)
            im = Image.new("RGB", (W, H), (128, 128, 128))
        return self.tf(im), self.y[i]


# ---------------------------------------------------------------- treino
def carregar(ds, bs, embaralhar, workers):
    return DataLoader(ds, bs, shuffle=embaralhar, num_workers=workers, pin_memory=True,
                      persistent_workers=workers > 0, drop_last=embaralhar)


@torch.no_grad()
def prever(modelo, dl, dev) -> np.ndarray:
    modelo.eval()
    saida = []
    for x, _ in dl:
        with torch.autocast(dev.type, dtype=torch.float16, enabled=dev.type == "cuda"):
            saida.append(torch.sigmoid(modelo(x.to(dev, non_blocking=True)).float().squeeze(1)).cpu())
    return torch.cat(saida).numpy()


def treinar(df_tr, df_val, args, dev, log):
    modelo = timm.create_model(args.arq, pretrained=True, num_classes=1).to(dev)
    opt = torch.optim.AdamW(modelo.parameters(), lr=args.lr, weight_decay=1e-2)
    dl_tr = carregar(Docs(df_tr.arquivo, df_tr.label, True), args.bs, True, args.workers)
    dl_val = carregar(Docs(df_val.arquivo, df_val.label, False), args.bs * 2, False, args.workers) if df_val is not None else None
    passos = args.epocas * len(dl_tr)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, args.lr, total_steps=passos, pct_start=0.1)
    scaler = torch.amp.GradScaler(enabled=dev.type == "cuda")
    perda_fn = nn.BCEWithLogitsLoss()
    hist = []
    for ep in range(args.epocas):
        modelo.train()
        t0, soma, n = time.time(), 0.0, 0
        for i, (x, y) in enumerate(dl_tr):
            x, y = x.to(dev, non_blocking=True), y.to(dev)
            with torch.autocast(dev.type, dtype=torch.float16, enabled=dev.type == "cuda"):
                perda = perda_fn(modelo(x).squeeze(1), y * 0.95 + 0.025)  # label smoothing leve
            opt.zero_grad(set_to_none=True)
            scaler.scale(perda).backward()
            scaler.step(opt)
            scaler.update()
            sched.step()
            soma, n = soma + perda.item() * len(y), n + len(y)
            if i % 200 == 0:
                log(f"  ep{ep + 1} {i}/{len(dl_tr)} perda={soma / n:.4f} {n / (time.time() - t0):.0f} img/s")
        reg = {"epoca": ep + 1, "perda_treino": soma / n, "seg": time.time() - t0}
        if dl_val is not None:
            p = prever(modelo, dl_val, dev)
            reg.update({f"val_{k}": v for k, v in metricas(df_val.label, p).items()})
        hist.append(reg)
        log(json.dumps(reg))
    return modelo, hist


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modo", choices=["ood", "final"], default="ood")
    ap.add_argument("--holdout", default="MOZAMBIQUE/DL", help="tipo de documento fora do treino (modo ood)")
    ap.add_argument("--arq", default="efficientnet_b0")
    ap.add_argument("--epocas", type=int, default=4)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--max-treino", type=int, default=0, help="limita nº de imagens (teste rápido)")
    ap.add_argument("--prever-teste", action="store_true")
    ap.add_argument("--saida", default="/kaggle/working" if NO_KAGGLE else r"C:\freuid\runs")
    args = ap.parse_args()

    random.seed(42), np.random.seed(42), torch.manual_seed(42)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    saida = Path(args.saida) / f"{args.modo}_{args.arq}" if not NO_KAGGLE else Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)
    arq_log = open(saida / f"log_{args.modo}.txt", "a", encoding="utf-8")

    def log(msg):
        print(msg, flush=True)
        arq_log.write(msg + "\n")
        arq_log.flush()

    raiz = achar_raiz()
    log(f"dispositivo={dev} raiz={raiz} args={vars(args)}")
    if NO_KAGGLE:
        df = pd.read_csv(raiz / "train_labels.csv")
        idx = indexar_jpegs(raiz)
        df["arquivo"] = df["id"].map(idx)
    else:
        df = pd.read_csv(raiz / "amostra.csv")
        df = df[df.arquivo.map(lambda a: Path(a).exists())]
    df = df.dropna(subset=["arquivo"]).reset_index(drop=True)
    if args.max_treino:
        df = df.sample(min(args.max_treino, len(df)), random_state=42).reset_index(drop=True)
    log(f"imagens de treino disponíveis: {len(df)}")

    resultado = {"args": vars(args), "n_total": len(df)}
    if args.modo == "ood":
        fora = df[df.type == args.holdout]
        dentro = df[df.type != args.holdout]
        val_id = dentro.groupby(["type", "label"], group_keys=False).sample(frac=0.15, random_state=42)
        treino = dentro.drop(val_id.index)
        log(f"treino={len(treino)} val_ID={len(val_id)} val_OOD={len(fora)} ({args.holdout})")
        modelo, hist = treinar(treino, val_id, args, dev, log)
        p_id = prever(modelo, carregar(Docs(val_id.arquivo, val_id.label, False), args.bs * 2, False, args.workers), dev)
        p_ood = prever(modelo, carregar(Docs(fora.arquivo, fora.label, False), args.bs * 2, False, args.workers), dev)
        resultado.update(historico=hist, val_id=metricas(val_id.label, p_id), val_ood=metricas(fora.label, p_ood))
        pd.concat([
            val_id.assign(prob=p_id, conjunto="ID"),
            fora.assign(prob=p_ood, conjunto="OOD"),
        ])[["id", "label", "is_digital", "type", "conjunto", "prob"]].to_csv(saida / "previsoes_validacao.csv", index=False)
    else:
        modelo, hist = treinar(df, None, args, dev, log)
        resultado.update(historico=hist)

    torch.save(modelo.state_dict(), saida / f"modelo_{args.modo}.pt")
    log("RESULTADO " + json.dumps({k: v for k, v in resultado.items() if k != "historico"}, ensure_ascii=False))

    if args.prever_teste:
        sub = pd.read_csv(raiz / "sample_submission.csv")
        idx = idx if NO_KAGGLE else indexar_jpegs(raiz)
        caminhos = sub["id"].map(idx)
        log(f"teste: {len(sub)} ids, {caminhos.notna().sum()} imagens encontradas")
        ok = caminhos.notna()
        p = prever(modelo, carregar(Docs(caminhos[ok], np.zeros(ok.sum()), False), args.bs * 2, False, args.workers), dev)
        sub["label"] = 0.5
        sub.loc[ok, "label"] = np.clip(p, 1e-4, 1 - 1e-4)
        sub.to_csv(saida / "submission.csv", index=False)
        resultado["teste_hist"] = np.histogram(p, bins=10, range=(0, 1))[0].tolist()
        log("submission.csv gravado")

    (saida / f"resultado_{args.modo}.json").write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")



if __name__ == "__main__":
    import shutil
    base = ["--epocas", "4", "--bs", "32", "--workers", "4"]
    for extra in (["--modo", "ood", "--holdout", "MOZAMBIQUE/DL"],
                  ["--modo", "final", "--prever-teste"]):
        sys.argv = ["cnn.py"] + base + extra
        main()
