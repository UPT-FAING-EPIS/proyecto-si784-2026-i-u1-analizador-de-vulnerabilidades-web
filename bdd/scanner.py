"""
Motor de escaneo de vulnerabilidades web avanzado.
Detecta: SQLi, XSS, CSRF, SSRF, RCE, LFI, RFI, Command Injection,
Open Redirect, Headers inseguros, SSL/TLS, CORS, tecnologías y más.
"""
import re
import time
import socket
import ssl
import datetime
from typing import Optional
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse, urljoin
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

TIMEOUT = 10
HEADERS_UA = {
    "User-Agent": "Mozilla/5.0 (VulnScan Security Scanner 2.0; +https://github.com/vulnscan)"
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def safe_get(url: str, timeout: int = TIMEOUT, allow_redirects: bool = True, **kwargs):
    try:
        return requests.get(
            url,
            timeout=timeout,
            headers=HEADERS_UA,
            allow_redirects=allow_redirects,
            verify=False,
            **kwargs
        )
    except RequestException:
        return None


def inject_param(url: str, payload: str) -> str:
    parsed = urlparse(url)
    params = parse_qsl(parsed.query)
    if params:
        new_params = [(k, v + payload) for k, v in params]
    else:
        new_params = [("id", payload), ("q", payload)]
    return urlunparse(parsed._replace(query=urlencode(new_params)))


def vuln(vuln_type, severity, title, description, endpoint, payload="", evidence="", risk="", solution="", cwe=""):
    return {
        "vuln_type": vuln_type,
        "severity": severity,
        "title": title,
        "description": description,
        "endpoint": endpoint,
        "payload": payload,
        "evidence": evidence[:500] if evidence else "",
        "risk": risk,
        "solution": solution,
        "cwe_id": cwe,
    }


# ── Tecnologías ───────────────────────────────────────────────────────────────

def detect_technologies(url: str, timeout: int = TIMEOUT) -> dict:
    tech = {"server": [], "cms": [], "frameworks": [], "libraries": [], "cdn": [], "waf": []}
    resp = safe_get(url, timeout)
    if not resp:
        return tech

    headers = resp.headers
    body = resp.text.lower()

    # Server
    if "server" in headers:
        tech["server"].append(headers["server"])
    if "x-powered-by" in headers:
        tech["frameworks"].append(headers["x-powered-by"])

    # CMS
    cms_patterns = {
        "WordPress": ["/wp-content/", "/wp-includes/", "wp-json"],
        "Joomla": ["/components/com_", "joomla"],
        "Drupal": ["/sites/default/", "drupal"],
        "Magento": ["/mage/", "magento", "/skin/frontend/"],
        "PrestaShop": ["prestashop", "/themes/default-bootstrap/"],
        "Shopify": ["cdn.shopify.com", "shopify"],
        "Laravel": ["laravel_session", "laravel"],
        "Django": ["csrfmiddlewaretoken", "django"],
    }
    for name, patterns in cms_patterns.items():
        if any(p in body or p in str(headers) for p in patterns):
            tech["cms"].append(name)

    # JS Frameworks
    js_patterns = {
        "React": ["react", "__react", "react-dom"],
        "Vue.js": ["vue.js", "__vue__", "vuex"],
        "Angular": ["ng-version", "angular.min.js"],
        "jQuery": ["jquery", "jquery.min.js"],
        "Bootstrap": ["bootstrap.min.css", "bootstrap.bundle"],
        "Next.js": ["__next", "_next/static"],
    }
    for name, patterns in js_patterns.items():
        if any(p in body for p in patterns):
            tech["libraries"].append(name)

    # WAF
    waf_indicators = {
        "Cloudflare": ["cloudflare", "__cfduid", "cf-ray"],
        "AWS WAF": ["awselb", "x-amz-"],
        "Sucuri": ["sucuri", "x-sucuri-id"],
        "Imperva": ["incap_ses", "visid_incap"],
        "ModSecurity": ["mod_security", "modsecurity"],
    }
    for name, patterns in waf_indicators.items():
        if any(p in body or p in str(headers).lower() for p in patterns):
            tech["waf"].append(name)

    # CDN
    cdn_patterns = {"Cloudflare": ["cf-ray"], "AWS CloudFront": ["x-amz-cf-id"], "Fastly": ["x-fastly"]}
    for name, patterns in cdn_patterns.items():
        if any(p in str(headers).lower() for p in patterns):
            tech["cdn"].append(name)

    return tech


# ── Crawling ──────────────────────────────────────────────────────────────────

def crawl_urls(base_url: str, depth: int = 2, timeout: int = TIMEOUT) -> list:
    visited = set()
    to_visit = {base_url}
    found = []
    parsed_base = urlparse(base_url)

    for _ in range(depth):
        next_level = set()
        for url in to_visit:
            if url in visited or len(visited) > 50:
                continue
            visited.add(url)
            resp = safe_get(url, timeout)
            if not resp:
                continue
            found.append({"url": url, "status": resp.status_code, "content_type": resp.headers.get("content-type", "")})
            try:
                soup = BeautifulSoup(resp.text, "html.parser")
                for tag in soup.find_all(["a", "form", "script", "link"]):
                    href = tag.get("href") or tag.get("src") or tag.get("action")
                    if href:
                        full = urljoin(url, href)
                        p = urlparse(full)
                        if p.netloc == parsed_base.netloc and full not in visited:
                            next_level.add(full)
            except Exception:
                pass
        to_visit = next_level

    return found[:100]


# ── Headers ───────────────────────────────────────────────────────────────────

def check_headers(url: str, timeout: int = TIMEOUT) -> list:
    findings = []
    resp = safe_get(url, timeout)
    if not resp:
        return findings

    h = resp.headers
    missing_headers = [
        ("X-Frame-Options", "Clickjacking", "Alto", "Añadir: X-Frame-Options: DENY", "CWE-1021"),
        ("Content-Security-Policy", "Falta CSP", "Medio", "Implementar Content-Security-Policy", "CWE-693"),
        ("Strict-Transport-Security", "Falta HSTS", "Alto", "Añadir: Strict-Transport-Security: max-age=31536000; includeSubDomains", "CWE-523"),
        ("X-Content-Type-Options", "Falta X-Content-Type-Options", "Medio", "Añadir: X-Content-Type-Options: nosniff", "CWE-16"),
        ("Referrer-Policy", "Falta Referrer-Policy", "Bajo", "Añadir: Referrer-Policy: strict-origin-when-cross-origin", "CWE-116"),
        ("Permissions-Policy", "Falta Permissions-Policy", "Bajo", "Implementar Permissions-Policy", "CWE-16"),
    ]

    for header, name, sev, sol, cwe in missing_headers:
        if header not in h:
            findings.append(vuln(
                "Missing Security Header", sev,
                f"Header faltante: {header}",
                f"El servidor no envía el header de seguridad {header}.",
                url, evidence=f"Header '{header}' ausente en respuesta HTTP",
                risk=f"Sin {header} los atacantes pueden explotar el navegador del usuario.",
                solution=sol, cwe=cwe
            ))

    # Cookies inseguras
    for cookie in resp.cookies:
        issues = []
        if not cookie.secure:
            issues.append("Falta flag Secure")
        if not cookie.has_nonstandard_attr("HttpOnly"):
            issues.append("Falta flag HttpOnly")
        if not cookie.has_nonstandard_attr("SameSite"):
            issues.append("Falta atributo SameSite")
        if issues:
            findings.append(vuln(
                "Insecure Cookie", "medium",
                f"Cookie insegura: {cookie.name}",
                f"La cookie '{cookie.name}' tiene configuración insegura: {', '.join(issues)}",
                url,
                evidence=f"Set-Cookie: {cookie.name}={cookie.value[:20]}...",
                risk="Las cookies inseguras pueden ser robadas mediante XSS o sniffing.",
                solution="Añadir flags Secure; HttpOnly; SameSite=Strict a todas las cookies de sesión.",
                cwe="CWE-614"
            ))

    # Server version disclosure
    if "server" in h and re.search(r"\d+\.\d+", h["server"]):
        findings.append(vuln(
            "Information Disclosure", "low",
            "Versión del servidor expuesta",
            f"El header Server revela versión: {h['server']}",
            url, evidence=f"Server: {h['server']}",
            risk="Los atacantes pueden buscar CVEs específicos para esta versión.",
            solution="Ocultar versión en configuración de Nginx/Apache.",
            cwe="CWE-200"
        ))

    if "x-powered-by" in h:
        findings.append(vuln(
            "Information Disclosure", "low",
            "Header X-Powered-By expuesto",
            f"El header X-Powered-By revela tecnología: {h['x-powered-by']}",
            url, evidence=f"X-Powered-By: {h['x-powered-by']}",
            risk="Revela el stack tecnológico facilitando ataques dirigidos.",
            solution="Remover X-Powered-By del servidor.",
            cwe="CWE-200"
        ))

    # CORS
    cors = h.get("Access-Control-Allow-Origin", "")
    if cors == "*":
        findings.append(vuln(
            "CORS Misconfiguration", "high",
            "CORS permisivo: Access-Control-Allow-Origin: *",
            "El servidor permite peticiones desde cualquier origen.",
            url, evidence="Access-Control-Allow-Origin: *",
            risk="Permite que sitios maliciosos realicen peticiones autenticadas.",
            solution="Restringir CORS a orígenes específicos y confiables.",
            cwe="CWE-942"
        ))

    return findings


# ── SSL/TLS ───────────────────────────────────────────────────────────────────

def check_ssl(url: str, timeout: int = TIMEOUT) -> list:
    findings = []
    parsed = urlparse(url)
    if parsed.scheme != "https":
        findings.append(vuln(
            "No HTTPS", "high",
            "Sitio no usa HTTPS",
            "El sitio no utiliza cifrado TLS/HTTPS.",
            url, risk="Datos transmitidos en texto plano; susceptible a MITM.",
            solution="Configurar SSL/TLS con certbot y redirigir HTTP a HTTPS.",
            cwe="CWE-319"
        ))
        return findings

    host = parsed.hostname
    port = parsed.port or 443
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.settimeout(timeout)
            s.connect((host, port))
            cert = s.getpeercert()
            cipher = s.cipher()

        # Verificar expiración
        exp_str = cert.get("notAfter", "")
        if exp_str:
            exp_date = datetime.datetime.strptime(exp_str, "%b %d %H:%M:%S %Y %Z")
            days_left = (exp_date - datetime.datetime.utcnow()).days
            if days_left < 30:
                findings.append(vuln(
                    "SSL Certificate Expiring", "high",
                    f"Certificado SSL vence en {days_left} días",
                    "El certificado SSL está próximo a expirar.",
                    url, evidence=f"NotAfter: {exp_str}",
                    risk="Un certificado vencido causa errores de seguridad en navegadores.",
                    solution="Renovar certificado con: certbot renew",
                    cwe="CWE-298"
                ))

        # Cipher débil
        if cipher and cipher[1] in ("TLSv1", "TLSv1.1", "SSLv3", "SSLv2"):
            findings.append(vuln(
                "Weak TLS Version", "high",
                f"Versión TLS insegura: {cipher[1]}",
                f"El servidor acepta {cipher[1]}, protocolo considerado inseguro.",
                url, evidence=f"Cipher: {cipher}",
                risk="Vulnerable a ataques POODLE, BEAST, SWEET32.",
                solution="Deshabilitar TLS 1.0/1.1. Solo permitir TLS 1.2 y 1.3 en Nginx.",
                cwe="CWE-326"
            ))

    except ssl.SSLCertVerificationError as e:
        findings.append(vuln(
            "Invalid SSL Certificate", "high",
            "Certificado SSL inválido",
            str(e), url,
            risk="Los usuarios recibirán advertencias de seguridad.",
            solution="Obtener certificado válido con Let's Encrypt: certbot --nginx",
            cwe="CWE-295"
        ))
    except Exception:
        pass

    return findings


# ── SQL Injection ─────────────────────────────────────────────────────────────

def check_sqli(url: str, timeout: int = TIMEOUT) -> list:
    findings = []
    sql_errors = [
        "you have an error in your sql syntax",
        "warning: mysql", "unclosed quotation mark",
        "quoted string not properly terminated",
        "pg_query()", "sqlite3.operationalerror",
        "ora-01756", "microsoft odbc", "syntax error",
        "mysql_fetch", "mysql_num_rows", "division by zero",
    ]

    payloads = ["'", "' OR '1'='1", "' OR 1=1--", "\" OR \"1\"=\"1", "1; DROP TABLE users--"]
    for payload in payloads[:2]:  # Limitar a 2 para no sobrecargar
        test_url = inject_param(url, payload)
        resp = safe_get(test_url, timeout)
        if not resp:
            continue
        lower = resp.text.lower()
        for err in sql_errors:
            if err in lower:
                findings.append(vuln(
                    "SQL Injection", "critical",
                    "SQL Injection detectado",
                    "Se detectó un error SQL en la respuesta al inyectar payload malicioso.",
                    test_url, payload=payload,
                    evidence=f"Error SQL encontrado: '{err}' en respuesta",
                    risk="Un atacante puede leer, modificar o eliminar datos de la base de datos.",
                    solution="Usar Prepared Statements / consultas parametrizadas. Nunca concatenar SQL.",
                    cwe="CWE-89"
                ))
                return findings

    # Boolean-based blind
    true_resp = safe_get(inject_param(url, "1 AND 1=1"), timeout)
    false_resp = safe_get(inject_param(url, "1 AND 1=2"), timeout)
    if true_resp and false_resp:
        if len(true_resp.text) != len(false_resp.text) and abs(len(true_resp.text) - len(false_resp.text)) > 50:
            findings.append(vuln(
                "SQL Injection (Blind)", "critical",
                "Posible SQL Injection ciego (Boolean-based)",
                "Diferencia en respuestas sugiere inyección SQL ciega.",
                url, payload="1 AND 1=1 / 1 AND 1=2",
                evidence=f"Longitud TRUE={len(true_resp.text)}, FALSE={len(false_resp.text)}",
                risk="Extracción de datos mediante inferencia.",
                solution="Implementar consultas parametrizadas.",
                cwe="CWE-89"
            ))

    return findings


# ── XSS ───────────────────────────────────────────────────────────────────────

def check_xss(url: str, timeout: int = TIMEOUT) -> list:
    findings = []
    payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "'\"><script>alert(1)</script>",
        "<svg onload=alert(1)>",
    ]

    for payload in payloads[:2]:
        test_url = inject_param(url, payload)
        resp = safe_get(test_url, timeout)
        if resp and payload in resp.text:
            findings.append(vuln(
                "XSS", "high",
                "Cross-Site Scripting (XSS) Reflejado",
                "El payload XSS es reflejado sin sanitización en la respuesta.",
                test_url, payload=payload,
                evidence=f"Payload encontrado en respuesta: {payload[:100]}",
                risk="Un atacante puede ejecutar JavaScript malicioso en el navegador de víctimas.",
                solution="Sanitizar salidas con escape HTML. Implementar CSP. Usar DOMPurify.",
                cwe="CWE-79"
            ))
            break

    return findings


