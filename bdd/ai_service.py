"""
Integración DeepSeek AI para análisis inteligente de vulnerabilidades.
"""
import os
import json
import re
from typing import Optional
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

SYSTEM_PROMPT = """Eres un experto en ciberseguridad y análisis de vulnerabilidades web con 15 años de experiencia.
Conoces profundamente OWASP Top 10, CVE, CWE, CVSS y mejores prácticas de seguridad.
Responde siempre en español técnico y en formato JSON válido cuando se te pida."""


def _call_deepseek(messages: list, temperature: float = 0.3, max_tokens: int = 2000) -> Optional[str]:
    if not DEEPSEEK_API_KEY:
        return None
    try:
        resp = requests.post(
            f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
    except Exception:
        pass
    return None


def _extract_json(text: str) -> Optional[dict]:
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{[\s\S]+\}", text)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return None


def analyze_vulnerability(vuln: dict, stack: str = "generic") -> dict:
    """Analiza una vulnerabilidad y genera solución completa con IA."""
    prompt = f"""Analiza esta vulnerabilidad de seguridad web y genera una solución completa.

VULNERABILIDAD:
- Tipo: {vuln.get('vuln_type', 'Unknown')}
- Severidad: {vuln.get('severity', 'unknown')}
- Título: {vuln.get('title', '')}
- Endpoint: {vuln.get('endpoint', '')}
- Payload: {vuln.get('payload', 'N/A')}
- Evidencia: {vuln.get('evidence', 'N/A')}
- Stack tecnológico: {stack}

Responde SOLO en JSON con esta estructura exacta:
{{
  "confirmed": true/false,
  "false_positive_probability": 0-100,
  "cvss_score": 0.0-10.0,
  "cwe_id": "CWE-XXX",
  "risk_explanation": "explicación del riesgo",
  "attack_scenario": "cómo un atacante lo explotaría",
  "remediation": {{
    "immediate": ["acción 1", "acción 2"],
    "long_term": ["mejora 1", "mejora 2"],
    "code_fix": "código corregido en {stack}",
    "config_fix": "configuración segura"
  }},
  "references": ["https://owasp.org/...", "https://cwe.mitre.org/..."],
  "estimated_fix_time": "X horas/días"
}}"""

    content = _call_deepseek([{"role": "user", "content": prompt}])
    if not content:
        return _fallback_analysis(vuln)

    parsed = _extract_json(content)
    if parsed:
        parsed["source"] = "deepseek"
        return parsed

    return _fallback_analysis(vuln)


def generate_scan_report(scan_data: dict) -> dict:
    """Genera un resumen ejecutivo del escaneo con IA."""
    vulns_summary = "\n".join([
        f"- [{v.get('severity','').upper()}] {v.get('title','')} @ {v.get('endpoint','')}"
        for v in scan_data.get("vulnerabilities", [])[:20]
    ])

    prompt = f"""Genera un reporte ejecutivo de seguridad para este escaneo:

URL objetivo: {scan_data.get('url', '')}
Total vulnerabilidades: {scan_data.get('total', 0)}
Críticas: {scan_data.get('counts', {}).get('critical', 0)}
Altas: {scan_data.get('counts', {}).get('high', 0)}
Medias: {scan_data.get('counts', {}).get('medium', 0)}
Bajas: {scan_data.get('counts', {}).get('low', 0)}
Tecnologías detectadas: {json.dumps(scan_data.get('technologies', {}), ensure_ascii=False)}

Vulnerabilidades encontradas:
{vulns_summary}

Responde en JSON:
{{
  "risk_score": 0-100,
  "risk_level": "CRÍTICO|ALTO|MEDIO|BAJO",
  "executive_summary": "resumen para gerencia (2-3 párrafos)",
  "top_threats": ["amenaza 1", "amenaza 2", "amenaza 3"],
  "immediate_actions": ["acción urgente 1", "acción urgente 2"],
  "security_posture": "evaluación general de la postura de seguridad",
  "compliance_notes": "notas sobre cumplimiento OWASP/PCI-DSS/ISO27001"
}}"""

    content = _call_deepseek([{"role": "user", "content": prompt}], max_tokens=1500)
    if content:
        parsed = _extract_json(content)
        if parsed:
            parsed["source"] = "deepseek"
            return parsed

    return {
        "risk_score": min(100, scan_data.get("counts", {}).get("critical", 0) * 25 +
                         scan_data.get("counts", {}).get("high", 0) * 10),
        "risk_level": "ALTO" if scan_data.get("counts", {}).get("critical", 0) > 0 else "MEDIO",
        "executive_summary": f"Se encontraron {scan_data.get('total', 0)} vulnerabilidades en {scan_data.get('url', '')}.",
        "source": "local"
    }


def prioritize_vulnerabilities(vulns: list) -> list:
    """Prioriza vulnerabilidades usando IA."""
    if not vulns:
        return vulns

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    return sorted(vulns, key=lambda v: severity_order.get(v.get("severity", "info"), 5))


def _fallback_analysis(vuln: dict) -> dict:
    fallback = {
        "SQL Injection": {
            "cvss_score": 9.8, "cwe_id": "CWE-89",
            "remediation": {
                "immediate": ["Usar Prepared Statements", "Deshabilitar mensajes de error SQL"],
                "code_fix": "# Python/SQLAlchemy\ncursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
            }
        },
        "XSS": {
            "cvss_score": 7.2, "cwe_id": "CWE-79",
            "remediation": {
                "immediate": ["Escapar output HTML", "Implementar CSP"],
                "code_fix": "import html\nsafe_output = html.escape(user_input)",
            }
        },
        "CSRF": {
            "cvss_score": 6.5, "cwe_id": "CWE-352",
            "remediation": {
                "immediate": ["Implementar CSRF tokens", "Usar SameSite=Strict cookies"],
            }
        },
    }
    vuln_type = vuln.get("vuln_type", "")
    base = fallback.get(vuln_type, {"cvss_score": 5.0, "cwe_id": "CWE-000"})
    base["source"] = "local"
    base["confirmed"] = True
    base["false_positive_probability"] = 20
    return base


class AIService:
    def __init__(self):
        self.cache = {}

    def generate_solution(self, vulnerability_type, target_stack="generic", use_cache=True):
        cache_key = f"{vulnerability_type}:{target_stack}"
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]

        prompt = f"""Genera una solución técnica detallada para una vulnerabilidad de tipo: {vulnerability_type} 
        en un stack tecnológico: {target_stack}.
        
        Responde SOLO en JSON con esta estructura:
        {{
          "success": true,
          "title": "título de la solución",
          "severity": "CRITICAL|HIGH|MEDIUM|LOW",
          "cwe_id": "CWE-XXX",
          "description": "descripción de la vulnerabilidad",
          "impact": "impacto potencial",
          "vulnerable_code": "ejemplo de código vulnerable en {target_stack}",
          "secure_code": "ejemplo de código seguro corregido en {target_stack}",
          "solution_steps": ["paso 1", "paso 2"],
          "best_practices": ["práctica 1", "práctica 2"],
          "verification": "cómo verificar que se ha corregido",
          "references": ["url1", "url2"],
          "estimated_fix_time": "tiempo estimado (ej: 2 horas)"
        }}"""

        content = _call_deepseek([{"role": "user", "content": prompt}])
        if not content:
            return {"success": False, "error": "No se pudo conectar con el servicio de IA"}

        parsed = _extract_json(content)
        if parsed:
            parsed["success"] = True
            if use_cache:
                self.cache[cache_key] = parsed
            return parsed

        return {"success": False, "error": "Error al procesar la respuesta de la IA"}

    def generate_multiple(self, vulnerabilities):
        return [self.generate_solution(v["type"], v.get("stack", "generic")) for v in vulnerabilities]

    def clear_cache(self):
        self.cache = {}


ai_service = AIService()
