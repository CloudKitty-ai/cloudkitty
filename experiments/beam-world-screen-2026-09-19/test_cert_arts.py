"""Guard for the cert harness's CERT_ARTS override and seat-scoped provenance (tier 2 reads the
beam arms and the clone from this directory's artifacts). Run: python -B test_cert_arts.py"""
import importlib, os, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
CERT = HERE.parent / "fog-gen1-cert"
sys.path.insert(0, str(CERT))

with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    (root / "ppo-fog-x").mkdir(parents=True)
    (root / "ppo-fog-x" / "policy-final.pt").write_bytes(b"not a real artifact")
    os.environ["CERT_ARTS"] = str(root)
    import cert_harness_fog as H
    importlib.reload(H)
    assert H.ARTS == root, H.ARTS
    # provenance hashes the artifacts the SEATING uses, under CERT_ARTS, and nothing else
    prov = H.provenance(H.DEFAULT_CONFIG, ["scripted", "ppo:x", "scripted", "ppo:x", "scripted"])
    assert prov["artifacts_root"] == str(root)
    assert set(prov["artifacts"]) == {"ppo:x"}, prov["artifacts"]
    assert prov["artifacts"]["ppo:x"] == __import__("hashlib").sha256(b"not a real artifact").hexdigest()
    # a seating that names an artifact absent from the root is an error, not a silent skip
    try:
        H.provenance(H.DEFAULT_CONFIG, ["ppo:cand-s2"] * 5)
        raise SystemExit("missing artifact was not an error")
    except FileNotFoundError:
        pass
    del os.environ["CERT_ARTS"]
    importlib.reload(H)
    assert H.ARTS == CERT / "artifacts", H.ARTS
print("test_cert_arts ok")
