"""
Information Disclosure Scanner - Detecta exposición de información sensible.
Analiza páginas de error, comentarios HTML, y rutas de archivos sensibles.
"""

import logging
import re
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

# Rutas sensibles comunes a probar
SENSITIVE_PATHS = [
    '/.env',
    '/.git/config',
    '/.git/HEAD',
    '/config.php',
    '/config.yml',
    '/config.yaml',
    '/wp-config.php',
    '/phpinfo.php',
    '/info.php',
    '/debug',
    '/actuator',
    '/actuator/env',
    '/actuator/health',
    '/__debug__/',
    '/console',
    '/admin/config',
    '/backup.zip',
    '/backup.sql',
    '/database.sql',
    '/robots.txt',
    '/sitemap.xml',
    '/.htaccess',
    '/web.config',
    '/crossdomain.xml',
]

# Patrones que indican información sensible en el cuerpo
SENSITIVE_PATTERNS = [
    (r'(?i)password\s*[=:]\s*["\']?[\w!@#$%^&*]+', 'Contraseña expuesta en respuesta'),
    (r'(?i)secret\s*[=:]\s*["\']?[\w!@#$%^&*]+', 'Secreto expuesto en respuesta'),
    (r'(?i)api[_-]?key\s*[=:]\s*["\']?[\w-]+', 'API Key expuesta en respuesta'),
    (r'(?i)aws[_-]?access[_-]?key', 'Credencial AWS expuesta'),
    (r'(?i)database\s+error', 'Error de base de datos expuesto'),
    (r'(?i)stack\s+trace', 'Stack trace expuesto en respuesta'),
    (r'(?i)exception\s+in\s+thread', 'Excepción Java expuesta'),
    (r'(?i)traceback\s+\(most\s+recent', 'Traceback Python expuesto'),
    (r'<!--.*?(todo|fixme|hack|bug|password|credential).*?-->', 'Comentario sensible en HTML'),
    (r'(?i)jdbc:[a-z]+://[\w\./:-]+', 'Cadena de conexión JDBC expuesta'),
    (r'/home/[\w]+/[\w/]+\.py', 'Ruta absoluta del servidor expuesta'),
    (r'/var/www/[\w/]+', 'Ruta del servidor web expuesta'),
]

# Códigos de estado que revelan información
INTERESTING_STATUS = {
    403: 'Recurso existe pero está protegido (403)',
    500: 'Error interno del servidor (500) - puede revelar información',
    401: 'Autenticación requerida - recurso sensible existe (401)',
}


class InfoDisclosureScanner:
    """
    Detecta divulgación de información sensible mediante:
    1. Prueba de rutas sensibles conocidas
    2. Análisis de patrones en respuestas (contraseñas, keys, trazas)
    3. Comentarios HTML con información sensible
    """

    def __init__(self, http_client):
        self.http = http_client

    def scan(self, base_url: str, urls: list, **_) -> list:
        findings = []

        # 1. Rutas sensibles
        findings.extend(self._test_sensitive_paths(base_url))

        # 2. Patrones en páginas existentes
        targets = list(set([base_url] + urls))[:8]
        for url in targets:
            findings.extend(self._analyze_response_body(url))

        return findings

    def _test_sensitive_paths(self, base_url: str) -> list:
        findings = []
        for path in SENSITIVE_PATHS:
            url = urljoin(base_url, path)
            try:
                resp = self.http.get(url)
                if resp is None:
                    continue

                if resp.status_code == 200 and len(resp.text) > 20:
                    # Verificar que no sea solo la página de inicio redirigida
                    if self._looks_like_real_content(path, resp.text):
                        findings.append({
                            'type': 'info_disclosure',
                            'subtype': 'sensitive_file',
                            'url': url,
                            'description': f'Archivo sensible accesible: {path}',
                            'evidence': f'HTTP 200 · {len(resp.text)} bytes · {path}',
                            'severity_hint': 'high' if path in ('/.env', '/.git/config', '/wp-config.php') else 'medium',
                        })

                elif resp.status_code in INTERESTING_STATUS:
                    findings.append({
                        'type': 'info_disclosure',
                        'subtype': 'interesting_status',
                        'url': url,
                        'description': INTERESTING_STATUS[resp.status_code],
                        'evidence': f'HTTP {resp.status_code} en {path}',
                        'severity_hint': 'low',
                    })

            except Exception as e:
                logger.debug(f"Path probe error {url}: {e}")

        return findings

    def _analyze_response_body(self, url: str) -> list:
        findings = []
        try:
            resp = self.http.get(url)
            if resp is None or 'text' not in resp.headers.get('Content-Type', ''):
                return []

            body = resp.text
            for pattern, description in SENSITIVE_PATTERNS:
                match = re.search(pattern, body, re.DOTALL)
                if match:
                    start = max(0, match.start() - 20)
                    end = min(len(body), match.end() + 40)
                    evidence = '...' + body[start:end].strip() + '...'
                    findings.append({
                        'type': 'info_disclosure',
                        'subtype': 'sensitive_data_in_response',
                        'url': url,
                        'description': description,
                        'evidence': evidence[:200],
                        'severity_hint': 'medium',
                    })

        except Exception as e:
            logger.debug(f"Body analysis error {url}: {e}")

        return findings

    @staticmethod
    def _looks_like_real_content(path: str, body: str) -> bool:
        """Heuristic: verify content matches the expected file type."""
        body_lower = body.lower()
        if '.env' in path:
            return any(k in body_lower for k in ('db_', 'app_key', 'secret', '='))
        if '.git' in path:
            return any(k in body_lower for k in ('[core]', 'ref:', 'repositoryformatversion'))
        if '.sql' in path or 'database' in path:
            return any(k in body_lower for k in ('insert into', 'create table', 'drop table'))
        if 'phpinfo' in path or 'info.php' in path:
            return 'phpinfo' in body_lower or 'php version' in body_lower
        if 'actuator' in path:
            return '{' in body  # JSON response
        return len(body) > 100
