"""Encrypt the trip data for the Trips app.

Usage: python3 encrypt.py <trips_dir> <meta_json> <passphrase_file> [out=data.enc]
  trips_dir: folder of trip JSON documents (one file per trip; the file name minus .json is the trip id)
  meta_json: JSON file with {"updatedAt": ..., "source": ...}
Writes data.enc: AES-256-GCM, key from PBKDF2-SHA256 (310,000 iterations) over the passphrase.
"""
import base64, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 310000

def main():
    trips_dir, meta_path, pass_path = sys.argv[1:4]
    out = sys.argv[4] if len(sys.argv) > 4 else "data.enc"
    trips = []
    for name in sorted(os.listdir(trips_dir)):
        if not name.endswith(".json"):
            continue
        doc = json.load(open(os.path.join(trips_dir, name)))
        if "data" in doc and isinstance(doc["data"], dict):  # ArtifactData export shape
            body = dict(doc["data"]); body["id"] = doc.get("id") or name[:-5]
        else:
            body = dict(doc); body.setdefault("id", name[:-5])
        body.pop("photo", None)
        trips.append(body)
    meta = json.load(open(meta_path))
    if "data" in meta and isinstance(meta["data"], dict):
        meta = meta["data"]
    payload = json.dumps({"trips": trips, "meta": meta}, ensure_ascii=False).encode()
    passphrase = open(pass_path).read().strip().encode()
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(passphrase)
    ct = AESGCM(key).encrypt(iv, payload, None)
    b = lambda x: base64.b64encode(x).decode()
    json.dump({"v": 1, "kdf": "PBKDF2-SHA256", "iter": ITER, "salt": b(salt), "iv": b(iv), "ct": b(ct)}, open(out, "w"))
    print(f"wrote {out}: {len(trips)} trips, {len(ct)} bytes")

if __name__ == "__main__":
    main()