# ── CSRF ──────────────────────────────────────────────────────────────────────

def check_csrf(url: str, timeout: int = TIMEOUT) -> list:
    findings = []
    resp = safe_get(url, timeout)
    if not resp:
        return findings

    soup = BeautifulSoup(resp.text, "html.parser")
    forms = soup.find_all("form")

    for form in forms:
        method = (form.get("method") or "get").lower()
        if method != "post":
            continue
        inputs = {inp.get("name", "").lower() for inp in form.find_all("input")}
        csrf_names = {"csrf", "token", "_token", "authenticity_token", "_csrf", "csrftoken"}
        if not inputs.intersection(csrf_names):
            action = form.get("action", url)
            findings.append(vuln(
                "CSRF", "high",
                "Formulario POST sin token CSRF",
                "Se encontró un formulario POST sin campo de token CSRF.",
                urljoin(url, action), payload="N/A",
                evidence=f"Formulario action='{action}' sin token CSRF",
                risk="Un atacante puede engañar al usuario para enviar peticiones no autorizadas.",
                solution="Implementar CSRF tokens en todos los formularios POST. Usar SameSite=Strict en cookies.",
                cwe="CWE-352"
            ))

    return findings


# ── Open Redirect ─────────────────────────────────────────────────────────────

def check_open_redirect(url: str, timeout: int = TIMEOUT) -> list:
    findings = []
    evil = "https://evil-domain-test.com"
    params = ["redirect", "next", "url", "goto", "return", "returnUrl", "redirectUrl", "dest"]

    for param in params[:4]:
        test_url = f"{url}{'&' if '?' in url else '?'}{param}={evil}"
        resp = safe_get(test_url, timeout, allow_redirects=False)
        if not resp:
            continue
        if resp.status_code in (301, 302, 303, 307, 308):
            loc = resp.headers.get("Location", "")
            if evil in loc:
                findings.append(vuln(
                    "Open Redirect", "medium",
                    "Open Redirect detectado",
                    f"El parámetro '{param}' permite redirección a dominios externos.",
                    test_url, payload=f"{param}={evil}",
                    evidence=f"Location: {loc}",
                    risk="Phishing y robo de credenciales mediante redirecciones maliciosas.",
                    solution="Validar URLs de redirección contra whitelist. No confiar en parámetros de redirección.",
                    cwe="CWE-601"
                ))
                break

    return findings


