"""
Open Redirect Scanner - Detecta redirecciones no validadas.
Módulo de ejemplo para demostrar la extensibilidad de VulnScan.

Para activarlo, agregar en core/engine.py:
    from scanners.redirect_scanner import RedirectScanner
    scanners.append(('Open Redirect', RedirectScanner(self.http), 'redirect'))

Y en rules/engine.py agregar la regla 'redirect' en VULNERABILITY_RULES.
"""

import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

logger = logging.getLogger(__name__)

# Parámetros comunes que suelen contener URLs de redirección
REDIRECT_PARAMS = [
    'redirect', 'redirect_to', 'redirect_url', 'return', 'return_to',
    'returnUrl', 'next', 'url', 'goto', 'target', 'dest', 'destination',
    'redir', 'ref', 'referer', 'forward', 'location', 'continue',
]

# Payloads de destinos externos para probar
REDIRECT_PAYLOADS = [
    'https://evil.com',
    '//evil.com',
    'https://evil.com%2F@trusted.com',
    '/\\/evil.com',
    'https:evil.com',
    '\\\\evil.com',
    'https://trusted.com@evil.com',
]


class RedirectScanner:
    """
    Prueba parámetros URL comúnmente usados para redirección.
    Detecta Open Redirects verificando si la respuesta redirige
    a un dominio diferente al objetivo.
    """

    def __init__(self, http_client):
        self.http = http_client

    def scan(self, base_url: str, urls: list, endpoints: list, **_) -> list:
        findings = []
        base_domain = urlparse(base_url).netloc
        all_targets = list(set(urls + endpoints))

        for url in all_targets:
            parsed = urlparse(url)
            params = parse_qs(parsed.query, keep_blank_values=True)

            for param_name in params:
                if not any(rp in param_name.lower() for rp in REDIRECT_PARAMS):
                    continue

                for payload in REDIRECT_PAYLOADS:
                    test_params = {k: v[0] for k, v in params.items()}
                    test_params[param_name] = payload
                    test_url = urlunparse(parsed._replace(
                        query=urlencode(test_params)
                    ))

                    try:
                        # allow_redirects=False para capturar el redirect antes de seguirlo
                        resp = self.http.session.get(
                            test_url,
                            timeout=self.http.timeout,
                            verify=False,
                            allow_redirects=False,
                        )
                        if resp is None:
                            continue

                        location = resp.headers.get('Location', '')
                        if resp.status_code in (301, 302, 303, 307, 308) and location:
                            dest_domain = urlparse(location).netloc
                            if dest_domain and dest_domain != base_domain:
                                findings.append({
                                    'type': 'redirect',
                                    'subtype': 'open_redirect',
                                    'url': test_url,
                                    'parameter': param_name,
                                    'payload': payload,
                                    'evidence': f'HTTP {resp.status_code} → Location: {location}',
                                    'severity_hint': 'medium',
                                })
                                break  # un payload confirmado es suficiente

                    except Exception as e:
                        logger.debug(f"Redirect test error: {e}")

        return findings
