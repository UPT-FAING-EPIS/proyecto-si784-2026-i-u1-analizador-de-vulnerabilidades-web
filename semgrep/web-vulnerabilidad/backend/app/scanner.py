from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from html import unescape
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

from .schemas import DEFAULT_MODULES


SEVERITY_POINTS = {"critical": 40, "high": 25, "medium": 12, "low": 5, "info": 1}
SQL_ERROR_PATTERNS = [
    "you have an error in your sql syntax",
    "warning: mysql",
    "unclosed quotation mark",
    "quoted string not properly terminated",
    "sqlite error",
    "postgresql query failed",
    "ora-01756",
    "sqlstate",
    "mysql_fetch",
]
OPEN_REDIRECT_PARAMS = {"next", "url", "redirect", "redirect_uri", "return", "returnurl", "dest", "destination"}
CSRF_NAMES = {"csrf", "csrf_token", "_csrf", "_token", "authenticity_token", "xsrf", "xsrf_token"}


@dataclass
class FetchedPage:
    url: str
    response: requests.Response
    body: str
    ssl_error: bool = False


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("La URL objetivo debe usar http o https.")
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", "", parsed.query, ""))


def same_origin(base_url: str, candidate: str) -> bool:
    base = urlparse(base_url)
    other = urlparse(candidate)
    return other.scheme in {"http", "https"} and other.netloc == base.netloc


def replace_param(url: str, param: str, value: str) -> str:
    parsed = urlparse(url)
    params = parse_qsl(parsed.query, keep_blank_values=True)
    updated = [(key, value if key == param else current) for key, current in params]
    return urlunparse(parsed._replace(query=urlencode(updated, doseq=True)))


def build_vulnerability(
    module: str,
    severity: str,
    title: str,
    description: str,
    evidence: str | None,
    remediation: str,
    url: str,
    parameter: str | None = None,
) -> dict:
    return {
        "module": module,
        "severity": severity,
        "title": title,
        "description": description,
        "evidence": evidence,
        "remediation": remediation,
        "url": url,
        "parameter": parameter,
    }


def crawl_pages(target_url: str, depth: int, timeout: int) -> list[FetchedPage]:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "WebVulnerabilityScanner/1.0 (authorized security assessment)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
    )

    visited: set[str] = set()
    pages: list[FetchedPage] = []
    queue: deque[tuple[str, int]] = deque([(target_url, 0)])
    max_pages = 20

    while queue and len(pages) < max_pages:
        current_url, current_depth = queue.popleft()
        if current_url in visited:
            continue
        visited.add(current_url)

        ssl_error_detected = False
        try:
            response = session.get(current_url, timeout=timeout, allow_redirects=True, verify=True)
        except requests.exceptions.SSLError:
            ssl_error_detected = True
            try:
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                response = session.get(current_url, timeout=timeout, allow_redirects=True, verify=False)
            except requests.RequestException:
                continue
        except requests.RequestException:
            continue

        body = response.text[:500_000]
        pages.append(FetchedPage(url=response.url, response=response, body=body, ssl_error=ssl_error_detected))

        content_type = response.headers.get("content-type", "")
        if current_depth >= depth or "text/html" not in content_type:
            continue

        soup = BeautifulSoup(body, "html.parser")
        for anchor in soup.find_all("a", href=True):
            href = unescape(anchor.get("href", "")).strip()
            absolute = normalize_discovered_url(target_url, response.url, href)
            if absolute and same_origin(target_url, absolute) and absolute not in visited:
                queue.append((absolute, current_depth + 1))

    if not pages:
        raise RuntimeError("No se pudo obtener ninguna pagina del objetivo.")

    return pages


def normalize_discovered_url(target_url: str, current_url: str, href: str) -> str | None:
    if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None
    absolute = urljoin(current_url, href)
    parsed = urlparse(absolute)
    if parsed.scheme not in {"http", "https"}:
        return None
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", "", parsed.query, ""))


