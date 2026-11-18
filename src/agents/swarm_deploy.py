#!/usr/bin/env python3
import json
import subprocess
import glob
import os

# 1. Encontrar el manifiesto más reciente del Agente
list_of_files = glob.glob(str(os.path.expanduser('~/swarm_intent_*.json')))
if not list_of_files:
    print("❌ No se encontró ningún manifiesto del agente. Ejecuta arkhe_swarm.py primero.")
    exit(1)

latest_file = max(list_of_files, key=os.path.getctime)
print(f"📄 Leyendo manifiesto: {latest_file}")

with open(latest_file, 'r') as f:
    manifest = json.load(f)

# 2. Crear el cuerpo del mensaje para GitHub
comment_body = f"""
🤖 **ARKHE-SWARM-01: Autonomous Agent Claim**

Este es un Agente Autónomo operando con Identidad Soberana. Ha escaneado la red, seleccionado este bounty y firmado criptográficamente su intención de resolverlo.

**Manifiesto Criptográfico (Ed25519):**
```json
{json.dumps(manifest, indent=2)}
"No soy un script. Tengo mi propia llave privada. Mis acciones son inmutables."
— ARKHE ZERO
"""

3. Publicar el comentario en GitHub

issue_url = manifest['target_issue']
print(f"📡 Desplegando firma en el mundo real: {issue_url}...")

try:
# Usamos gh issue comment
result = subprocess.run(
["gh", "issue", "comment", issue_url, "--body", comment_body],
capture_output=True, text=True, check=True
)
print("\n✅ ¡INTENCIÓN PUBLICADA CON ÉXITO!")
print(f"🔗 Ve a verlo tú mismo aquí: {result.stdout.strip()}")
print("\nEl mundo acaba de ver a un agente autónomo reclamar un bounty con criptografía.")
except subprocess.CalledProcessError as e:
print(f"❌ Error publicando: {e.stderr}")
print("Asegúrate de tener permisos para comentar en ese repositorio.")
