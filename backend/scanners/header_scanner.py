"""
Header Scanner - FIXED:
  - Now always scans base_url directly (not just discovered URLs)
  - Handles sites that return no cookies gracefully
  - Better de-duplication
"""

import logging

logger = logging.getLogger(__name__)

SECURITY_HEADERS = {
    'Strict-Transport-Security': {
        'description': 'HSTS fuerza conexiones HTTPS, previniendo ataques de downgrade.',
        'recommendation': 'Agregar: Strict-Transport-Security: max-age=31536000; includeSubDomains',
        'severity': 'high',
        'reference': 'https://owasp.org/www-project-secure-headers/#strict-transport-security',
    },
    'Content-Security-Policy': {
        'description': 'CSP controla qué recursos pueden cargarse, mitigando ataques XSS.',
        'recommendation': 'Agregar una cabecera Content-Security-Policy restrictiva.',
        'severity': 'high',
        'reference': 'https://owasp.org/www-project-secure-headers/#content-security-policy',
    },
    'X-Content-Type-Options': {
        'description': 'Previene ataques de MIME-type sniffing.',
        'recommendation': 'Agregar: X-Content-Type-Options: nosniff',
        'severity': 'medium',
        'reference': 'https://owasp.org/www-project-secure-headers/#x-content-type-options',
    },
    'X-Frame-Options': {
        'description': 'Previene clickjacking controlando el encuadre de la página.',
        'recommendation': 'Agregar: X-Frame-Options: DENY o SAMEORIGIN',
        'severity': 'medium',
        'reference': 'https://owasp.org/www-project-secure-headers/#x-frame-options',
    },
    'Referrer-Policy': {
        'description': 'Controla cuánta información del referrer se comparte.',
        'recommendation': 'Agregar: Referrer-Policy: strict-origin-when-cross-origin',
        'severity': 'low',
        'reference': 'https://owasp.org/www-project-secure-headers/#referrer-policy',
    },
    'Permissions-Policy': {
        'description': 'Controla las funcionalidades del navegador disponibles para la página.',
        'recommendation': 'Agregar: Permissions-Policy: geolocation=(), microphone=(), camera=()',
        'severity': 'low',
        'reference': 'https://owasp.org/www-project-secure-headers/#permissions-policy',
    },
}

DANGEROUS_HEADERS = {
    'Server': {
        'description': 'La cabecera Server expone la versión del software, ayudando al atacante.',
        'recommendation': 'Eliminar o anonimizar la cabecera Server.',
        'severity': 'low',
    },
    'X-Powered-By': {
        'description': 'X-Powered-By revela el stack tecnológico del backend.',
        'recommendation': 'Eliminar la cabecera X-Powered-By.',
        'severity': 'low',
    },
}


class HeaderScanner:
    def __init__(self, http_client):
        self.http = http_client

    def scan(self, base_url, urls, **_) -> list:
        findings = []
        seen = set()

        # Always scan the base URL first, then up to 2 more
        targets = [base_url] + [u for u in urls if u != base_url]
        targets = list(dict.fromkeys(targets))[:3]

        for url in targets:
            try:
                resp = self.http.get(url)
                if resp is None:
                    continue
                headers = {k.lower(): v for k, v in resp.headers.items()}

                # Missing security headers
                for header, meta in SECURITY_HEADERS.items():
                    if header.lower() not in headers:
                        key = f"missing:{header}"
                        if key not in seen:
                            seen.add(key)
                            findings.append({
                                'type': 'misconfiguration',
                                'subtype': 'missing_header',
                                'url': base_url,   # report against base URL
                                'header': header,
                                'description': meta['description'],
                                'recommendation': meta['recommendation'],
                                'reference': meta['reference'],
                                'severity_hint': meta['severity'],
                                'evidence': f"Cabecera '{header}' ausente en la respuesta HTTP.",
                            })

                # Dangerous headers
                for header, meta in DANGEROUS_HEADERS.items():
                    val = resp.headers.get(header)
                    if val:
                        key = f"disclosure:{header}"
                        if key not in seen:
                            seen.add(key)
                            findings.append({
                                'type': 'misconfiguration',
                                'subtype': 'information_disclosure',
                                'url': base_url,
                                'header': header,
                                'description': meta['description'],
                                'recommendation': meta['recommendation'],
                                'severity_hint': meta['severity'],
                                'evidence': f"{header}: {val}",
                            })

                # Cookie security (only on base URL to avoid duplicates)
                if url == base_url:
                    for cookie in resp.cookies:
                        cookie_issues = []
                        attrs = (cookie._rest or {})
                        if 'HttpOnly' not in attrs:
                            cookie_issues.append('HttpOnly flag ausente')
                        if not cookie.secure:
                            cookie_issues.append('Secure flag ausente')
                        if 'SameSite' not in attrs:
                            cookie_issues.append('Atributo SameSite ausente')

                        if cookie_issues:
                            findings.append({
                                'type': 'misconfiguration',
                                'subtype': 'insecure_cookie',
                                'url': base_url,
                                'cookie_name': cookie.name,
                                'description': f"La cookie '{cookie.name}' tiene problemas de seguridad.",
                                'recommendation': 'Configurar HttpOnly, Secure y SameSite=Strict en todas las cookies.',
                                'severity_hint': 'medium',
                                'evidence': '; '.join(cookie_issues),
                            })

            except Exception as e:
                logger.warning(f"Header scan error for {url}: {e}")

        return findings
