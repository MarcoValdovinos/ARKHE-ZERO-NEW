#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib, os, glob, time, logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
logging.basicConfig(level=logging.INFO, format="%(asctime)s [ARKHE] %(message)s")
log = logging.getLogger("arkhe")
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.exceptions import InvalidSignature
    HAS_CRYPTO=True
except ImportError:
    HAS_CRYPTO=False
    log.warning("cryptography no instalada")
BASE=Path(__file__).resolve().parent
SEARCH_DIRS=[BASE,BASE/"src/mesh",BASE/"src"/"mesh",Path.home()/"ARKHE-ZERO-NEW"/"src"/"mesh"]
ALLOWLIST={
 "ecatepec-01-1122":"ad214786291a111c06db44cf2e797fbd2b4c50c476792345ed051bc85b099e3d",
 "ecatepec-02-1122":"ebf38a03c5ea3376caa4ef4d31cdc1b19f97bc5c530bb4444c44bf860e7c7d95",
}
@dataclass
class Verdict:
    node_id: str
    decision: str | None
    valid: bool
    ok_signature: bool | None
    ok_allowlist: bool
    ok_hash_std: bool | None
    reasons: list[str]
    entry_hash: str
    prev_hash: str
    source: str
    payload: dict
    def to_dict(self): return asdict(self)
def canonical(payload: dict, signed_payload: str|None, canonical_field: str|None) -> str:
    if signed_payload: return signed_payload
    if canonical_field: return canonical_field
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def verify_signature(pub_hex: str, msg: str, sig_hex: str) -> tuple[bool|None, list[str]]:
    if not HAS_CRYPTO: return None, ["cryptography_no_instalada"]
    if not pub_hex: return None, ["sin_llave_publica"]
    if not sig_hex: return None, ["sin_firma"]
    try:
        pub=Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))
        pub.verify(bytes.fromhex(sig_hex), msg.encode())
        return True, []
    except InvalidSignature:
        return False, ["firma_invalida"]
    except Exception as e:
        return False, [f"error_verificacion:{e}"]
def verify_event(ev: dict) -> Verdict:
    node=ev.get("node_id") or ev.get("node") or "desconocido"
    payload=ev.get("payload") or ev.get("data") or {}
    if not isinstance(payload, dict): payload={"value": payload}
    msg=canonical(payload, ev.get("signed_payload"), ev.get("canonical"))
    sig_hex=ev.get("signature") or ev.get("sig") or ""
    entry_hash=ev.get("entry_hash") or ev.get("hash") or ""
    prev_hash=ev.get("prev_hash") or ev.get("prev") or ""
    pub_hex=ALLOWLIST.get(node, "")
    reasons: list[str]=[]
    if node not in ALLOWLIST: reasons.append("node_no_autorizado")
    ok_sig, sig_reasons=verify_signature(pub_hex, msg, sig_hex)
    reasons.extend(sig_reasons)
    ok_hash=None
    if entry_hash:
        calc=hashlib.sha256((msg+(prev_hash or "")).encode()).hexdigest()
        ok_hash=(calc==entry_hash)
        if not ok_hash: reasons.append("hash_no_coincide_formato_estandar_aviso")
    valid=(ok_sig is True) and (node in ALLOWLIST)
    return Verdict(node_id=node, decision=payload.get("decision"), valid=valid, ok_signature=ok_sig, ok_allowlist=node in ALLOWLIST, ok_hash_std=ok_hash, reasons=reasons, entry_hash=entry_hash, prev_hash=prev_hash, source=ev.get("_source_file",""), payload=payload)
def find_files() -> list[str]:
    out=[]
    for d in SEARCH_DIRS:
        if d.exists(): out.extend(glob.glob(str(d/"memoria_*.json")))
    return sorted(set(out))
def load_events() -> tuple[list[dict], list[dict]]:
    events=[]; errors=[]
    for f in find_files():
        try:
            data=json.loads(Path(f).read_text())
            arr=data if isinstance(data,list) else (data.get("events") or data.get("memoria") or data.get("entries") or [])
            for e in arr:
                e["_source_file"]=Path(f).name; events.append(e)
        except Exception as e:
            errors.append({"file":Path(f).name,"error":str(e)})
    return events, errors
def build_status() -> dict:
    t0=time.time()
    events, errors=load_events()
    verdicts=[verify_event(e) for e in events]
    total=len(verdicts); valid_n=sum(1 for v in verdicts if v.valid); invalid_n=total-valid_n
    nodes=sorted(set(v.node_id for v in verdicts))
    h=datetime.now().hour
    decision="CALDO 100" if h<12 else "MOLE 120"
    rule="Antes de 12:00 = CALDO 100 · Despues = MOLE 120"
    seen=set(); chain_ok=True
    for v in verdicts:
        if v.entry_hash in seen: chain_ok=False
        seen.add(v.entry_hash)
    return {"service":"ARKHE MESH VERIFIER","version":"2.0.0-elite","decision":decision,"rule":rule,"hour":h,"total_events":total,"valid":valid_n,"invalid":invalid_n,"nodes":nodes,"allowlist_nodes":list(ALLOWLIST.keys()),"has_cryptography":HAS_CRYPTO,"chain_unique_hashes":chain_ok,"files":[Path(f).name for f in find_files()],"errors":errors,"verify_ms":round((time.time()-t0)*1000,2),"events":[v.to_dict() for v in verdicts[-100:]],"audit":"Verifica Ed25519 + allowlist + hash. No firma. No expone privadas. Timestamp verificable, no peer-review, no endorsement."}
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def _send(self,code:int,body:bytes,ctype:str):
        self.send_response(code)
        self.send_header("Content-Type",ctype)
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("X-Frame-Options","DENY")
        self.send_header("Referrer-Policy","no-referrer")
        self.send_header("Content-Security-Policy","default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:[STRIPPED] connect-src 'self'")
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        p=urlparse(self.path).path
        if p in ("/","/visor.html","/visor_prod.html","/visor_v2.html"):
            f=BASE/"visor_v2.html"
            if not f.exists(): return self._send(404,b"visor_v2.html no encontrado","text/plain")
            return self._send(200,f.read_bytes(),b"text/html; charset=utf-8")
        if p=="/api/status": return self._send(200,json.dumps(build_status(),indent=2,ensure_ascii=False).encode(),b"application/json")
        if p=="/api/health": return self._send(200,json.dumps({"ok":True,"has_cryptography":HAS_CRYPTO,"version":"2.0.0-elite"}).encode(),b"application/json")
        return self._send(404,b"404","text/plain")
if __name__=="__main__":
    port=int(os.environ.get("PORT","8080"))
    log.info(f"ELITE en http://127.0.0.1:{port}/visor_v2.html")
    log.info(f"API http://127.0.0.1:{port}/api/status")
    ThreadingHTTPServer(("0.0.0.0",port),Handler).serve_forever()