def check_headers(page: FetchedPage) -> list[dict]:
    headers = {key.lower(): value for key, value in page.response.headers.items()}
    checks = [
        (
            "content-security-policy",
            "medium",
            "Content-Security-Policy ausente",
            "La respuesta no define una politica CSP, lo que aumenta el impacto de XSS y carga de recursos no confiables.",
            "Definir una politica CSP restrictiva y monitorear violaciones en modo report-only antes de endurecerla.",
        ),
        (
            "x-frame-options",
            "medium",
            "X-Frame-Options ausente",
            "La aplicacion podria ser embebida en iframes y quedar expuesta a clickjacking.",
            "Configurar X-Frame-Options DENY/SAMEORIGIN o frame-ancestors en CSP.",
        ),
        (
            "x-content-type-options",
            "low",
            "X-Content-Type-Options ausente",
            "El navegador podria intentar interpretar recursos con un tipo distinto al declarado.",
            "Agregar X-Content-Type-Options: nosniff.",
        ),
        (
            "referrer-policy",
            "low",
            "Referrer-Policy ausente",
            "Las URLs completas podrian filtrarse como referrer hacia sitios externos.",
            "Configurar Referrer-Policy, por ejemplo strict-origin-when-cross-origin.",
        ),
        (
            "permissions-policy",
            "low",
            "Permissions-Policy ausente",
            "No se restringe explicitamente el uso de APIs sensibles del navegador.",
            "Definir Permissions-Policy segun las funciones realmente necesarias.",
        ),
        (
            "x-xss-protection",
            "low",
            "X-XSS-Protection ausente",
            "La cabecera X-XSS-Protection no esta configurada, lo que expone a navegadores antiguos a ataques de script reflejado.",
            "Agregar X-XSS-Protection: 1; mode=block.",
        ),
    ]

    vulnerabilities = []
    for header, severity, title, description, remediation in checks:
        if header not in headers:
            vulnerabilities.append(
                build_vulnerability(
                    "headers",
                    severity,
                    title,
                    description,
                    None,
                    remediation,
                    page.url,
                )
            )

    if page.url.startswith("https://") and "strict-transport-security" not in headers:
        vulnerabilities.append(
            build_vulnerability(
                "headers",
                "medium",
                "Strict-Transport-Security ausente",
                "El sitio usa HTTPS pero no anuncia HSTS, por lo que clientes recurrentes no quedan protegidos contra downgrade.",
                None,
                "Agregar Strict-Transport-Security con max-age suficiente y evaluar includeSubDomains.",
                page.url,
            )
        )

    content_type = headers.get("content-type", "")
    if "text/html" in content_type and "charset" not in content_type:
        vulnerabilities.append(
            build_vulnerability(
                "headers",
                "info",
                "Charset no especificado en Content-Type",
                "La respuesta no declara explicitamente la codificacion de caracteres (charset) en la cabecera Content-Type, lo que podria provocar que el navegador malinterprete la codificacion.",
                content_type,
                "Especificar siempre la codificacion en la cabecera, por ejemplo: Content-Type: text/html; charset=utf-8.",
                page.url,
            )
        )

    if page.ssl_error:
        vulnerabilities.append(
            build_vulnerability(
                "headers",
                "low",
                "Error de verificacion SSL/TLS",
                "El servidor utiliza un certificado SSL/TLS no valido, autofirmado o vencido. Esto expone a los usuarios a ataques de intermediario (MitM).",
                None,
                "Instalar un certificado SSL valido emitido por una autoridad certificadora de confianza (por ejemplo, Let's Encrypt).",
                page.url,
            )
        )

    return vulnerabilities


