#!/bin/bash
cd ~/ARKHE-ZERO-NEW/src/mesh/
# Mata cualquier mesh viejo atorado
pkill -9 -f syncro_mesh_v2.py 2>/dev/null
sleep 1
nohup python3 syncro_mesh_v2.py > ~/mesh.log 2>&1 &
echo "MESH arrancado, log en ~/mesh.log"
