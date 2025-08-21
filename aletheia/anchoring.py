import json, hashlib

def certificate_hash_bytes(cert_path: str) -> str:
    with open(cert_path, "rb") as f:
        data = f.read()
    return "0x"+hashlib.sha256(data).hexdigest()

def certificate_hash_json(cert_obj: dict) -> str:
    blob = json.dumps(cert_obj, sort_keys=True, separators=(",",":")).encode()
    return "0x"+hashlib.sha256(blob).hexdigest()