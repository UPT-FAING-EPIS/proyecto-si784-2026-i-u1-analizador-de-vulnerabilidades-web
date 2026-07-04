import json

import httpx

from .config import settings


def build_local_summary(vulnerabilities: list[dict]) -> str:
    if not vulnerabilities:
        return "No se detectaron vulnerabilidades con los modulos ejecutados. Mantener pruebas periodicas y revisar controles de seguridad manualmente."

    severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
    counts: dict[str, int] = {}
    for vulnerability in vulnerabilities:
        severity = vulnerability.get("severity", "info").lower()
        counts[severity] = counts.get(severity, 0) + 1

    top = sorted(
        vulnerabilities,
        key=lambda item: severity_order.get(item.get("severity", "info").lower(), 0),
        reverse=True,
    )[:3]
    top_titles = ", ".join(item["title"] for item in top)
    counts_text = ", ".join(f"{severity}: {amount}" for severity, amount in sorted(counts.items()))

    return (
        f"Resumen automatico: se encontraron {len(vulnerabilities)} hallazgos ({counts_text}). "
        f"Priorizar: {top_titles}. Revisar evidencias, aplicar mitigaciones y repetir el escaneo."
    )


async def analyze_with_deepseek(vulnerabilities: list[dict], target_url: str) -> str:
    if not settings.deepseek_api_key:
        return build_local_summary(vulnerabilities)

    compact_findings = [
        {
            "module": item.get("module"),
            "severity": item.get("severity"),
            "title": item.get("title"),
            "url": item.get("url"),
            "parameter": item.get("parameter"),
            "evidence": item.get("evidence"),
        }
        for item in vulnerabilities[:25]
    ]

    prompt = (
        "Analiza estos hallazgos de un escaner web defensivo. "
        "Devuelve un resumen ejecutivo breve en espanol, prioridades, impacto probable y siguientes acciones. "
        "No inventes vulnerabilidades que no aparezcan en los datos.\n\n"
        f"Objetivo: {target_url}\n"
        f"Hallazgos: {json.dumps(compact_findings, ensure_ascii=True)}"
    )

    payload = {
        "model": settings.deepseek_model,
        "messages": [
            {"role": "system", "content": "Eres un analista senior de seguridad web."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 700,
    }
    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(settings.deepseek_api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return build_local_summary(vulnerabilities)

