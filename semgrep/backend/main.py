"""
VulnScan Pro - Backend Principal
FastAPI + MySQL + DeepSeek AI + Scanner Avanzado
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,https://149.34.48.176"
).split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from database import init_db
    init_db()
    yield


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="VulnScan Pro API",
    description="Plataforma profesional de análisis y escaneo de vulnerabilidades web con IA",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ── Security headers middleware ───────────────────────────────────────────────

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# ── Routers ───────────────────────────────────────────────────────────────────

from routes.auth_routes import router as auth_router
from routes.scan_routes import router as scan_router
from routes.admin_routes import router as admin_router
from routes.report_routes import router as report_router
from solutions_routes import router as solutions_router

app.include_router(auth_router)
app.include_router(scan_router)
app.include_router(admin_router)
app.include_router(report_router)
app.include_router(solutions_router)


# ── Health & info ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "version": "3.0.0", "environment": os.getenv("ENVIRONMENT", "production")}


@app.get("/api/modules", tags=["System"])
def list_modules():
    return {
        "modules": [
            {"id": "Headers", "name": "HTTP Headers", "description": "Analiza headers de seguridad HTTP"},
            {"id": "SSL", "name": "SSL/TLS", "description": "Verifica certificados y configuración SSL"},
            {"id": "XSS", "name": "Cross-Site Scripting", "description": "Detecta vulnerabilidades XSS"},
            {"id": "SQLi", "name": "SQL Injection", "description": "Detecta inyección SQL"},
            {"id": "CSRF", "name": "CSRF", "description": "Verifica tokens CSRF en formularios"},
            {"id": "OpenRedirect", "name": "Open Redirect", "description": "Detecta redirecciones abiertas"},
            {"id": "LFI", "name": "LFI / Path Traversal", "description": "Detecta inclusión de archivos locales"},
            {"id": "CommandInjection", "name": "Command Injection", "description": "Detecta inyección de comandos"},
            {"id": "SSRF", "name": "SSRF", "description": "Detecta Server-Side Request Forgery"},
            {"id": "SensitiveFiles", "name": "Archivos Sensibles", "description": "Busca archivos expuestos"},
            {"id": "HttpMethods", "name": "HTTP Methods", "description": "Verifica métodos HTTP peligrosos"},
            {"id": "ErrorDisclosure", "name": "Error Disclosure", "description": "Detecta divulgación de errores"},
            {"id": "Crawling", "name": "Crawling", "description": "Descubre URLs y endpoints"},
        ]
    }
