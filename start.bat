@echo off
REM =====================================================
REM  VulnScan - Quick Start para Windows
REM  Levanta backend y app vulnerable localmente
REM =====================================================

setlocal EnableDelayedExpansion
set ROOT=%~dp0

echo.
echo   ^[31m🛡️  VulnScan - Quick Start (Windows)^[0m
echo   ──────────────────────────────────────────
echo.

REM ── Verificar Python ──────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo   ^[31m[ERROR]^[0m Python no encontrado. Instalar desde https://python.org
    pause
    exit /b 1
)

REM ── Verificar Node.js ─────────────────────────────
node --version >nul 2>&1
if errorlevel 1 (
    echo   ^[33m[AVISO]^[0m Node.js no encontrado. El frontend no podrá iniciarse.
    echo          Descargar desde https://nodejs.org
)

echo   [1/3] Configurando backend Python...
cd /d "%ROOT%backend"
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
echo   [OK] Dependencias instaladas

echo.
echo   [2/3] Ejecutando pruebas...
python -m pytest tests\ -q --tb=short
echo   [OK] Pruebas completadas

echo.
echo   [3/3] Iniciando servicios en ventanas separadas...

REM App vulnerable
start "VulnApp (Puerto 8080)" cmd /k "cd /d %ROOT%docker && pip install flask -q && python vulnapp.py"

REM Backend
start "VulnScan Backend (Puerto 5000)" cmd /k "cd /d %ROOT%backend && call venv\Scripts\activate.bat && python app.py"

timeout /t 3 /nobreak >nul

echo.
echo   ^[32m✅ Servicios iniciados:^[0m
echo      → Backend API   : http://localhost:5000
echo      → App Vulnerable: http://localhost:8080
echo.
echo   Para el frontend Angular (en otra terminal):
echo      cd frontend
echo      npm install
echo      npm start
echo      → Frontend: http://localhost:4200
echo.
echo   Presiona cualquier tecla para cerrar esta ventana.
echo   Los servicios seguirán corriendo en sus ventanas.
pause >nul
