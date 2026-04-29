"""
Rule Engine - Classifies, scores and enriches vulnerability findings.
Maps raw scanner output to structured, OWASP-aligned vulnerability reports.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

VULNERABILITY_RULES = {
    'xss': {
        'name': 'Cross-Site Scripting (XSS)',
        'owasp': 'A03:2021 – Injection',
        'cwe': 'CWE-79',
        'severity': 'high',
        'cvss_range': '6.1 – 8.8',
        'description': (
            'XSS allows attackers to inject malicious scripts into web pages viewed by other users. '
            'This can lead to session hijacking, credential theft, or malware distribution.'
        ),
        'remediation': [
            'Encode all user-supplied output using context-aware encoding (HTML, JS, CSS, URL).',
            'Implement a strict Content-Security-Policy (CSP) header.',
            'Use modern frameworks that automatically escape output (React, Angular, Vue).',
            'Validate and sanitize all inputs on the server side.',
        ],
        'references': [
            'https://owasp.org/www-community/attacks/xss/',
            'https://cwe.mitre.org/data/definitions/79.html',
        ],
    },
    'sqli': {
        'name': 'SQL Injection',
        'owasp': 'A03:2021 – Injection',
        'cwe': 'CWE-89',
        'severity': 'critical',
        'cvss_range': '8.1 – 10.0',
        'description': (
            'SQL Injection allows attackers to interfere with database queries, '
            'potentially extracting, modifying or deleting data, bypassing authentication, '
            'or executing operating system commands.'
        ),
        'remediation': [
            'Use parameterized queries / prepared statements exclusively.',
            'Apply ORM frameworks that handle query parameterization.',
            'Implement input validation using allowlists.',
            'Apply principle of least privilege to database accounts.',
            'Deploy a Web Application Firewall (WAF).',
        ],
        'references': [
            'https://owasp.org/www-community/attacks/SQL_Injection',
            'https://cwe.mitre.org/data/definitions/89.html',
        ],
    },
    'misconfiguration': {
        'name': 'Security Misconfiguration',
        'owasp': 'A05:2021 – Security Misconfiguration',
        'cwe': 'CWE-16',
        'severity': 'medium',
        'cvss_range': '4.0 – 7.5',
        'description': (
            'Security misconfigurations include missing security headers, verbose error messages, '
            'default credentials, and unnecessary features enabled. They can be exploited to '
            'facilitate other attacks.'
        ),
        'remediation': [
            'Implement all recommended security headers.',
            'Remove or restrict information-disclosure headers.',
            'Apply security-focused cookie attributes (HttpOnly, Secure, SameSite).',
            'Regularly audit and harden server configurations.',
        ],
        'references': [
            'https://owasp.org/Top10/A05_2021-Security_Misconfiguration/',
            'https://owasp.org/www-project-secure-headers/',
        ],
    },
    'csrf': {
        'name': 'Cross-Site Request Forgery (CSRF)',
        'owasp': 'A01:2021 – Broken Access Control',
        'cwe': 'CWE-352',
        'severity': 'medium',
        'cvss_range': '4.3 – 6.8',
        'description': (
            'CSRF tricks authenticated users into submitting malicious requests. '
            'Without CSRF protection, attackers can perform actions on behalf of victims.'
        ),
        'remediation': [
            'Implement synchronizer CSRF tokens in all state-changing forms.',
            "Use the SameSite=Strict cookie attribute.",
            'Verify the Origin and Referer headers on the server.',
            'Consider double-submit cookie pattern as an alternative.',
        ],
        'references': [
            'https://owasp.org/www-community/attacks/csrf',
            'https://cwe.mitre.org/data/definitions/352.html',
        ],
    },
}

VULNERABILITY_RULES['redirect'] = {
    'name': 'Open Redirect',
    'owasp': 'A01:2021 – Broken Access Control',
    'cwe': 'CWE-601',
    'severity': 'medium',
    'cvss_range': '4.3 – 6.1',
    'description': (
        'Un Open Redirect permite a un atacante redirigir a usuarios hacia sitios '
        'maliciosos externos, facilitando phishing y robo de credenciales.'
    ),
    'remediation': [
        'Validar que las URLs de redirección pertenezcan al dominio autorizado.',
        'Usar un mapa de redirecciones indirectas en lugar de URLs dinámicas.',
        'Rechazar cualquier URL con esquema externo (http://, https://) en parámetros de redirección.',
    ],
    'references': [
        'https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/11-Client-side_Testing/04-Testing_for_Client-side_URL_Redirect',
        'https://cwe.mitre.org/data/definitions/601.html',
    ],
}

VULNERABILITY_RULES['info_disclosure'] = {
    'name': 'Information Disclosure',
    'owasp': 'A05:2021 – Security Misconfiguration',
    'cwe': 'CWE-200',
    'severity': 'medium',
    'cvss_range': '4.0 – 7.5',
    'description': (
        'La exposición de información sensible (rutas, credenciales, stack traces, '
        'archivos de configuración) puede facilitar ataques dirigidos.'
    ),
    'remediation': [
        'Deshabilitar páginas de error detalladas en producción.',
        'Restringir acceso a archivos de configuración (.env, .git, config.*).',
        'Eliminar comentarios con información sensible del HTML.',
        'Configurar el servidor web para denegar acceso a rutas sensibles.',
    ],
    'references': [
        'https://owasp.org/Top10/A05_2021-Security_Misconfiguration/',
        'https://cwe.mitre.org/data/definitions/200.html',
    ],
}

SEVERITY_OVERRIDE = {
    # Fine-tune severity for specific subtypes
    ('misconfiguration', 'missing_header'): None,  # use severity_hint
    ('misconfiguration', 'information_disclosure'): 'low',
    ('misconfiguration', 'insecure_cookie'): 'medium',
    ('sqli', 'time_based'): 'high',  # Less certain than error_based
}


class RuleEngine:
    """
    Applies classification rules to raw scanner findings.
    Returns None if a finding should be suppressed.
    """

    def evaluate(self, finding: dict) -> dict | None:
        vuln_type = finding.get('type')
        rule = VULNERABILITY_RULES.get(vuln_type)
        if not rule:
            logger.warning(f"No rule for type: {vuln_type}")
            return None

        subtype = finding.get('subtype', '')

        # Determine severity
        override = SEVERITY_OVERRIDE.get((vuln_type, subtype))
        if override is not None:
            severity = override
        elif 'severity_hint' in finding:
            severity = finding['severity_hint']
        else:
            severity = rule['severity']

        enriched = {
            'id': self._generate_id(finding),
            'type': vuln_type,
            'subtype': subtype,
            'name': rule['name'],
            'severity': severity,
            'owasp': rule['owasp'],
            'cwe': rule['cwe'],
            'cvss_range': rule['cvss_range'],
            'description': finding.get('description') or rule['description'],
            'remediation': rule['remediation'],
            'references': rule.get('references', []),
            'url': finding.get('url', ''),
            'parameter': finding.get('parameter'),
            'payload': finding.get('payload'),
            'evidence': finding.get('evidence', ''),
            'recommendation': finding.get('recommendation'),
            'header': finding.get('header'),
            'cookie_name': finding.get('cookie_name'),
            'request': finding.get('request'),
            'discovered_at': datetime.now(timezone.utc).isoformat(),
        }

        # Clean None values
        return {k: v for k, v in enriched.items() if v is not None}

    @staticmethod
    def _generate_id(finding: dict) -> str:
        import hashlib
        key = f"{finding.get('type')}{finding.get('url')}{finding.get('parameter')}{finding.get('payload', '')}"
        return hashlib.md5(key.encode()).hexdigest()[:12]