def check_info_disclosure(page: FetchedPage) -> list[dict]:
    vulnerabilities = []
    server = page.response.headers.get("server")
    powered_by = page.response.headers.get("x-powered-by")
    if server:
        vulnerabilities.append(
            build_vulnerability(
                "info_disclosure",
                "low",
                "Cabecera Server expone tecnologia",
                "La cabecera Server revela informacion que puede ayudar a perfilar el stack.",
                server[:300],
                "Reducir o eliminar banners de version en el servidor web o proxy.",
                page.url,
            )
        )
    if powered_by:
        vulnerabilities.append(
            build_vulnerability(
                "info_disclosure",
                "low",
                "Cabecera X-Powered-By expone tecnologia",
                "La cabecera X-Powered-By revela framework o runtime de la aplicacion.",
                powered_by[:300],
                "Eliminar X-Powered-By en framework, servidor o proxy.",
                page.url,
            )
        )

    body = page.body.lower()
    indicators = [
        "traceback (most recent call last)",
        "stack trace",
        "debug mode",
        "notice: undefined",
        "warning: include",
        "fatal error",
        "database error",
        "exception in thread",
    ]
    for indicator in indicators:
        if indicator in body:
            vulnerabilities.append(
                build_vulnerability(
                    "info_disclosure",
                    "medium",
                    "Mensaje tecnico visible",
                    "La respuesta contiene trazas o mensajes tecnicos que podrian revelar rutas, consultas o detalles internos.",
                    indicator,
                    "Deshabilitar debug en produccion y retornar paginas de error genericas con logging interno.",
                    page.url,
                )
            )
            break

    return vulnerabilities


def check_csrf(page: FetchedPage) -> list[dict]:
    soup = BeautifulSoup(page.body, "html.parser")
    vulnerabilities = []
    for form in soup.find_all("form"):
        method = (form.get("method") or "get").lower()
        if method != "post":
            continue
        token_found = False
        for input_node in form.find_all("input"):
            name = (input_node.get("name") or "").lower()
            input_type = (input_node.get("type") or "").lower()
            if input_type == "hidden" and any(token in name for token in CSRF_NAMES):
                token_found = True
                break
        if not token_found:
            action = urljoin(page.url, form.get("action") or page.url)
            vulnerabilities.append(
                build_vulnerability(
                    "csrf",
                    "medium",
                    "Formulario POST sin token CSRF visible",
                    "Se detecto un formulario POST sin un campo oculto que parezca token anti-CSRF.",
                    f"action={action}",
                    "Agregar tokens CSRF por sesion o por request y validar SameSite en cookies de autenticacion.",
                    page.url,
                )
            )
    return vulnerabilities


def check_reflected_xss(page: FetchedPage, timeout: int) -> list[dict]:
    parsed = urlparse(page.url)
    params = parse_qsl(parsed.query, keep_blank_values=True)
    if not params:
        return []

    vulnerabilities = []
    session = requests.Session()
    payload = "<script>alert(1337)</script>"
    for name, _ in params[:8]:
        test_url = replace_param(page.url, name, payload)
        try:
            response = session.get(test_url, timeout=timeout, allow_redirects=True)
        except requests.RequestException:
            continue
        if payload in response.text:
            vulnerabilities.append(
                build_vulnerability(
                    "xss",
                    "high",
                    "Reflejo directo de payload XSS",
                    "Un parametro se refleja sin codificacion contextual aparente en la respuesta HTML.",
                    payload,
                    "Codificar salida segun contexto, validar entradas y reforzar con CSP.",
                    response.url,
                    name,
                )
            )
    return vulnerabilities


def check_sqli(page: FetchedPage, timeout: int) -> list[dict]:
    parsed = urlparse(page.url)
    params = parse_qsl(parsed.query, keep_blank_values=True)
    if not params:
        return []

    vulnerabilities = []
    baseline = page.body.lower()
    session = requests.Session()
    for name, current_value in params[:8]:
        test_url = replace_param(page.url, name, f"{current_value}'")
        try:
            response = session.get(test_url, timeout=timeout, allow_redirects=True)
        except requests.RequestException:
            continue
        body = response.text.lower()
        for pattern in SQL_ERROR_PATTERNS:
            if pattern in body and pattern not in baseline:
                vulnerabilities.append(
                    build_vulnerability(
                        "sqli",
                        "high",
                        "Error SQL inducido por parametro",
                        "El parametro produjo un mensaje de error SQL, senal de posible inyeccion basada en errores.",
                        pattern,
                        "Usar consultas parametrizadas, ORM seguro y manejo de errores generico.",
                        response.url,
                        name,
                    )
                )
                break
    return vulnerabilities


