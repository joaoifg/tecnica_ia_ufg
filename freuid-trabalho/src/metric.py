"""Métricas da competição FREUID 2026 (menor é melhor)."""

import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve


def freuid_score(y_true, y_score):
    """Score oficial: combinação harmônica de AUC e TPR@1%FPR.

    AuDET ≈ 1 - ROC-AUC; APCER@1%BPCER = 1 - TPR no ponto FPR ≤ 0,01.
    O retorno é 1 - média harmônica de (AUC, TPR@1%FPR); menor é melhor.
    """
    auc = roc_auc_score(y_true, y_score)
    fpr, tpr, _ = roc_curve(y_true, y_score)
    mask = fpr <= 0.01
    tpr_at_1 = tpr[mask].max() if mask.any() else 0.0
    g_audet, g_apcer = auc, tpr_at_1
    if g_audet + g_apcer == 0:
        return 1.0
    return 1 - 2 * g_audet * g_apcer / (g_audet + g_apcer)


def freuid_breakdown(y_true, y_score):
    """Retorna dicionário com AUC, TPR@1%FPR, APCER@1%BPCER e score FREUID."""
    auc = roc_auc_score(y_true, y_score)
    fpr, tpr, _ = roc_curve(y_true, y_score)
    mask = fpr <= 0.01
    tpr_at_1 = float(tpr[mask].max()) if mask.any() else 0.0
    apcer = 1.0 - tpr_at_1
    score = freuid_score(y_true, y_score)
    return {
        "roc_auc": float(auc),
        "audet": float(1.0 - auc),
        "tpr_at_1pct_fpr": tpr_at_1,
        "apcer_at_1pct_bpcer": apcer,
        "freuid_score": float(score),
    }
