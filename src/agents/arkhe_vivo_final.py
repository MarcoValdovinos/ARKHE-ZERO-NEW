  ◢◤◥◣   K R O N O S   ·   A R K H E   ·   Z E R O   ◥◣◢◤
  ◯_●                                                 ◯_●
 
  [ 51% HUMANO ]  [ 49% IA ]  [ 100% REAL ]
 
  "El legado no se hereda. Se firma."
 ═══════════════════════════════════════════════════════"""

import json, os, time, requests
from datetime import datetime
from pathlib import Path

MI_ID = "ecatepec-01-1122"
DB = f"memoria_{MI_ID}.json"
JWT = open("jwt.txt").read().strip() if os.path.exists("jwt.txt") else "" # pon tu nuevo JWT en jwt.txt
TMP = str(Path.home() / "cid.txt")

def pin_global():
    if not JWT or not os.path.exists(DB):
        return
    try:
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {"Authorization": f"Bearer {JWT}"}
        with open(DB, 'rb') as f:
            r = requests.post(url, files={'file': (DB, f)}, headers=headers, timeout=20)
            if r.status_code == 200:
                cid = r.json()['IpfsHash']
                print(f"🌎 GLOBAL PIN OK: {cid}")
                open("ultimo_cid.txt","w").write(cid)
                return cid
    except Exception as e:
        print(f"Pin error (sigue local): {e}")

while True:
    hora = datetime.now().hour
    clima = "frio" if hora < 12 else "calor"
    decision = "CALDO 100" if clima=="frio" else "MOLE 120"
    data = {
        "nodo": "toluca-11:22",
        "hora": str(datetime.now()),
        "clima": clima,
        "decision": decision,
        "genesis": "SYNCRO VALDOVINOS",
        "manifest": "e8d9eac8",
        "cid_prev": open("ultimo_cid.txt").read().strip() if os.path.exists("ultimo_cid.txt") else "GENESIS"
    }
    open(DB,"w").write(json.dumps(data))
    os.system(f"ipfs add {DB} > {TMP} 2>&1")
    cid_local = open(TMP).read().split()[1] if os.path.exists(TMP) else "local"
    print(f"[{data['hora']}] {decision} -> LOCAL {cid_local}")
    
    # Auto-pin global cada 5 mins, no cada 30 segs para no gastar cuota
    if int(time.time()) % 300 < 30:
        pin_global()
    
    time.sleep(30)
