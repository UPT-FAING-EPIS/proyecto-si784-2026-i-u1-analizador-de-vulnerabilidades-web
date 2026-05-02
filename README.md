# Escáner de Vulnerabilidades Web

Este proyecto consiste en un escáner de vulnerabilidades web con un frontend en **Next.js** y un backend en **Python (FastAPI)**, usando **SQLite** como base de datos local.

## Estructura del Proyecto

- `frontend/`: Aplicación en Next.js (App Router, Tailwind CSS, TypeScript).
- `backend/`: API en FastAPI con SQLAlchemy y SQLite.

## Requisitos
- Node.js
- Python 3
- npm / yarn / pnpm

## Cómo ejecutar el Frontend

1. Abre una terminal y navega a la carpeta `frontend`:
   ```bash
   cd frontend
   ```
2. Instala las dependencias (si no se instalaron automáticamente):
   ```bash
   npm install
   ```
3. Ejecuta el servidor de desarrollo:
   ```bash
   npm run dev
   ```
   El frontend estará disponible en `http://localhost:3000`.

## Cómo ejecutar el Backend

1. Abre otra terminal y navega a la carpeta `backend`:
   ```bash
   cd backend
   ```
2. Activa el entorno virtual (ya ha sido creado):
   ```bash
   source venv/bin/activate
   ```
3. Ejecuta el servidor de FastAPI:
   ```bash
   uvicorn main:app --reload
   ```
   El backend estará disponible en `http://localhost:8000`. Puedes acceder a la documentación interactiva en `http://localhost:8000/docs`.

## Siguientes pasos
- Integrar las herramientas de escaneo en FastAPI.
- Diseñar la interfaz en Next.js para enviar URLs y ver los resultados.
- Configurar endpoints para guardar el historial de escaneos en la base de datos SQLite.
