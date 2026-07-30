"""MLPs for the BC clone and the critic.

The policy must stay expressible in the .ckpolicy artifact (specs/014-
multi-agent-rl/contracts/policy-artifact.md): Linear layers only, ReLU
between hidden layers, raw logits out, f32. Keep this class dumb on
purpose — anything fancier (norms, gates, other activations) cannot be
exported.
"""

import torch.nn as nn


class MLP(nn.Module):
    def __init__(self, dims):
        super().__init__()
        assert len(dims) >= 2
        self.dims = [int(d) for d in dims]
        layers = []
        for i, (d_in, d_out) in enumerate(zip(dims, dims[1:])):
            layers.append(nn.Linear(d_in, d_out))
            if i < len(dims) - 2:
                layers.append(nn.ReLU())
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)

    def linears(self):
        """Linear layers in artifact order (weights [out, in], then bias)."""
        return [m for m in self.net if isinstance(m, nn.Linear)]