# ── LFI / Path Traversal ──────────────────────────────────────────────────────

def check_lfi(url: str, timeout: int = TIMEOUT) -> list:
    findings = []
    payloads = [
        "../../../../etc/passwd",
        "..%2F..%2F..%2Fetc%2Fpasswd",
        "....//....//....//etc/passwd",
        "/etc/passwd",
    ]
    indicators = ["root:x:0:0", "root:!:", "daemon:", "/bin/bash"]

    for payload in payloads[:2]:
        test_url = inject_param(url, payload)
        resp = safe_get(test_url, timeout)
        if not resp:
            continue
        if any(ind in resp.text for ind in indicators):
            findings.append(vuln(
                "LFI", "critical",
                "Local File Inclusion (LFI) detectado",
                "El servidor devuelve contenido de /etc/passwd mediante path traversal.",
                test_url, payload=payload,
                evidence="Contenido de /etc/passwd encontrado en respuesta",
                risk="Un atacante puede leer archivos sensibles del servidor.",
                solution="Validar y sanitizar parámetros de ruta. Usar rutas absolutas. Implementar chroot.",
                cwe="CWE-22"
            ))
            break

    return findings


# ── Command Injection ─────────────────────────────────────────────────────────

def check_command_injection(url: str, timeout: int = TIMEOUT) -> list:
    findings = []
    payloads = [
        "; id",
        "| id",
        "` id`",
        "; cat /etc/passwd",
        "& whoami",
    ]
    indicators = ["uid=", "gid=", "root:", "www-data", "apache"]

    for payload in payloads[:2]:
        test_url = inject_param(url, payload)
        resp = safe_get(test_url, timeout)
        if not resp:
            continue
        if any(ind in resp.text for ind in indicators):
            findings.append(vuln(
                "Command Injection", "critical",
                "Command Injection detectado",
                "El servidor ejecuta comandos del sistema operativo desde parámetros de usuario.",
                test_url, payload=payload,
                evidence=resp.text[:200],
                risk="Un atacante puede ejecutar comandos arbitrarios en el servidor.",
                solution="Nunca pasar input de usuario a funciones del sistema. Usar APIs seguras en lugar de shell.",
                cwe="CWE-78"
            ))
            break

    return findings


