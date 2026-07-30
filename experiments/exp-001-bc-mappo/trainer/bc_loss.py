"""Masked cross-entropy with legal-only label smoothing (prereg §5, §7.2,
§11: mask applied consistently to sampling, log-probs, AND entropy).

Illegal logits are pushed to -inf before the softmax, so illegal actions
get exactly zero probability and contribute zero gradient. The smoothing
target spreads eps only over the row's LEGAL actions — smoothing must not
fight the mask, and it guarantees entropy > 0 at convergence (the clone
must not be deterministic when PPO starts).
"""

import torch
import torch.nn.functional as F

NEG_INF = float("-inf")


def masked_log_softmax(logits, mask):
    return F.log_softmax(logits.masked_fill(~mask, NEG_INF), dim=-1)


def smoothed_targets(label, mask, eps: float):
    """(1-eps) on the expert action, eps uniform over the row's legal set
    (label included). Rows are guaranteed never-all-illegal upstream."""
    legal = mask.to(torch.float32)
    q = legal * (eps / legal.sum(dim=-1, keepdim=True))
    q[torch.arange(label.shape[0], device=label.device), label] += 1.0 - eps
    return q


def bc_loss_and_metrics(logits, mask, label, eps: float):
    logp = masked_log_softmax(logits, mask)
    # q is exactly 0 where logp is -inf; zero the -infs so 0 * -inf can't
    # poison the sum with NaN.
    logp_safe = torch.where(mask, logp, torch.zeros_like(logp))
    q = smoothed_targets(label, mask, eps)
    loss = -(q * logp_safe).sum(dim=-1).mean()

    with torch.no_grad():
        p = logp.exp()
        entropy = -(p * logp_safe).sum(dim=-1).mean()
        pred = logits.masked_fill(~mask, NEG_INF).argmax(dim=-1)
        top1 = (pred == label).to(torch.float32).mean()
    return loss, {
        "entropy": entropy.item(),
        "top1": top1.item(),
        "pred": pred,
    }
