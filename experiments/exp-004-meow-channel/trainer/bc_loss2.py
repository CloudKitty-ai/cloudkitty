"""Two-head BC loss (prereg §5): two masked CEs, SUMMED.

Each head gets exp-001's masked cross-entropy with legal-only label
smoothing over ITS OWN mask; the training objective is the plain sum —
the factored NLL of the joint (activity, message) label, no lambda
weighting (the loss composition registered in §5). Per-head metrics are
reported separately; the plateau statistic is the summed val loss.
"""

import importlib.util
import sys
from pathlib import Path

_EXP1 = Path(__file__).resolve().parents[2] / "exp-001-bc-mappo" / "trainer"
_spec = importlib.util.spec_from_file_location("exp001_bc_loss", _EXP1 / "bc_loss.py")
_v1 = importlib.util.module_from_spec(_spec)
sys.modules["exp001_bc_loss"] = _v1
_spec.loader.exec_module(_v1)

bc_loss_and_metrics = _v1.bc_loss_and_metrics
NEG_INF = _v1.NEG_INF


def two_head_loss(logits, n_actions, mask, label, mask_msg, label_msg, eps):
    """Splits the trunk's logits by index convention and sums the heads.

    Returns (loss, metrics) where metrics carries per-head entropy/top1
    and the per-row predictions for class accounting.
    """
    act_logits = logits[:, :n_actions]
    msg_logits = logits[:, n_actions:]
    act_loss, act_m = bc_loss_and_metrics(act_logits, mask, label, eps)
    msg_loss, msg_m = bc_loss_and_metrics(msg_logits, mask_msg, label_msg, eps)
    return act_loss + msg_loss, {
        "act_loss": act_loss.item(),
        "msg_loss": msg_loss.item(),
        "act_entropy": act_m["entropy"],
        "msg_entropy": msg_m["entropy"],
        "act_top1": act_m["top1"],
        "msg_top1": msg_m["top1"],
        "act_pred": act_m["pred"],
        "msg_pred": msg_m["pred"],
    }
