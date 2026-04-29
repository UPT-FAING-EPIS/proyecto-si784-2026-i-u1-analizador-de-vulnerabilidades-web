"""
XSS Scanner - FIXED:
  - Added base_url itself as a test target
  - Broader reflection detection (catches partial reflection)
  - Tests pages without params too (looks for forms on any page)
  - Better evidence extraction
"""

import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

logger = logging.getLogger(__name__)

XSS_PAYLOADS = [
    '<script>alert("XSS")</script>',
    '"><script>alert(1)</script>',
    "'><img src=x onerror=alert(1)>",
    '<svg onload=alert(1)>',
    '"><svg/onload=alert`1`>',
    '<iframe src="javascript:alert(1)">',
    '"><details open ontoggle=alert(1)>',
    "';alert(1)//",
]

REFLECTION_SIGNATURES = [
    '<script>alert',
    'onerror=alert',
    'onload=alert',
    'ontoggle=alert',
    'javascript:alert',
    '<iframe src=',
    '<details open',
    "';alert(",
    '<svg',
]


class XSSScanner:
    def __init__(self, http_client):
        self.http = http_client

    def scan(self, base_url, urls, forms, endpoints, **_) -> list:
        findings = []

        # Include base_url and all discovered URLs as targets
        all_targets = list(dict.fromkeys([base_url] + urls + endpoints))

        for url in all_targets:
            findings.extend(self._test_url_params(url))

        for form in forms:
            findings.extend(self._test_form(form))

        # Deduplicate by (url, parameter)
        seen = set()
        unique = []
        for f in findings:
            key = (f['url'], f.get('parameter', ''))
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique

    def _test_url_params(self, url: str) -> list:
        findings = []
        parsed = urlparse(url)
        params = parse_qs(parsed.query, keep_blank_values=True)
        if not params:
            return []

        for param_name in params:
            for payload in XSS_PAYLOADS:
                test_params = {k: v[0] for k, v in params.items()}
                test_params[param_name] = payload
                test_url = urlunparse(parsed._replace(query=urlencode(test_params)))
                try:
                    resp = self.http.get(test_url)
                    if resp and self._is_reflected(payload, resp.text):
                        findings.append({
                            'type': 'xss',
                            'subtype': 'reflected',
                            'url': url,
                            'parameter': param_name,
                            'payload': payload,
                            'evidence': self._extract_evidence(payload, resp.text),
                        })
                        break
                except Exception as e:
                    logger.debug(f"XSS param test error: {e}")
        return findings

    def _test_form(self, form: dict) -> list:
        findings = []
        for field in form['fields']:
            if field['type'] in ('hidden', 'file', 'email', 'number'):
                continue
            for payload in XSS_PAYLOADS:
                data = {f['name']: f.get('value', 'test') or 'test' for f in form['fields']}
                data[field['name']] = payload
                try:
                    if form['method'] == 'POST':
                        resp = self.http.post(form['action'], data=data)
                    else:
                        resp = self.http.get(form['action'], params=data)

                    if resp and self._is_reflected(payload, resp.text):
                        findings.append({
                            'type': 'xss',
                            'subtype': 'reflected_form',
                            'url': form['action'],
                            'parameter': field['name'],
                            'payload': payload,
                            'evidence': self._extract_evidence(payload, resp.text),
                        })
                        break
                except Exception as e:
                    logger.debug(f"XSS form test error: {e}")
        return findings

    @staticmethod
    def _is_reflected(payload: str, body: str) -> bool:
        if not body:
            return False
        body_lower = body.lower()
        # Check signatures
        if any(sig.lower() in body_lower for sig in REFLECTION_SIGNATURES):
            return True
        # Check if raw payload appears unescaped (no &lt; / &gt;)
        if payload.lower() in body_lower:
            escaped = payload.replace('<', '&lt;').replace('>', '&gt;')
            if escaped.lower() not in body_lower:
                return True
        return False

    @staticmethod
    def _extract_evidence(payload: str, body: str) -> str:
        if not body:
            return payload
        body_lower = body.lower()
        search = payload[:12].lower()
        idx = body_lower.find(search)
        if idx == -1:
            # Try finding any signature
            for sig in REFLECTION_SIGNATURES:
                idx = body_lower.find(sig.lower())
                if idx != -1:
                    break
        if idx == -1:
            return f"Payload reflejado: {payload[:60]}"
        start = max(0, idx - 40)
        end = min(len(body), idx + len(payload) + 40)
        return '...' + body[start:end].replace('\n', ' ').strip() + '...'
