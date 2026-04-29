# ═══════════════════════════════════════════════════════
#  VulnScan – Development Makefile
# ═══════════════════════════════════════════════════════

.PHONY: help up down build logs backend frontend vulnapp test lint clean

help:
	@echo ""
	@echo "  VulnScan – Comandos disponibles"
	@echo "  ─────────────────────────────────────"
	@echo "  make up        Levantar todos los servicios (Docker)"
	@echo "  make down      Detener y eliminar contenedores"
	@echo "  make build     Rebuildar imágenes Docker"
	@echo "  make logs      Ver logs de todos los servicios"
	@echo "  make backend   Correr backend localmente (Flask)"
	@echo "  make frontend  Correr frontend localmente (Angular)"
	@echo "  make vulnapp   Correr la app vulnerable localmente"
	@echo "  make test      Ejecutar pruebas del backend"
	@echo "  make clean     Limpiar artefactos de build"
	@echo ""

# ── Docker commands ───────────────────────────────────
up:
	docker-compose up --build -d
	@echo ""
	@echo "  ✅ Servicios iniciados:"
	@echo "  → Frontend:  http://localhost:4200"
	@echo "  → Backend:   http://localhost:5000"
	@echo "  → VulnApp:   http://localhost:8080"
	@echo ""

down:
	docker-compose down

build:
	docker-compose build --no-cache

logs:
	docker-compose logs -f

# ── Local dev commands ────────────────────────────────
backend:
	cd backend && \
	  python -m venv venv && \
	  . venv/bin/activate && \
	  pip install -r requirements.txt -q && \
	  python app.py

frontend:
	cd frontend && \
	  npm install && \
	  npm start -- --proxy-config proxy.conf.json

vulnapp:
	cd docker && pip install flask -q && python vulnapp.py

# ── Test ─────────────────────────────────────────────
test:
	cd backend && python -m pytest tests/ -v

# ── Clean ─────────────────────────────────────────────
clean:
	find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true
	rm -rf frontend/dist frontend/.angular
	@echo "Cleaned."
