#!/bin/bash

SELLO_JS="/* ═══════════════════════════════════════════════════════
 *  ◢◤◥◣   K R O N O S   ·   A R K H E   ·   Z E R O   ◥◣◢◤
 *  ◯_●                                                 ◯_●
 * 
 *  [ 51% HUMANO ]  [ 49% IA ]  [ 100% REAL ]
 * 
 *  \"El legado no se hereda. Se firma.\"
 * ═══════════════════════════════════════════════════════ */

"

SELLO_PY="\"\"\"═══════════════════════════════════════════════════════
  ◢◤◥◣   K R O N O S   ·   A R K H E   ·   Z E R O   ◥◣◢◤
  ◯_●                                                 ◯_●
 
  [ 51% HUMANO ]  [ 49% IA ]  [ 100% REAL ]
 
  \"El legado no se hereda. Se firma.\"
 ═══════════════════════════════════════════════════════\"\"\"

"

echo "🛡️ Iniciando Sellado del Ecosistema 51/49 (Ignorando librerías externas)..."

# Sellar archivos JavaScript/TypeScript (IGNORANDO node_modules, .next, qv-env)
find . -type d \( -name "node_modules" -o -name ".next" -o -name "qv-env" -o -name "venv" -o -name ".git" \) -prune -o -type f \( -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" \) -print | while read file; do
    if ! grep -q "El legado no se hereda" "$file"; then
        echo "$SELLO_JS$(cat "$file")" > "$file"
        echo "✅ Sellado: $file"
    fi
done

# Sellar archivos Python (IGNORANDO site-packages, qv-env, venv)
find . -type d \( -name "site-packages" -o -name "venv" -o -name "qv-env" -o -name ".git" \) -prune -o -type f -name "*.py" -print | while read file; do
    if ! grep -q "El legado no se hereda" "$file"; then
        echo "$SELLO_PY$(cat "$file")" > "$file"
        echo "✅ Sellado: $file"
    fi
done

echo "🏆 Sellado completado. El legado ha sido firmado."
