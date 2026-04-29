# 🛡️ VulnScan – Web Vulnerability Analysis System

> A full-stack security testing tool aligned to the OWASP Top 10:2021, built with Angular + Flask and deployable via Docker.

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Quick Start with Docker](#quick-start-with-docker)
- [Local Development Setup](#local-development-setup)
- [API Reference](#api-reference)
- [Scanner Modules](#scanner-modules)
- [Project Structure](#project-structure)
- [Adding New Scanners](#adding-new-scanners)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (Angular 17)         Port 4200                    │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │ ScannerComp  │  │ ResultsComp   │  │  ReportComp     │  │
│  └──────┬───────┘  └───────────────┘  └─────────────────┘  │
│         │ ScanService (HttpClient)                          │
└─────────┼───────────────────────────────────────────────────┘
          │ REST API (JSON)
┌─────────┼───────────────────────────────────────────────────┐
│  Backend (Flask)               Port 5000                    │
│         │                                                   │
│  ┌──────▼──────────────────────────────────────────────┐   │
│  │              Core Engine (engine.py)                 │   │
│  │  ┌─────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │ Crawler │→ │ Scanners │→ │  Rules   │→ Results  │   │
│  │  └─────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
│  XSS Scanner │ SQLi Scanner │ Header Scanner │ CSRF Scanner  │
└─────────────────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────┐
│  VulnApp (Intentionally Vulnerable)    Port 8080            │
│  Flask app with XSS, SQLi, CSRF, missing headers            │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

| Module | Vulnerability | OWASP Category | CWE |
|--------|-------------|----------------|-----|
| XSS Scanner | Reflected XSS in URL params & forms | A03:2021 – Injection | CWE-79 |
| SQLi Scanner | Error-based & time-based SQLi | A03:2021 – Injection | CWE-89 |
| Header Scanner | Missing security headers, info disclosure | A05:2021 – Misconfiguration | CWE-16 |
| CSRF Scanner | Missing CSRF tokens on POST forms | A01:2021 – Broken Access Control | CWE-352 |

---

## Quick Start with Docker

### Prerequisites
- Docker ≥ 24.0
- Docker Compose ≥ 2.20

### Launch everything with one command:

```bash
git clone https://github.com/your-org/vulnscan.git
cd vulnscan
docker-compose up --build
```

Access the services:
- **Frontend:** http://localhost:4200
- **Backend API:** http://localhost:5000/api
- **Vulnerable Test App:** http://localhost:8080

### Test scan target:
Enter `http://vulnapp:8080` (within Docker network) or `http://localhost:8080` from the host.

---

## Local Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python app.py
# API available at http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm start
# App available at http://localhost:4200
```

### Vulnerable Test App

```bash
cd docker
pip install flask
python vulnapp.py
# App at http://localhost:8080
```

---

## API Reference

### Start a scan
```
POST /api/scan
Content-Type: application/json

{
  "url": "http://localhost:8080",
  "scan_xss": true,
  "scan_sqli": true,
  "scan_headers": true,
  "scan_csrf": true,
  "max_depth": 2,
  "timeout": 10
}

Response 202:
{ "scan_id": "uuid", "status": "pending" }
```

### Poll scan status
```
GET /api/scan/{scan_id}

Response:
{
  "id": "...",
  "url": "...",
  "status": "completed",
  "progress": 100,
  "results": {
    "total_findings": 9,
    "severity_summary": { "critical": 2, "high": 3, "medium": 3, "low": 1 },
    "findings": [...]
  }
}
```

### Get HTML report
```
GET /api/scan/{scan_id}/report
Content-Type: text/html
```

### List all scans
```
GET /api/scans
```

---

## Scanner Modules

Each scanner implements the same interface:

```python
class MyScanner:
    def __init__(self, http_client: HTTPClient):
        self.http = http_client

    def scan(self, base_url: str, urls: list, forms: list, endpoints: list) -> list[dict]:
        """
        Returns a list of raw finding dicts.
        The Rule Engine will enrich and classify them.
        """
        ...
```

---

## Project Structure

```
vulnscan/
├── backend/
│   ├── app.py                # Flask app factory
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── api/
│   │   └── routes.py         # REST endpoints
│   ├── core/
│   │   └── engine.py         # Scan orchestrator
│   ├── crawler/
│   │   └── spider.py         # Link & form discovery
│   ├── scanners/
│   │   ├── xss_scanner.py
│   │   ├── sqli_scanner.py
│   │   ├── header_scanner.py
│   │   └── csrf_scanner.py
│   ├── rules/
│   │   └── engine.py         # OWASP classification
│   ├── reports/
│   │   └── generator.py      # JSON + HTML reports
│   └── utils/
│       └── http_client.py    # Centralized HTTP
│
├── frontend/
│   ├── package.json
│   ├── Dockerfile
│   ├── nginx.conf
│   └── src/
│       └── app/
│           ├── app.module.ts
│           ├── services/
│           │   └── scan.service.ts
│           └── components/
│               └── scanner/
│
├── docker/
│   ├── vulnapp.py            # Vulnerable test app
│   └── Dockerfile.vulnapp
│
├── docker-compose.yml
└── README.md
```

---

## Adding New Scanners

1. Create `backend/scanners/my_scanner.py` implementing the scanner interface above.
2. Add a rule to `backend/rules/engine.py` in `VULNERABILITY_RULES`.
3. Register the scanner in `backend/core/engine.py`:

```python
if self.options.get('scan_mymodule', True):
    scanners.append(('My Module', MyScanner(self.http), 'mytype'))
```

4. Add the option to the frontend scan options form.

No other files need modification — the architecture is fully modular.

---

## ⚠️ Legal Disclaimer

**VulnScan is intended exclusively for authorized security testing.**
Only use this tool against systems you own or have explicit written permission to test.
Unauthorized security testing is illegal and unethical.

---

## License

MIT License – See LICENSE file for details.
