"""Gera kaggle/kernel/freuid_kaggle.py a partir de src/cnn.py e envia ao Kaggle.

Uso: python kaggle/montar_kernel.py [--push]
O kernel roda: (1) validação OOD deixando MOZAMBIQUE/DL de fora;
               (2) treino final com tudo + previsão do teste -> submission.csv
"""
import json, subprocess, sys
from pathlib import Path

AQUI = Path(__file__).parent
SRC = (AQUI.parent / "src" / "cnn.py").read_text(encoding="utf-8")
corpo, _ = SRC.split('if __name__ == "__main__":')
execucao = '''
if __name__ == "__main__":
    import shutil
    base = ["--epocas", "4", "--bs", "32", "--workers", "4"]
    for extra in (["--modo", "ood", "--holdout", "MOZAMBIQUE/DL"],
                  ["--modo", "final", "--prever-teste"]):
        sys.argv = ["cnn.py"] + base + extra
        main()
'''
dest = AQUI / "kernel"
dest.mkdir(exist_ok=True)
(dest / "freuid_kaggle.py").write_text("import sys\n" + corpo + execucao, encoding="utf-8")
(dest / "kernel-metadata.json").write_text(json.dumps({
    "id": "joaohenriquecfo/freuid-cnn-ood",
    "title": "FREUID CNN OOD",
    "code_file": "freuid_kaggle.py",
    "language": "python",
    "kernel_type": "script",
    "is_private": True,
    "enable_gpu": True,
    "enable_internet": True,
    "competition_sources": ["the-freuid-challenge-2026-ijcai-ecai"],
    "dataset_sources": [], "kernel_sources": [],
}, indent=2), encoding="utf-8")
print("kernel montado em", dest)
if "--push" in sys.argv:
    subprocess.run([sys.executable, "-m", "kaggle", "kernels", "push", "-p", str(dest)], check=True)
