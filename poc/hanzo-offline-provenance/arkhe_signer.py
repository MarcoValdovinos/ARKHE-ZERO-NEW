#!/usr/bin/env python3
"""
ARKHE-VAULT-SIGNER: Firma criptográfica de evidencia digital.
Uso: python3 arkhe_signer.py <archivo_a_firmar>
"""
import sys
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

KEYS_DIR = Path.home() / ".secrets"
PRIV_KEY_FILE = KEYS_DIR / "ecatepec-01-1122_private.key"

def sign_file(file_path):
    if not PRIV_KEY_FILE.exists():
        print("❌ Error: No se encontró la llave privada. Ejecuta el mesh primero.")
        return

    path = Path(file_path)
    if not path.exists():
        print(f"❌ Error: El archivo {file_path} no existe.")
        return

    # 1. Calcular el Hash SHA-256 del archivo (la huella digital)
    file_hash = hashlib.sha256(path.read_bytes()).hexdigest()

    # 2. Crear el bloque de evidencia
    evidence_block = {
        "filename": path.name,
        "file_hash_sha256": file_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device_id": "ecatepec-01-1122"
    }
    
    # 3. Firmar el bloque con Ed25519
    priv_bytes = PRIV_KEY_FILE.read_bytes()
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(priv_bytes)
    
    block_bytes = json.dumps(evidence_block, sort_keys=True).encode()
    signature = private_key.sign(block_bytes).hex()
    
    evidence_block["signature_ed25519"] = signature

    # 4. Guardar el recibo
    receipt_file = path.with_suffix(path.suffix + ".arkhe-receipt")
    receipt_file.write_text(json.dumps(evidence_block, indent=2))
    
    print(f"✅ Evidencia Firmada: {path.name}")
    print(f"🔐 Hash SHA-256: {file_hash[:16]}...")
    print(f"✍️ Firma Ed25519: {signature[:32]}...")
    print(f"📄 Recibo guardado en: {receipt_file.name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 arkhe_signer.py <archivo>")
    else:
        sign_file(sys.argv[1])
