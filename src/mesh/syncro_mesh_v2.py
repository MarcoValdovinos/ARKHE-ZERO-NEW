#!/usr/bin/env python3
import hashlib, http.server, json, os, re, socket, socketserver, threading, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

MI_ID = "ecatepec-02-1122"
HOME = Path.home()
DATA_DIR = HOME / "arkhe-mesh-data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / f"memoria_{MI_ID}.json"
KEYS_DIR = HOME / ".secrets"
KEYS_DIR.mkdir(parents=True, exist_ok=True)
PRIV_KEY_FILE = KEYS_DIR / f"{MI_ID}_private.key"
PUB_KEY_FILE = KEYS_DIR / f"{MI_ID}_public.key"
PORT = 8000
FILENAME_RE = re.compile(r"^memoria_[A-Za-z0-9_-]{1,64}\.json$")
DB_LOCK = threading.Lock()

def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def load_or_create_keys():
    if not PRIV_KEY_FILE.exists():
        log("Generando llaves Ed25519...")
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        priv_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        PRIV_KEY_FILE.write_bytes(priv_bytes)
        PUB_KEY_FILE.write_bytes(pub_bytes)
        os.chmod(PRIV_KEY_FILE, 0o600)
    else:
        priv_bytes = PRIV_KEY_FILE.read_bytes()
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(priv_bytes)
    return private_key

SIGNING_KEY = load_or_create_keys()
VERIFY_KEY = SIGNING_KEY.public_key()
MY_PUBLIC_HEX = VERIFY_KEY.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()

def canonical_hash(payload: dict) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()

def load_node_doc(path: Path) -> dict:
    if not path.exists(): return {"nodo": MI_ID, "public_key": MY_PUBLIC_HEX, "events": []}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(doc, dict) and isinstance(doc.get("events"), list): return doc
    except: pass
    return {"nodo": MI_ID, "public_key": MY_PUBLIC_HEX, "events": []}

def atomic_write_json(path: Path, data: dict) -> None:
    tmp_path = path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp_path, path)

def append_local_decision(decision: str) -> None:
    with DB_LOCK:
        doc = load_node_doc(DB_PATH)
        events = doc["events"]
        prev_hash = events[-1]["entry_hash"] if events else "GENESIS"
        
        event = {
            "nodo": MI_ID,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision": decision,
            "prev_hash": prev_hash,
        }
        body = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        event["signature"] = SIGNING_KEY.sign(body).hex()
        event["entry_hash"] = canonical_hash(event)
        
        events.append(event)
        atomic_write_json(DB_PATH, doc)
        log(f"DECISION FIRMADA: {decision} | Sig: {event['signature'][:10]}...")

def verify_event_chain(doc: dict) -> bool:
    if not isinstance(doc, dict) or not isinstance(doc.get("events"), list): return False
    node_pub_key_hex = doc.get("public_key")
    if not node_pub_key_hex: return False

    try:
        pub_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(node_pub_key_hex))
    except:
        return False

    prev = "GENESIS"
    for ev in doc["events"]:
        if not isinstance(ev, dict): return False
        sig = ev.pop("signature", None)
        expected_hash = ev.pop("entry_hash", None)
        if not sig or not expected_hash or ev.get("prev_hash") != prev: return False
        
        body = json.dumps(ev, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        try:
            pub_key.verify(bytes.fromhex(sig), body)
        except:
            log(f"FIRMA INVÁLIDA en {doc['nodo']}")
            return False
            
        ev["signature"] = sig
        ev["entry_hash"] = expected_hash
        prev = expected_hash
    return True

class MeshHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None: return
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("/", "/nodes"):
            files = sorted(p.name for p in DATA_DIR.iterdir() if p.is_file() and FILENAME_RE.fullmatch(p.name))
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps({"nodo": MI_ID, "public_key": MY_PUBLIC_HEX, "files": files}).encode())
            return
        name = path.lstrip("/")
        if not FILENAME_RE.fullmatch(name): return self.send_error(404)
        target = (DATA_DIR / name).resolve()
        if target.parent != DATA_DIR.resolve() or not target.is_file(): return self.send_error(404)
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(target.read_bytes())

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("192.168.43.1", 80)); return s.getsockname()[0]
    except: return "127.0.0.1"

def servidor_mesh() -> None:
    with ReusableTCPServer(("0.0.0.0", PORT), MeshHandler) as httpd:
        log(f"MESH CRIPTOGRÁFICO: http://{get_local_ip()}:{PORT}")
        httpd.serve_forever()

def sync_from_host(ip: str, local_ip: str) -> None:
    if ip == local_ip: return
    try:
        req = urllib.request.Request(f"http://{ip}:{PORT}/nodes", headers={"User-Agent": "SYNCRO-V2"})
        with urllib.request.urlopen(req, timeout=0.45) as resp:
            index = json.loads(resp.read(64 * 1024).decode("utf-8"))
    except: return
    for fname in index.get("files", []):
        if fname == DB_PATH.name: continue
        try:
            f_req = urllib.request.Request(f"http://{ip}:{PORT}/{fname}", headers={"User-Agent": "SYNCRO-V2"})
            with urllib.request.urlopen(f_req, timeout=1.5) as f_resp:
                raw = f_resp.read(512 * 1024 + 1)
                if len(raw) > 512 * 1024: continue
                remote_doc = json.loads(raw.decode("utf-8"))
                if not verify_event_chain(remote_doc): continue
                dest = DATA_DIR / fname
                with DB_LOCK:
                    if len(remote_doc["events"]) >= len(load_node_doc(dest)["events"]):
                        atomic_write_json(dest, remote_doc)
                        log(f"SYNC VERIFICADO: {fname} de {ip}")
        except: pass

def buscar_y_sincronizar() -> None:
    local_ip = get_local_ip()
    bases = ("192.168.43.", "192.168.137.", "192.168.0.", "10.42.0.")
    candidates = [f"{b}{i}" for b in bases for i in range(1, 20)]
    with ThreadPoolExecutor(max_workers=24) as pool:
        for ip in candidates: pool.submit(sync_from_host, ip, local_ip)

def main() -> None:
    threading.Thread(target=servidor_mesh, daemon=True).start()
    time.sleep(0.5)
    while True:
        hora = datetime.now().hour
        decision = "CALDO 100" if hora < 12 else "MOLE 120"
        append_local_decision(decision)
        buscar_y_sincronizar()
        time.sleep(30)

if __name__ == "__main__":
    main()
