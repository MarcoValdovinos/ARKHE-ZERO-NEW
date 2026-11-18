#!/usr/bin/env python3
import urllib.request
import os

print("📥 Descargando motor criptográfico...")
try:
    nacl = urllib.request.urlopen("https://cdn.jsdelivr.net/npm/tweetnacl@1.0.3/nacl.min.js", timeout=15).read().decode('utf-8')
    nacl_util = urllib.request.urlopen("https://cdn.jsdelivr.net/npm/tweetnacl-util@0.15.1/nacl-util.min.js", timeout=15).read().decode('utf-8')
except Exception as e:
    print(f"❌ Error descargando: {e}")
    print("Necesitas internet para la compilación (solo una vez).")
    exit(1)

print("📦 Empaquetando en un solo archivo soberano...")

html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ARKHE ZERO — Identidad Soberana</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #05050a; color: #e0e0e0; font-family: 'Courier New', monospace; padding: 20px; min-height: 100vh; }}
  body::before {{ content: ''; position: fixed; inset: 0; background: radial-gradient(circle at 30% 20%, rgba(0,255,200,0.08), transparent 50%), radial-gradient(circle at 70% 80%, rgba(180,100,255,0.08), transparent 50%); z-index: -1; }}
  .container {{ max-width: 700px; margin: 0 auto; }}
  h1 {{ color: #00ffcc; text-align: center; font-size: 1.8rem; letter-spacing: 4px; text-shadow: 0 0 20px rgba(0,255,200,0.5); margin: 20px 0; }}
  .subtitle {{ text-align: center; color: #888; font-size: 0.75rem; letter-spacing: 2px; margin-bottom: 30px; }}
  .card {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(0,255,200,0.2); border-radius: 12px; padding: 20px; margin-bottom: 20px; backdrop-filter: blur(10px); }}
  .card h3 {{ color: #00ffcc; font-size: 0.85rem; letter-spacing: 2px; margin-bottom: 12px; }}
  .did {{ font-family: monospace; font-size: 0.7rem; word-break: break-all; color: #d7b4ff; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 6px; }}
  .row {{ display: flex; gap: 8px; margin-top: 8px; }}
  button {{ background: #00ffcc; color: #000; border: none; padding: 10px 16px; font-weight: bold; cursor: pointer; border-radius: 6px; font-family: inherit; font-size: 0.8rem; transition: 0.2s; }}
  button:hover {{ background: #fff; }}
  button.ghost {{ background: transparent; color: #00ffcc; border: 1px solid #00ffcc; }}
  textarea, input {{ width: 100%; background: rgba(0,0,0,0.5); border: 1px solid rgba(0,255,200,0.3); color: #fff; padding: 10px; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 0.8rem; resize: vertical; }}
  textarea {{ min-height: 80px; }}
  .result {{ margin-top: 12px; padding: 10px; border-radius: 6px; font-size: 0.8rem; word-break: break-all; }}
  .valid {{ background: rgba(0,255,100,0.15); border: 1px solid #00ff64; color: #00ff64; }}
  .invalid {{ background: rgba(255,0,0,0.15); border: 1px solid #ff3300; color: #ff6666; }}
  .footer {{ text-align: center; color: #555; font-size: 0.7rem; margin-top: 40px; letter-spacing: 2px; }}
  .pulse {{ animation: pulse 2s infinite; }}
  @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.6; }} }}
</style>
</head>
<body>
<div class="container">
  <h1>⚛ ARKHE ZERO</h1>
  <div class="subtitle">IDENTIDAD SOBERANA · W3C DID:KEY · ED25519</div>

  <div class="card">
    <h3>◆ TU IDENTIDAD DESCENTRALIZADA</h3>
    <div class="did" id="didDisplay">Generando...</div>
    <div class="row">
      <button onclick="copyText('didDisplay')">Copiar DID</button>
      <button class="ghost" onclick="exportIdentity()">Exportar Identidad</button>
    </div>
  </div>

  <div class="card">
    <h3>◆ FIRMAR UN DOCUMENTO</h3>
    <textarea id="signInput" placeholder="Escribe tu mensaje, contrato o declaración..."></textarea>
    <div class="row">
      <button onclick="doSign()">Firmar con mi DID</button>
    </div>
    <div id="signResult"></div>
  </div>

  <div class="card">
    <h3>◆ VERIFICAR UNA FIRMA</h3>
    <textarea id="verifyText" placeholder="Pega el texto original aquí..."></textarea>
    <input id="verifySig" placeholder="Firma (base64)" style="margin-top: 8px;">
    <input id="verifyKey" placeholder="DID del firmante (did:key:...)" style="margin-top: 8px;">
    <div class="row">
      <button onclick="doVerify()">Verificar</button>
    </div>
    <div id="verifyResult"></div>
  </div>

  <div class="footer">
    <span class="pulse">◯_●</span> 51% HUMANO · 49% IA · 100% SOBERANO
    <br><br>
    Ninguna conexión a internet. Ninguna dependencia externa.<br>
    Este archivo funciona para siempre.
  </div>
</div>

<script>{nacl}</script>
<script>{nacl_util}</script>
<script>
const BASE58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';

function encodeBase58(bytes) {{
  let n = 0n;
  for (const b of bytes) n = n * 256n + BigInt(b);
  let r = '';
  while (n > 0n) {{ r = BASE58[Number(n % 58n)] + r; n = n / 58n; }}
  for (const b of bytes) {{ if (b === 0) r = '1' + r; else break; }}
  return r;
}}

function bytesToDID(pubBytes) {{
  const buf = new Uint8Array(2 + pubBytes.length);
  buf[0] = 0xed; buf[1] = 0x01;
  buf.set(pubBytes, 2);
  return 'did:key:z' + encodeBase58(buf);
}}

function didToBytes(did) {{
  if (!did.startsWith('did:key:z')) throw new Error('DID inválido');
  const encoded = did.slice(9);
  let n = 0n;
  for (const c of encoded) {{ n = n * 58n + BigInt(BASE58.indexOf(c)); }}
  const bytes = [];
  while (n > 0n) {{ bytes.unshift(Number(n % 256n)); n = n / 256n; }}
  while (encoded.startsWith('1') && bytes.length < 34) bytes.unshift(0);
  return new Uint8Array(bytes.slice(2));
}}

// 1. Generar o cargar identidad
let identity = JSON.parse(localStorage.getItem('arkhe_identity') || 'null');
if (!identity) {{
  const kp = nacl.sign.keyPair();
  identity = {{
    priv: nacl.util.encodeBase64(kp.secretKey),
    pub: nacl.util.encodeBase64(kp.publicKey),
    did: bytesToDID(kp.publicKey),
    created: new Date().toISOString()
  }};
  localStorage.setItem('arkhe_identity', JSON.stringify(identity));
}}

document.getElementById('didDisplay').textContent = identity.did;

// 2. Firmar
function doSign() {{
  const text = document.getElementById('signInput').value;
  if (!text) return alert('Escribe algo para firmar');
  const data = nacl.util.decodeUTF8(text);
  const sk = nacl.util.decodeBase64(identity.priv);
  const sig = nacl.sign.detached(data, sk);
  const sigB64 = nacl.util.encodeBase64(sig);
  document.getElementById('signResult').innerHTML = `
    <div class="result valid">
      <strong>✓ FIRMADO</strong><br><br>
      <strong>Firma:</strong><br>${sigB64}<br><br>
      <strong>DID del firmante:</strong><br>${identity.did}
    </div>`;
}}

// 3. Verificar
function doVerify() {{
  const text = document.getElementById('verifyText').value;
  const sig = document.getElementById('verifySig').value.trim();
  const did = document.getElementById('verifyKey').value.trim();
  const result = document.getElementById('verifyResult');

  if (!text || !sig || !did) {{
    result.innerHTML = '<div class="result invalid">❌ Faltan datos (texto, firma o DID)</div>';
    return;
  }}

  try {{
    const data = nacl.util.decodeUTF8(text);
    const sigBytes = nacl.util.decodeBase64(sig);
    const pubBytes = didToBytes(did);
    const valid = nacl.sign.detached.verify(data, sigBytes, pubBytes);
    
    if (valid) {{
      result.innerHTML = '<div class="result valid"><strong>✅ FIRMA VÁLIDA</strong><br>El documento es auténtico y no ha sido alterado.</div>';
    }} else {{
      result.innerHTML = '<div class="result invalid"><strong>❌ FIRMA INVÁLIDA</strong><br>El documento fue alterado o el DID no coincide.</div>';
    }}
  }} catch(e) {{
    result.innerHTML = `<div class="result invalid">❌ Error: ${{e.message}}</div>`;
  }}
}}

// 4. Exportar
function exportIdentity() {{
  const blob = new Blob([JSON.stringify(identity, null, 2)], {{type:'application/json'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'arkhe-identity.json';
  a.click();
}}

function copyText(id) {{
  navigator.clipboard.writeText(document.getElementById(id).textContent);
  alert('Copiado');
}}
</script>
</body>
</html>'''

with open('arkhe-sovereign.html', 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize('arkhe-sovereign.html') / 1024
print(f"\\n✅ ARCHIVO SOBERANO CREADO")
print(f"📦 Tamaño: {{size_kb:.1f}} KB")
print(f"📍 Ubicación: ~/ARKHE-ZERO-NEW/arkhe-sovereign.html")
print(f"\\n🌐 Pruébalo: abre el archivo en cualquier navegador.")