# ── SSRF ──────────────────────────────────────────────────────────────────────

def check_ssrf(url: str, timeout: int = TIMEOUT) -> list:
    findings = []
    ssrf_params = ["url", "src", "href", "path", "dest", "image", "file", "host", "proxy"]
    internal_urls = ["http://169.254.169.254/latest/meta-data/", "http://localhost/", "http://127.0.0.1/"]

    for param in ssrf_params[:3]:
        for internal in internal_urls[:1]:
            test_url = f"{url}{'&' if '?' in url else '?'}{param}={internal}"
            resp = safe_get(test_url, timeout)
            if not resp:
                continue
            if any(x in resp.text for x in ["ami-id", "instance-id", "localhost", "127.0.0.1"]):
                findings.append(vuln(
                    "SSRF", "critical",
                    "Server-Side Request Forgery (SSRF) detectado",
                    f"El parámetro '{param}' permite realizar peticiones internas del servidor.",
                    test_url, payload=f"{param}={internal}",
                    evidence=resp.text[:200],
                    risk="Acceso a servicios internos, metadata de cloud, escalada de privilegios.",
                    solution="Validar y restringir URLs de destino. Implementar allowlist de hosts.",
                    cwe="CWE-918"
                ))

    return findings


# ── Información sensible ──────────────────────────────────────────────────────

