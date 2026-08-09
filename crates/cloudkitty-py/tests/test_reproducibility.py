"""SC-002 (spec 014 T030): identical seed + config + action sequence in two
separate OS processes produce bit-identical observation, mask, global-state,
and reward streams. The rollout runs in a fresh subprocess twice and the
stream digests must match exactly.
"""

import hashlib
import subprocess
import sys


def rollout_digest():
    import numpy as np

    import cloudkitty

    env = cloudkitty.ParallelEnv(horizon=60)
    obs, infos = env.reset(seed=7)
    agents = env.possible_agents
    digest = hashlib.sha256()

    for agent in agents:
        digest.update(obs[agent].tobytes())
        digest.update(infos[agent]["mask"].tobytes())
    digest.update(env.state().tobytes())

    for step_index in range(60):
        # A deterministic masked action script: the k-th legal entry,
        # rotated by step, so every process picks identically.
        actions = {}
        for offset, agent in enumerate(agents):
            mask = np.asarray(infos[agent]["mask"], dtype=np.uint8)
            legal_a = np.flatnonzero(mask[:34])
            legal_m = np.flatnonzero(mask[34:])
            actions[agent] = [
                int(legal_a[(step_index + offset) % legal_a.size]),
                int(legal_m[(step_index + offset) % legal_m.size]),
            ]
        obs, rewards, terminations, truncations, infos = env.step(actions)
        for agent in agents:
            digest.update(obs[agent].tobytes())
            digest.update(infos[agent]["mask"].tobytes())
            digest.update(repr(rewards[agent]).encode())
        digest.update(env.state().tobytes())

    return digest.hexdigest()


def test_two_processes_bit_identical_streams():
    runs = [
        subprocess.run(
            [sys.executable, __file__, "--emit"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        for _ in range(2)
    ]
    assert len(runs[0]) == 64, f"unexpected digest output: {runs[0]!r}"
    assert runs[0] == runs[1], "streams diverged across processes"


if __name__ == "__main__" and "--emit" in sys.argv:
    print(rollout_digest())
