import json, os, hashlib
from dataclasses import asdict
from .core import BeliefCertificate

def save_certificate(cert: BeliefCertificate, path: str) -> str:
    data = asdict(cert)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return path

def load_certificate(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256_hex(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return "0x" + h.hexdigest()