def check_sensitive_files(url: str, timeout: int = TIMEOUT) -> list:
    findings = []
    sensitive_paths = [
        ("/.git/HEAD", "git", "Repositorio Git expuesto"),
        ("/.env", "APP_KEY", "Archivo .env expuesto"),
        ("/phpinfo.php", "PHP Version", "PHPInfo expuesto"),
        ("/.htaccess", "RewriteEngine", ".htaccess expuesto"),
        ("/wp-config.php.bak", "DB_PASSWORD", "Backup wp-config expuesto"),
        ("/config.php", "password", "config.php expuesto"),
        ("/backup.zip", "PK", "Backup ZIP accesible"),
        ("/robots.txt", None, "robots.txt (enumeración)"),
        ("/sitemap.xml", None, "sitemap.xml (enumeración)"),
        ("/.DS_Store", None, ".DS_Store expuesto"),
        ("/server-status", "Apache Server Status", "Apache server-status expuesto"),
        ("/nginx_status", "Active connections", "Nginx status expuesto"),
    ]

    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    for path, indicator, name in sensitive_paths:
        test_url = base + path
        resp = safe_get(test_url, timeout)
        if not resp or resp.status_code not in (200, 403):
            continue
        if indicator and indicator.lower() not in resp.text.lower():
            continue
        sev = "critical" if path in ("/.env", "/.git/HEAD") else "medium" if resp.status_code == 200 else "low"
        findings.append(vuln(
            "Sensitive File Exposure", sev,
            name,
            f"Archivo sensible accesible: {test_url}",
            test_url, evidence=f"HTTP {resp.status_code} — {resp.text[:100]}",
            risk="Exposición de credenciales, código fuente o configuraciones.",
            solution=f"Restringir acceso a {path} mediante Nginx/Apache. Eliminar archivos sensibles del webroot.",
            cwe="CWE-200"
        ))

    return findings


