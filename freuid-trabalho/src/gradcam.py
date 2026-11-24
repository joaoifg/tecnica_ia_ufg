"""Grad-CAM da EfficientNet-B0 em poucos acertos e erros (passo 4).

LICENÇA: as sobreposições de Grad-CAM mostram a foto do documento, então ficam SÓ em
C:\\freuid\\runs\\ood_efficientnet_b0\\gradcam\\ (fora do git, fora de reports/).
No repositório entra apenas reports/analise/gradcam_resumo.json: números agregados sobre
ONDE o mapa de calor se concentra (borda × centro, quadrantes), sem imagem.

Uso: python src/gradcam.py --n 8
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import timm
import torch
from PIL import Image

from cnn import H, W, Docs
from config import ANALISE
from protocolo import carregar_split

RUN = Path(r"C:\freuid\runs\ood_efficientnet_b0")


def gradcam(modelo, x, camada):
    ativ, grad = {}, {}
    h1 = camada.register_forward_hook(lambda m, i, o: ativ.__setitem__("a", o))
    h2 = camada.register_full_backward_hook(lambda m, gi, go: grad.__setitem__("g", go[0]))
    modelo.zero_grad()
    saida = modelo(x)
    saida.sum().backward()
    h1.remove(), h2.remove()
    pesos = grad["g"].mean(dim=(2, 3), keepdim=True)
    cam = torch.relu((pesos * ativ["a"]).sum(1)).squeeze(0)
    cam = cam / (cam.max() + 1e-8)
    return torch.nn.functional.interpolate(cam[None, None], (H, W), mode="bilinear")[0, 0].detach().cpu().numpy(), \
        torch.sigmoid(saida).item()


def regioes(cam: np.ndarray) -> dict:
    """Fração da 'massa' do mapa em cada região (borda = faixa externa de 10%)."""
    tot = cam.sum() + 1e-8
    bh, bw = int(0.1 * H), int(0.1 * W)
    centro = cam[bh:-bh, bw:-bw].sum() / tot
    esq, dir_ = cam[:, : W // 2].sum() / tot, cam[:, W // 2:].sum() / tot
    sup, inf = cam[: H // 2].sum() / tot, cam[H // 2:].sum() / tot
    return {"borda_10pct": float(1 - centro), "centro": float(centro), "metade_esquerda": float(esq),
            "metade_direita": float(dir_), "metade_superior": float(sup), "metade_inferior": float(inf)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8, help="imagens por grupo (acerto/erro × ID/OOD)")
    args = ap.parse_args()
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    modelo = timm.create_model("efficientnet_b0", pretrained=False, num_classes=1)
    modelo.load_state_dict(torch.load(RUN / "modelo_melhor.pt", map_location="cpu"))
    modelo.to(dev).eval()
    camada = modelo.conv_head

    res = json.loads((RUN / "resultado_protocolo.json").read_text(encoding="utf-8"))
    t = res["limiar_custo"]
    prev = pd.read_csv(RUN / "previsoes_validacao.csv")
    split = carregar_split(salvar=False)[["id", "arquivo"]]
    prev = prev.merge(split, on="id")
    prev["pred"] = (prev.prob >= t).astype(int)
    prev["grupo"] = np.where(prev.pred == prev.label, "acerto", "erro")

    pasta = RUN / "gradcam"
    pasta.mkdir(exist_ok=True)
    tf = Docs([], [], False).tf
    # referência: se o mapa fosse uniforme, a faixa de borda de 10% teria 1 - 0,8² = 36% da massa
    resumo = {"limiar": t, "camada": "conv_head", "borda_se_mapa_uniforme": 0.36, "grupos": {}}
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for (conj, grupo), g in prev.groupby(["conjunto", "grupo"]):
        amostra = g.sample(min(args.n, len(g)), random_state=42)
        regs = []
        for r in amostra.itertuples():
            im = Image.open(r.arquivo).convert("RGB")
            x = tf(im)[None].to(dev).requires_grad_(True)
            cam, p = gradcam(modelo, x, camada)
            regs.append(regioes(cam))
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.imshow(im.resize((W, H)))
            ax.imshow(cam, cmap="jet", alpha=0.45)
            ax.set_title(f"{conj} {grupo} rótulo={r.label} p={p:.2f}")
            ax.axis("off")
            fig.savefig(pasta / f"{conj}_{grupo}_{r.id}.png", bbox_inches="tight")
            plt.close(fig)
        resumo["grupos"][f"{conj}_{grupo}"] = {"n": len(regs),
                                               **{k: float(np.mean([d[k] for d in regs])) for k in regs[0]}}
    (RUN / "gradcam_resumo.json").write_text(json.dumps(resumo, indent=2, ensure_ascii=False), encoding="utf-8")
    (ANALISE / "gradcam_resumo.json").write_text(json.dumps(resumo, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(resumo, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
