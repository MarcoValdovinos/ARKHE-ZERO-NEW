#!/usr/bin/env python3
"""
ARKHE MULTISIG: Protocolo de firma de umbral (2 de 3).
Demuestra gobernanza criptográfica para evidencias de alto valor.
"""
import json
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# --- 1. GENERAR 3 IDENTIDADES (Peritos A, B, C) ---
def generar_llaves(nombre):
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()
    priv_bytes = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return {"nombre": nombre, "private": priv_bytes.hex(), "public": pub_bytes.hex(), "key_obj": priv}

peritos = [generar_llaves("Perito_A"), generar_llaves("Perito_B"), generar_llaves("Perito_C")]

# --- 2. CREAR EL DOCUMENTO BASE ---
documento = b"Contrato de confidencialidad ARKHE ZERO - Valor: $1,000,000 USD"
doc_hash = hashlib.sha256(documento).hexdigest()

print("=== INICIANDO PROTOCOLO MULTIFIRMA (2 de 3) ===")
print(f"📄 Documento a firmar: {documento.decode()}")
print(f"🔐 Hash del Documento: {doc_hash[:16]}...\n")

# --- 3. LOS PERITOS FIRMAN (Supongamos que A y B están de acuerdo) ---
firmas = []
for perito in [peritos[0], peritos[1]]: # A y B firman. C no.
    firma = perito["key_obj"].sign(documento)
    firmas.append({
        "perito": perito["nombre"],
        "public_key": perito["public"],
        "firma": firma.hex()
    })
    print(f"✍️ {perito['nombre']} ha firmado el documento.")

# --- 4. EL VERIFICADOR (El juez o el sistema) ---
print("\n=== VERIFICACIÓN DE EVIDENCIA ===")
firmas_validas = 0

for f in firmas:
    try:
        # Reconstruir la llave pública del perito
        pub_bytes = bytes.fromhex(f["public_key"])
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
        # Verificar la firma matemática
        public_key.verify(bytes.fromhex(f["firma"]), documento)
        firmas_validas += 1
        print(f"✅ Firma válida de {f['perito']}.")
    except Exception:
        print(f"❌ ALERTA: La firma de {f['perito']} es falsa o el documento fue alterado.")

# --- 5. LA REGLA DE UMBRAL (Threshold) ---
UMBRAL_REQUERIDO = 2
if firmas_validas >= UMBRAL_REQUERIDO:
    print(f"\n🏆 RESULTADO: Evidencia VÁLIDA. Se alcanzaron {firmas_validas}/{UMBRAL_REQUERIDO} firmas necesarias.")
    print("🔒 El documento es inmutable y de grado forense.")
else:
    print(f"\n🚨 RESULTADO: Evidencia RECHAZADA. Solo hay {firmas_validas} firmas. Se necesitan {UMBRAL_REQUERIDO}.")