# ── HTTP Methods ──────────────────────────────────────────────────────────────

def check_http_methods(url: str, timeout: int = TIMEOUT) -> list:
    findings = []
    try:
        resp = requests.options(url, timeout=timeout, headers=HEADERS_UA, verify=False)
        allow = resp.headers.get("Allow", "") + resp.headers.get("Access-Control-Allow-Methods", "")
        dangerous = [m for m in ["PUT", "DELETE", "TRACE", "CONNECT", "PATCH"] if m in allow]
        if dangerous:
            findings.append(vuln(
                "Dangerous HTTP Methods", "medium",
                f"Métodos HTTP peligrosos habilitados: {', '.join(dangerous)}",
                "El servidor permite métodos HTTP que podrían ser explotados.",
                url, evidence=f"Allow: {allow}",
                risk="Permite modificar/eliminar recursos o ataques cross-site tracing.",
                solution="Deshabilitar métodos no necesarios en la configuración del servidor.",
                cwe="CWE-16"
            ))
    except Exception:
        pass
    return findings


# ── Error disclosure ──────────────────────────────────────────────────────────

def check_error_disclosure(url: str, timeout: int = TIMEOUT) -> list:
    findings = []
    test_urls = [
        url + "/nonexistent-page-12345",
        inject_param(url, "' AND 1=CONVERT(int, 'error')--"),
    ]
    patterns = ["stack trace", "exception in", "traceback", "at line", "syntax error",
                "undefined variable", "mysql_fetch", "pg_query", "warning:", "fatal error"]

    for test_url in test_urls:
        resp = safe_get(test_url, timeout)
        if not resp:
            continue
        lower = resp.text.lower()
        for pat in patterns:
            if pat in lower:
                findings.append(vuln(
                    "Error Information Disclosure", "medium",
                    "Mensajes de error detallados expuestos",
                    f"El servidor expone información interna en mensajes de error.",
                    test_url, evidence=resp.text[:300],
                    risk="Revela tecnologías, rutas y lógica interna al atacante.",
                    solution="Configurar manejo genérico de errores. Deshabilitar debug en producción.",
                    cwe="CWE-209"
                ))
                break

    return findings