def check_open_redirect(page: FetchedPage, timeout: int) -> list[dict]:
    parsed = urlparse(page.url)
    params = parse_qsl(parsed.query, keep_blank_values=True)
    if not params:
        return []

    vulnerabilities = []
    session = requests.Session()
    payload = "https://example.com"
    for name, _ in params[:8]:
        if name.lower() not in OPEN_REDIRECT_PARAMS:
            continue
        test_url = replace_param(page.url, name, payload)
        try:
            response = session.get(test_url, timeout=timeout, allow_redirects=False)
        except requests.RequestException:
            continue
        location = response.headers.get("location", "")
        if response.status_code in {301, 302, 303, 307, 308} and location.startswith(payload):
            vulnerabilities.append(
                build_vulnerability(
                    "open_redirect",
                    "medium",
                    "Redireccion abierta",
                    "La aplicacion redirige hacia un dominio externo controlado por un parametro.",
                    f"Location: {location}",
                    "Permitir solo rutas relativas o destinos externos en lista de confianza.",
                    test_url,
                    name,
                )
            )
    return vulnerabilities


def probe_sensitive_files(target_url: str, timeout: int) -> list[dict]:
    parsed = urlparse(target_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    probes = ["/.env", "/phpinfo.php", "/server-status"]
    vulnerabilities = []
    session = requests.Session()
    for path in probes:
        url = f"{base}{path}"
        try:
            response = session.get(url, timeout=timeout, allow_redirects=False)
        except requests.RequestException:
            continue
        text = response.text[:5000].lower()
        if path == "/.env" and response.status_code == 200 and any(key in text for key in ["db_password", "secret", "app_key"]):
            vulnerabilities.append(
                build_vulnerability(
                    "info_disclosure",
                    "critical",
                    "Archivo .env expuesto",
                    "Se pudo acceder a un archivo de variables de entorno con posibles secretos.",
                    url,
                    "Bloquear archivos sensibles desde el servidor web y rotar credenciales expuestas.",
                    url,
                )
            )
        elif path == "/phpinfo.php" and response.status_code == 200 and "php version" in text:
            vulnerabilities.append(
                build_vulnerability(
                    "info_disclosure",
                    "high",
                    "phpinfo expuesto",
                    "La pagina phpinfo revela configuracion detallada del runtime.",
                    url,
                    "Eliminar phpinfo.php en produccion.",
                    url,
                )
            )
        elif path == "/server-status" and response.status_code == 200 and "server status" in text:
            vulnerabilities.append(
                build_vulnerability(
                    "info_disclosure",
                    "medium",
                    "server-status expuesto",
                    "El endpoint de estado del servidor parece accesible publicamente.",
                    url,
                    "Restringir server-status por IP o deshabilitarlo.",
                    url,
                )
            )
    return vulnerabilities


def calculate_risk_score(vulnerabilities: list[dict]) -> int:
    score = sum(SEVERITY_POINTS.get(item.get("severity", "info").lower(), 0) for item in vulnerabilities)
    return min(score, 100)


def scan_target(target_url: str, modules: list[str], depth: int, timeout: int) -> tuple[list[dict], int]:
    enabled_modules = set(modules or DEFAULT_MODULES)
    normalized = normalize_url(target_url)
    pages = crawl_pages(normalized, depth, timeout)
    vulnerabilities: list[dict] = []

    for page in pages:
        if "headers" in enabled_modules:
            vulnerabilities.extend(check_headers(page))
        if "info_disclosure" in enabled_modules:
            vulnerabilities.extend(check_info_disclosure(page))
        if "csrf" in enabled_modules:
            vulnerabilities.extend(check_csrf(page))
        if "xss" in enabled_modules:
            vulnerabilities.extend(check_reflected_xss(page, timeout))
        if "sqli" in enabled_modules:
            vulnerabilities.extend(check_sqli(page, timeout))
        if "open_redirect" in enabled_modules:
            vulnerabilities.extend(check_open_redirect(page, timeout))

    if "info_disclosure" in enabled_modules:
        vulnerabilities.extend(probe_sensitive_files(normalized, timeout))

    return vulnerabilities, calculate_risk_score(vulnerabilities)

