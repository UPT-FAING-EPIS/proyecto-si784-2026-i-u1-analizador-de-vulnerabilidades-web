#!/usr/bin/env bash
# =============================================================
#  VulnScan – Quick Start (sin Docker)
#  Levanta backend, app vulnerable y muestra instrucciones
# =============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo -e "${CYAN}  🛡️  VulnScan – Quick Start${NC}"
echo -e "${CYAN}  ─────────────────────────────────────────${NC}"
echo ""

# ── Backend setup ──────────────────────────────────────────
echo -e "${YELLOW}[1/3] Configurando entorno Python del backend...${NC}"
cd "$ROOT/backend"
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt -q
echo -e "${GREEN}      ✅ Dependencias instaladas${NC}"

# ── Run tests ──────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[2/3] Ejecutando pruebas unitarias...${NC}"
python -m pytest tests/ -q --tb=short 2>&1
echo -e "${GREEN}      ✅ Pruebas OK${NC}"

# ── Start services ─────────────────────────────────────────
echo ""
echo -e "${YELLOW}[3/3] Iniciando servicios...${NC}"

# App vulnerable
cd "$ROOT/docker"
pip install flask -q
python vulnapp.py &
VULNAPP_PID=$!

# Backend
cd "$ROOT/backend"
python app.py &
BACKEND_PID=$!

sleep 2

echo ""
echo -e "${GREEN}  ✅ Servicios iniciados:${NC}"
echo -e "     → Backend API : ${CYAN}http://localhost:5000${NC}"
echo -e "     → App Vulnerable: ${CYAN}http://localhost:8080${NC}"
echo ""
echo -e "${YELLOW}  Para el frontend Angular, en otra terminal:${NC}"
echo -e "     cd frontend && npm install && npm start"
echo -e "     → Frontend: ${CYAN}http://localhost:4200${NC}"
echo ""
echo -e "  ${YELLOW}Presiona CTRL+C para detener todos los servicios.${NC}"
echo ""

# Wait and cleanup on exit
trap "echo ''; echo 'Deteniendo servicios...'; kill $VULNAPP_PID $BACKEND_PID 2>/dev/null; exit 0" INT TERM
wait
