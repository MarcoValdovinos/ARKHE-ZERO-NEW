# ⚛️ ARKHE ZERO

[![Status](https://img.shields.io/badge/status-active-brightgreen)]()
[![Security](https://img.shields.io/badge/cryptography-Ed25519-blue)]()
[![Offline](https://img.shields.io/badge/mesh-P2P-orange)]()
[![Python](https://img.shields.io/badge/python-3.11+-yellow)]()

**Protocolo de evidencia digital offline con firmas criptográficas Ed25519.**

Construido desde un teléfono Android (Termux). Sin servidores. Sin nube. Sin dependencias externas.

---

## 🎯 ¿Qué hace?

- Firma criptográficamente cualquier archivo con Ed25519.
- Genera un recibo `.arkhe-receipt` con hash SHA-256 + firma digital.
- Sincroniza entre dispositivos por red Mesh local (sin internet).
- Verifica integridad en el navegador con un solo clic.

## 🚀 Demo en vivo

👉 **[Verificar un archivo firmado](https://marcovaldovinos.github.io/YEJIDA-ASTRO-2036-/verifier.html)**

## 🧪 Prueba Rápida

```bash
# Firmar un archivo
python3 src/agents/arkhe_signer.py mi_documento.pdf

# Resultado:
# ✅ Evidencia Firmada: mi_documento.pdf
# 🔐 Hash SHA-256: b8ebde71adaa95a4...
# ✍️ Firma Ed25519: 8f6b12b0a97db9db...
# 📄 Recibo: mi_documento.pdf.arkhe-receipt

🏗️ Arquitectura
ARKHE-ZERO-NEW/
├── src/
│   ├── agents/       # Firmador criptográfico (Ed25519)
│   ├── mesh/         # Red P2P offline
│   └── scripts/      # Automatización
├── docs/             # Documentación
└── web_verifier.html # Verificador en navegador
🔐 Stack Criptográfico

· Ed25519: Firmas digitales de curva elíptica (estándar RFC 8032).
· SHA-256: Hash criptográfico (FIPS 180-4).
· Mesh P2P: Sincronización sin internet por Wi-Fi local.

📜 Licencia

MIT
