#!/data/data/com.termux/files/usr/bin/bash
cd ~/sycro-web/web && npx next build --webpack && git add . && git commit -m "ΔΨΩ∞ deploy $(date +%H:%M)" && git push