# ── Motor principal ───────────────────────────────────────────────────────────

def run_full_scan(
    url: str,
    modules: list,
    depth: int = 2,
    timeout: int = TIMEOUT,
    progress_callback=None
) -> dict:
    import requests as req
    req.packages.urllib3.disable_warnings()

    start = time.time()
    all_vulns = []
    crawled = []
    technologies = {}

    def log(msg):
        if progress_callback:
            progress_callback(msg)

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    log(f"Iniciando escaneo de {url}")

    # Tecnologías
    log("Detectando tecnologías...")
    technologies = detect_technologies(url, timeout)

    # Crawling
    if "Crawling" in modules:
        log("Crawling de URLs...")
        crawled = crawl_urls(url, depth, timeout)

    # Módulos de escaneo
    module_map = {
        "Headers": (check_headers, "Analizando headers HTTP..."),
        "SSL": (check_ssl, "Verificando SSL/TLS..."),
        "XSS": (check_xss, "Probando XSS..."),
        "SQLi": (check_sqli, "Probando SQL Injection..."),
        "CSRF": (check_csrf, "Verificando CSRF..."),
        "OpenRedirect": (check_open_redirect, "Probando Open Redirect..."),
        "LFI": (check_lfi, "Probando LFI/Path Traversal..."),
        "CommandInjection": (check_command_injection, "Probando Command Injection..."),
        "SSRF": (check_ssrf, "Probando SSRF..."),
        "SensitiveFiles": (check_sensitive_files, "Buscando archivos sensibles..."),
        "HttpMethods": (check_http_methods, "Verificando métodos HTTP..."),
        "ErrorDisclosure": (check_error_disclosure, "Verificando divulgación de errores..."),
    }

    for mod_name, (fn, msg) in module_map.items():
        if mod_name in modules or "All" in modules:
            log(msg)
            try:
                results = fn(url, timeout)
                all_vulns.extend(results)
            except Exception as e:
                log(f"Error en módulo {mod_name}: {e}")

    # Contar por severidad
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for v in all_vulns:
        sev = v.get("severity", "info").lower()
        counts[sev] = counts.get(sev, 0) + 1

    duration = round(time.time() - start, 2)

    return {
        "vulnerabilities": all_vulns,
        "technologies": technologies,
        "crawled_urls": crawled,
        "counts": counts,
        "total": len(all_vulns),
        "duration": duration,
        "url": url,
    }
