  ◢◤◥◣   K R O N O S   ·   A R K H E   ·   Z E R O   ◥◣◢◤
  ◯_●                                                 ◯_●
 
  [ 51% HUMANO ]  [ 49% IA ]  [ 100% REAL ]
 
  "El legado no se hereda. Se firma."
 ═══════════════════════════════════════════════════════"""

import json, os, time
from datetime import datetime

while True:
    hora = datetime.now().hour
    clima = "frio" if hora < 12 else "calor"
    decision = "CALDO 100" if clima=="frio" else "MOLE 120"
    
    data = {
        "nodo": "toluca-11:22",
        "hora": str(datetime.now()),
        "clima": clima,
        "decision": decision,
        "genesis": "ARKHE ZERO",
        "manifest": "e8d9eac8"
    }
    open("memoria_ecatepec-01-1122.json","w").write(json.dumps(data))
    os.system("ipfs add memoria_ecatepec-01-1122.json > /tmp/c.txt 2>&1")
    cid = open("/tmp/c.txt").read().split()[1] if os.path.exists("/tmp/c.txt") else "offline"
    print(f"[{data['hora']}] {decision} -> CID: {cid}")
    time.sleep(30) # cada 30 seg decide solo
