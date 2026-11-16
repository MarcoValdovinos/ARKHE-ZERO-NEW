#!/usr/bin/env python3
"""
SYNCRO Mesh Node — Versión endurecida para Termux (Auditoría de Seguridad Aplicada).
"""
from __future__ import annotations
import hashlib, http.server, json, os, re, socket, socketserver, threading, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

MI_ID = "ecatepec-01-1122"
HOME = Path.home()
DATA_DIR = HOME / "arkhe-mesh-data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / f"memoria_{MI_ID}.json"
PORT = 8000
MAX_PAYLOAD_BYTES = 512 * 1024
FILENAME_RE = re.compile(r"^memoria_[A-Za-z0-9_-]{1,64}\.json$")
DB_LOCK = threading.Lock()

def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def canonical_hash(payload: dict) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()

def load_node_doc(path: Path) -> dict:
    if not path.exists(): return {"nodo": MI_ID, "genesis": "SYNCRO", "events": []}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(doc, dict) and isinstance(doc.get("events"), list): return doc
    except: pass
    return {"nodo": MI_ID, "genesis": "SYNCRO", "events": []}

def atomic_write_json(path: Path, data: dict) -> None:
    tmp_path = path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp_path, path)

def verify_event_chain(doc: dict) -> bool:
    if not isinstance(doc, dict) or not isinstance(doc.get("events"), list): return False
    prev = "GENESIS"
    for ev in doc["events"]:
        if not isinstance(ev, dict): return False
        expected_hash = ev.get("entry_hash")
        if ev.get("prev_hash") != prev or not isinstance(expected_hash, str): return False
        unsigned = {k: v for k, v in ev.items() if k != "entry_hash"}
        if canonical_hash(unsigned) != expected_hash: return False
        prev = expected_hash
    return True

class MeshHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None: return
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("/", "/nodes"):
            files = sorted(p.name for p in DATA_DIR.iterdir() if p.is_file() and FILENAME_RE.fullmatch(p.name))
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            self.wfile.write(json.dumps({"nodo": MI_ID, "files": files}).encode())
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
        log(f"MESH SEGURO ACTIVO: http://{get_local_ip()}:{PORT}")
        httpd.serve_forever()

def sync_from_host(ip: str, local_ip: str) -> None:
    if ip == local_ip: return
    try:
        req = urllib.request.Request(f"http://{ip}:{PORT}/nodes", headers={"User-Agent": "SYNCRO"})
        with urllib.request.urlopen(req, timeout=0.45) as resp:
            index = json.loads(resp.read(64 * 1024).decode("utf-8"))
    except: return
    for fname in index.get("files", []):
        if fname == DB_PATH.name: continue
        try:
            f_req = urllib.request.Request(f"http://{ip}:{PORT}/{fname}", headers={"User-Agent": "SYNCRO"})
            with urllib.request.urlopen(f_req, timeout=1.5) as f_resp:
                raw = f_resp.read(MAX_PAYLOAD_BYTES + 1)
                if len(raw) > MAX_PAYLOAD_BYTES: continue
                remote_doc = json.loads(raw.decode("utf-8"))
                if not verify_event_chain(remote_doc): continue
                dest = DATA_DIR / fname
                with DB_LOCK:
                    if len(remote_doc["events"]) >= len(load_node_doc(dest)["events"]):
                        atomic_write_json(dest, remote_doc)
                        log(f"SYNC OK: {fname} de {ip}")
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
        log(f"DECISION: {decision}")
        buscar_y_sincronizar()
        time.sleep(30)

if __name__ == "__main__":
    main()
