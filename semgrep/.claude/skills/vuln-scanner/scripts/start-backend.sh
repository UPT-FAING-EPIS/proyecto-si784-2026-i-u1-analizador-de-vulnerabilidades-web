#!/usr/bin/env bash
# Arranca el backend local del Web Vulnerability Scanner para que la skill funcione.
# Uso: bash .claude/skills/vuln-scanner/scripts/start-backend.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/../../../../web-vulnerabilidad/backend"

cd "$BACKEND_DIR"

if [ ! -f "venv_win/Scripts/python.exe" ]; then
  echo "No se encontro venv_win. Creando entorno virtual e instalando dependencias..."
  python -m venv venv_win
  ./venv_win/Scripts/python.exe -m pip install --upgrade pip -q
  ./venv_win/Scripts/python.exe -m pip install -r requirements.txt -q
fi

echo "Iniciando backend en http://127.0.0.1:8000 ..."
exec ./venv_win/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
