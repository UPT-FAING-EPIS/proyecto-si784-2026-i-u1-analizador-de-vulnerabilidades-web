# Web Vulnerability Scanner

Sistema web desacoplado para escanear vulnerabilidades comunes en aplicaciones web.

## Estructura

- `backend/`: API REST FastAPI, autenticacion JWT, SQLAlchemy y escaner modular.
- `frontend/`: Next.js App Router con login, registro, dashboard, historial y reportes.

## Arranque rapido

Backend:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.init_db
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

URLs:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## Variables principales

Edita `backend/.env` y `frontend/.env.local` si cambian la base de datos o las URLs locales.

