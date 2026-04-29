# Changelog

Todos los cambios notables de VulnScan se documentan en este archivo.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.1.0/).

---

## [1.0.0] — 2024-01-01

### Añadido

#### Backend (Flask + Python)
- **Core Engine** (`core/engine.py`): orquestador del pipeline completo con soporte de progreso async
- **WebCrawler** (`crawler/spider.py`): descubrimiento de URLs, formularios y endpoints parametrizados
- **XSSScanner** (`scanners/xss_scanner.py`): 8 payloads, detección de reflexión en parámetros y forms
- **SQLiScanner** (`scanners/sqli_scanner.py`): error-based y time-based con 12 firmas de motores SQL
- **HeaderScanner** (`scanners/header_scanner.py`): 6 cabeceras OWASP + disclosure + cookies inseguras
- **CSRFScanner** (`scanners/csrf_scanner.py`): detección de formularios POST sin token CSRF
- **RedirectScanner** (`scanners/redirect_scanner.py`): Open Redirect en 14 parámetros comunes
- **InfoDisclosureScanner** (`scanners/info_disclosure_scanner.py`): 24 rutas sensibles + 12 patrones regex
- **RuleEngine** (`rules/engine.py`): clasificación OWASP Top 10:2021, CWE, CVSS range, severidad
- **ReportGenerator** (`reports/generator.py`): reportes JSON y HTML autónomos
- **HTTPClient** (`utils/http_client.py`): sesión centralizada con retry, timeout, SSL configurable
- **API REST** (`api/routes.py`): endpoints POST /scan, GET /scan/{id}, GET /scans, GET /scan/{id}/report
- **59 pruebas unitarias** distribuidas en 3 archivos de test

#### Frontend (Angular 17)
- **NavbarComponent**: barra de navegación con badge de contador de hallazgos
- **ScannerComponent**: formulario reactivo con opciones de módulos, profundidad, timeout y barra de progreso
- **ResultsComponent**: vista de hallazgos con filtros por severidad/tipo, búsqueda y cards expandibles
- **HistoryComponent**: historial persistente en localStorage con carga de escaneos anteriores
- **ReportComponent**: reporte visual completo con exportación JSON/HTML y cobertura OWASP
- **ScanService**: cliente HTTP con polling reactivo (RxJS interval + takeWhile)
- **StateService**: estado compartido entre componentes sin NgRx
- **SeverityPipe**: transformación de severidades al español
- Estilos globales con CSS variables para modo oscuro completo

#### Infraestructura Docker
- `docker-compose.yml`: tres servicios (frontend, backend, vulnapp)
- `docker/vulnapp.py`: aplicación Flask intencionalmente vulnerable con XSS, SQLi, CSRF y headers faltantes
- `frontend/nginx.conf`: proxy inverso de `/api/*` al backend Flask
- `frontend/Dockerfile`: build multietapa Angular → Nginx

#### Herramientas de desarrollo
- `Makefile`: comandos `up`, `down`, `build`, `logs`, `backend`, `frontend`, `test`, `clean`
- `start.sh`: script de inicio rápido para Linux/Mac
- `start.bat`: script de inicio rápido para Windows
- `docs/INSTALL.md`: guía de instalación y troubleshooting
- `docs/EXTENDING.md`: guía para agregar nuevos módulos scanner

### Vulnerabilidades cubiertas

| ID | Categoría OWASP | Scanner | CWE |
|----|----------------|---------|-----|
| A01 | Broken Access Control | csrf_scanner, redirect_scanner | CWE-352, CWE-601 |
| A03 | Injection | xss_scanner, sqli_scanner | CWE-79, CWE-89 |
| A05 | Security Misconfiguration | header_scanner, info_disclosure_scanner | CWE-16 |

---

## [Próxima versión] — Planificado

### Por añadir
- `ssrf_scanner.py` — Server-Side Request Forgery (CWE-918)
- `xxe_scanner.py` — XML External Entity Injection (CWE-611)
- `cors_scanner.py` — CORS mal configurado (CWE-942)
- `auth_scanner.py` — Credenciales por defecto y fuerza bruta (CWE-287)
- Persistencia de escaneos en SQLite (reemplaza store en memoria)
- Autenticación básica en la API REST
- Soporte para escaneo autenticado (session cookies, Bearer tokens)
- Dashboard con gráficos de tendencia histórica
