#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_API_URL = "https://vulnerabilidad-web.sytes.net/backend"
DEFAULT_MODULES = ["xss", "sqli", "headers", "csrf", "open_redirect", "info_disclosure"]
POLL_INTERVAL_SECONDS = 3


def load_local_env() -> None:
    """Carga .env.local (junto a este script) sin pisar variables ya exportadas."""
    env_file = Path(__file__).resolve().parent.parent / ".env.local"
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def api_request(method: str, url: str, api_key: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code in (401, 403):
            raise SystemExit(
                f"Error de autenticacion ({exc.code}): la API key es invalida o fue "
                f"revocada. Genera una nueva desde el dashboard.\nDetalle: {body}"
            )
        raise SystemExit(f"Error HTTP {exc.code} llamando a {url}: {body}")
    except urllib.error.URLError as exc:
        raise SystemExit(f"No se pudo conectar a {url}: {exc.reason}")


def format_report(target_url: str, detail: dict) -> str:
    vulns = detail.get("vulnerabilities", [])
    risk_score = detail.get("risk_score")

    if not vulns:
        return f"Escaneo completado. No se encontraron vulnerabilidades en {target_url}."

    lines = [
        f"Se encontraron {len(vulns)} vulnerabilidad(es) en {target_url} "
        f"(Puntuacion de riesgo: {risk_score}/100):",
        "",
    ]
    for v in vulns:
        lines.append(f"- [{v['severity'].upper()}] {v['title']}")
        lines.append(f"  {v['description']}")
        lines.append(f"  Recomendacion: {v['remediation']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Escanea una URL con Web Vulnerability Scanner")
    parser.add_argument("target_url", help="URL objetivo a escanear")
    parser.add_argument("--depth", type=int, default=1, help="Profundidad de rastreo (0-3)")
    parser.add_argument(
        "--modules",
        type=str,
        default=",".join(DEFAULT_MODULES),
        help="Modulos separados por coma (ej. xss,sqli,headers)",
    )
    parser.add_argument("--timeout", type=int, default=10, help="Timeout por request (3-30s)")
    args = parser.parse_args()

    load_local_env()

    api_key = os.environ.get("WVS_API_KEY")
    if not api_key:
        print(
            "Error: la variable de entorno WVS_API_KEY no esta configurada. "
            "Genera una API key desde el dashboard del scanner y expórtala antes de "
            "usar esta skill.",
            file=sys.stderr,
        )
        return 1

    api_base_url = os.environ.get("WVS_API_URL", DEFAULT_API_URL).rstrip("/")
    modules = [m.strip() for m in args.modules.split(",") if m.strip()]

    payload = {
        "target_url": args.target_url,
        "modules": modules,
        "depth": args.depth,
        "timeout": args.timeout,
    }

    scan = api_request("POST", f"{api_base_url}/api/integrations/scans", api_key, payload)
    scan_id = scan["id"]
    print(f"Escaneo {scan_id} creado para {args.target_url}, esperando resultados...")

    while True:
        time.sleep(POLL_INTERVAL_SECONDS)
        detail = api_request("GET", f"{api_base_url}/api/integrations/scans/{scan_id}", api_key)
        status = detail["status"]
        if status in ("completed", "failed"):
            break

    if status == "failed":
        print(f"El escaneo fallo: {detail.get('error_message')}", file=sys.stderr)
        return 1

    print(format_report(args.target_url, detail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
