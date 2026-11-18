#!/usr/bin/env python3
"""
ARKHE-SWARM: Agente Autónomo con Identidad Criptográfica.
Demuestra que un agente puede tener soberanía, buscar trabajo y firmar sus intenciones.
"""
import json
import subprocess
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

KEYS_DIR = Path.home() / ".secrets"
AGENT_KEY = KEYS_DIR / "arkhe_swarm_private.key"
PUB_KEY = KEYS_DIR / "arkhe_swarm_public.key"

def init_agent_identity():
    if not AGENT_KEY.exists():
        print("🤖 [SWARM] Generando identidad criptográfica para el Agente...")
        priv = ed25519.Ed25519PrivateKey.generate()
        pub = priv.public_key()
        AGENT_KEY.write_bytes(priv.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        ))
        PUB_KEY.write_bytes(pub.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ))
    else:
        print("🤖 [SWARM] Identidad del Agente cargada.")
    
    priv_bytes = AGENT_KEY.read_bytes()
    return ed25519.Ed25519PrivateKey.from_private_bytes(priv_bytes)

def firmar_manifest(agent_key, manifest_data):
    # Crear un hash del manifiesto y firmarlo
    data_bytes = json.dumps(manifest_data, sort_keys=True).encode('utf-8')
    signature = agent_key.sign(data_bytes)
    return signature.hex()

def scan_bounties():
    print("🕵️  [SWARM] Escaneando GitHub en busca de bounties de alto valor...")
    # Usa el CLI de gh para buscar bounties
    try:
        result = subprocess.run(
            ["gh", "search", "issues", "--label", "bounty", "--state", "open", "--limit", "3", "--json", "title,url,repository"],
            capture_output=True, text=True, check=True
        )
        bounties = json.loads(result.stdout)
        return bounties
    except Exception as e:
        print(f"❌ Error escaneando: {e}")
        return []

def main():
    agent_key = init_agent_identity()
    pub_hex = PUB_KEY.read_bytes().hex()
    
    print(f"\n🧬 IDENTIDAD DEL AGENTE (DID): did:key:{pub_hex[:16]}...")
    
    # 1. El agente busca trabajo
    bounties = scan_bounties()
    
    if not bounties:
        print("No se encontraron bounties. Abortando.")
        return

    # 2. El agente elige su objetivo (el primero)
    target = bounties[0]
    print(f"\n🎯 OBJETIVO SELECCIONADO: {target['title']}")
    print(f"🔗 URL: {target['url']}")
    
    # 3. El agente genera un manifiesto de intención
    manifest = {
        "agent_id": "ARKHE-SWARM-01",
        "public_key": pub_hex,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "ACCEPT_BOUNTY",
        "target_issue": target['url'],
        "target_repo": target['repository']['nameWithOwner'],
        "human_in_the_loop": False, # ¡El agente actúa solo!
        "cryptographic_proof": "Ed25519"
    }

    # 4. El agente firma su propia intención
    signature = firmar_manifest(agent_key, manifest)
    manifest["signature"] = signature
    
    print("\n=============================================")
    print("🔏 MANIFIESTO DE INTENCIÓN FIRMADO POR EL AGENTE")
    print("=============================================")
    print(json.dumps(manifest, indent=2))
    
    # Guardar el recibo para auditoría
    receipt_file = Path.home() / f"swarm_intent_{int(datetime.now().timestamp())}.json"
    receipt_file.write_text(json.dumps(manifest, indent=2))
    
    print(f"\n✅ Prueba de intención guardada en: {receipt_file.name}")
    print("📢 Este agente ahora posee una firma criptográfica única y sus acciones son inmutables.")
    print("Esto es un Agente Autónomo Soberano.")

if __name__ == "__main__":
    main()
