#!/usr/bin/env python3
import json, hashlib, os, glob
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.exceptions import InvalidSignature
    HAS_CRYPTO=True
except ImportError:
    HAS_CRYPTO=False
BASE=Path(__file__).resolve().parent
SEARCH_DIRS=[BASE,BASE/"src/mesh",BASE/"src"/"mesh",Path.home()/"ARKHE-ZERO-NEW"/"src"/"mesh"]
ALLOWLIST={
 "ecatepec-01-1122":"ad214786291a111c06db44cf2e797fbd2b4c50c476792345ed051bc85b099e3d",
 "ecatepec-02-1122":"ebf38a03c5ea3376caa4ef4d31cdc1b19f97bc5c530bb4444c44bf860e7c7d95",
}
def sha256_hex(s): return hashlib.sha256(s.encode()).hexdigest()
def find_memoria_files():
    out=[]
    for d in SEARCH_DIRS:
        if d.exists(): out.extend(glob.glob(str(d/"memoria_*.json")))
    return sorted(set(out))
def load_events():
    events=[]
    for f in find_memoria_files():
        try:
            data=json.loads(Path(f).read_text())
            arr=data if isinstance(data,list) else (data.get("events") or data.get("memoria") or data.get("entries") or [])
            for e in arr:
                e["_source_file"]=Path(f).name
                events.append(e)
        except Exception as ex:
            events.append({"_error":str(ex),"_source_file":Path(f).name})
    return events
def verify_event(ev):
    node=ev.get("node_id") or ev.get("node") or "desconocido"
    payload=ev.get("payload") or ev.get("data") or {}
    msg=ev.get("signed_payload") or ev.get("canonical") or json.dumps(payload,sort_keys=True,separators=(",",":"))
    sig_hex=ev.get("signature") or ev.get("sig") or ""
    entry_hash=ev.get("entry_hash") or ev.get("hash") or ""
    prev_hash=ev.get("prev_hash") or ev.get("prev") or ""
    pub_hex=ALLOWLIST.get(node,None)
    reasons=[]
    if node not in ALLOWLIST: reasons.append("node_no_autorizado")
    if pub_hex is None: reasons.append("sin_llave_publica")
    if not sig_hex: reasons.append("sin_firma")
    ok_sig=None
    if HAS_CRYPTO and pub_hex and sig_hex:
        try:
            pub=Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))
            pub.verify(bytes.fromhex(sig_hex),msg.encode())
            ok_sig=True
        except InvalidSignature:
            ok_sig=False;reasons.append("firma_invalida")
        except Exception as ex:
            ok_sig=False;reasons.append(f"error:{ex}")
    elif not HAS_CRYPTO: reasons.append("cryptography_no_instalada")
    ok_hash=None
    if entry_hash:
        calc=sha256_hex(msg+(prev_hash or ""))
        ok_hash=(calc==entry_hash)
        if not ok_hash: reasons.append("hash_no_coincide_formato_estandar")
    valid=(ok_sig is True) and (node in ALLOWLIST) and (ok_hash is True)
    return {"node_id":node,"decision":payload.get("decision") if isinstance(payload,dict) else None,"payload":payload,"entry_hash":entry_hash,"prev_hash":prev_hash,"ok_signature":ok_sig,"ok_hash_std":ok_hash,"ok_allowlist":node in ALLOWLIST,"valid":valid,"reasons":reasons,"source":ev.get("_source_file")}
def build_status():
    events=load_events()
    verified=[verify_event(e) for e in events if "_error" not in e]
    errors=[e for e in events if "_error" in e]
    total=len(verified);valid_n=sum(1 for v in verified if v["valid"]);invalid_n=total-valid_n
    nodes=sorted(set(v["node_id"] for v in verified))
    from datetime import datetime
    h=datetime.now().hour
    decision="SIN_EVENTOS" if total==0 else ("VERIFICADO" if invalid_n==0 else "CON_ERRORES")
    return {"service":"ARKHE MESH VERIFIER","version":"1.0.0-prod","decision":decision,"hour":h,"total_events":total,"valid":valid_n,"invalid":invalid_n,"nodes":nodes,"allowlist_nodes":list(ALLOWLIST.keys()),"has_cryptography":HAS_CRYPTO,"files":[Path(f).name for f in find_memoria_files()],"errors":errors,"events":verified[-100:]}
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def _send(self,code,body,ctype):
        b=body.encode() if isinstance(body,str) else body
        self.send_response(code);self.send_header("Content-Type",ctype);self.send_header("Content-Length",str(len(b)));self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(b)
    def do_GET(self):
        p=urlparse(self.path).path
        if p in ("/","/visor.html","/visor_prod.html"):
            f=BASE/"visor_prod.html"
            if not f.exists(): return self._send(404,"visor_prod.html no encontrado","text/plain")
            return self._send(200,f.read_bytes(),"text/html; charset=utf-8")
        if p=="/api/status": return self._send(200,json.dumps(build_status(),indent=2,ensure_ascii=False),"application/json")
        if p=="/api/health": return self._send(200,json.dumps({"ok":True,"has_cryptography":HAS_CRYPTO}),"application/json")
        return self._send(404,"404","text/plain")
if __name__=="__main__":
    port=int(os.environ.get("PORT","8080"))
    print(f"[ARKHE PROD] http://127.0.0.1:{port}/visor_prod.html")
    print(f"[ARKHE PROD] API http://127.0.0.1:{port}/api/status")
    print(f"[ARKHE PROD] cryptography={HAS_CRYPTO} archivos={find_memoria_files()}")
    ThreadingHTTPServer(("0.0.0.0",port),H).serve_forever()
