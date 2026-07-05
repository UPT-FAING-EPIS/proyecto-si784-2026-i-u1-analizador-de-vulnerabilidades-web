"""
Generación de reportes: PDF, HTML, JSON.
"""
import json
import datetime
import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user

router = APIRouter(prefix="/api/reports", tags=["Reports"])

REPORTS_DIR = os.getenv("REPORTS_DIR", "/tmp/vulnscan_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

SEVERITY_COLORS = {
    "critical": "#dc2626",
    "high": "#ea580c",
    "medium": "#d97706",
    "low": "#2563eb",
    "info": "#6b7280",
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>VulnScan Report - {url}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #e2e8f0; }}
  .header {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 40px; border-bottom: 2px solid #3b82f6; }}
  .logo {{ font-size: 28px; font-weight: 700; color: #3b82f6; }}
  .logo span {{ color: #10b981; }}
  h1 {{ font-size: 22px; margin-top: 10px; color: #f1f5f9; }}
  .meta {{ color: #94a3b8; font-size: 14px; margin-top: 8px; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
  .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }}
  .stat-card {{ background: #1e293b; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #334155; }}
  .stat-value {{ font-size: 36px; font-weight: 700; }}
  .stat-label {{ color: #94a3b8; font-size: 13px; margin-top: 5px; }}
  .critical {{ color: #dc2626; }} .high {{ color: #ea580c; }}
  .medium {{ color: #d97706; }} .low {{ color: #2563eb; }}
  .section {{ margin: 30px 0; }}
  .section-title {{ font-size: 18px; font-weight: 600; margin-bottom: 20px; padding-bottom: 10px;
    border-bottom: 1px solid #334155; color: #f1f5f9; }}
  .vuln-card {{ background: #1e293b; border-radius: 10px; margin: 15px 0; padding: 20px;
    border-left: 4px solid; border-color: var(--sev-color); }}
  .vuln-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
  .vuln-title {{ font-size: 16px; font-weight: 600; }}
  .badge {{ padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;
    color: white; background: var(--sev-color); }}
  .detail {{ margin: 8px 0; font-size: 14px; color: #cbd5e1; }}
  .detail strong {{ color: #94a3b8; margin-right: 8px; }}
  .code {{ background: #0f172a; border-radius: 6px; padding: 12px; font-family: monospace;
    font-size: 13px; color: #10b981; margin: 10px 0; word-break: break-all; }}
  .solution {{ background: #052e16; border: 1px solid #166534; border-radius: 8px;
    padding: 15px; margin-top: 12px; }}
  .solution-title {{ color: #4ade80; font-weight: 600; margin-bottom: 8px; }}
  footer {{ text-align: center; padding: 30px; color: #475569; font-size: 13px;
    border-top: 1px solid #1e293b; margin-top: 40px; }}
</style>
</head>
<body>
<div class="header">
  <div class="logo">Vuln<span>Scan</span> Pro</div>
  <h1>Reporte de Análisis de Vulnerabilidades</h1>
  <div class="meta">
    Objetivo: {url} &nbsp;|&nbsp; Fecha: {date} &nbsp;|&nbsp;
    Duración: {duration}s &nbsp;|&nbsp; Total hallazgos: {total}
  </div>
</div>
<div class="container">
  <div class="stats-grid">
    <div class="stat-card"><div class="stat-value critical">{critical}</div><div class="stat-label">Críticas</div></div>
    <div class="stat-card"><div class="stat-value high">{high}</div><div class="stat-label">Altas</div></div>
    <div class="stat-card"><div class="stat-value medium">{medium}</div><div class="stat-label">Medias</div></div>
    <div class="stat-card"><div class="stat-value low">{low}</div><div class="stat-label">Bajas</div></div>
  </div>

  {tech_section}

  <div class="section">
    <div class="section-title">Vulnerabilidades Encontradas</div>
    {vulns_html}
  </div>
</div>
<footer>VulnScan Pro &mdash; Reporte generado el {date} &mdash; Confidencial</footer>
</body>
</html>"""


def _build_vuln_html(v: models.Vulnerability) -> str:
    sev = v.severity.value
    color = SEVERITY_COLORS.get(sev, "#6b7280")
    ai = v.ai_analysis or {}
    remediation = ai.get("remediation", {})
    immediate = remediation.get("immediate", [])
    code_fix = remediation.get("code_fix", v.solution or "")

    imm_html = "".join(f"<li>{a}</li>" for a in immediate) if immediate else ""
    solution_content = f"<ul>{imm_html}</ul>" if imm_html else f"<p>{v.solution or 'Ver documentación OWASP'}</p>"
    if code_fix:
        solution_content += f'<div class="code">{code_fix[:500]}</div>'

    cwe = v.cwe_id or ai.get("cwe_id", "")
    cvss = f"{v.cvss_score:.1f}" if v.cvss_score else (f"{ai.get('cvss_score', 'N/A')}")

    return f"""
<div class="vuln-card" style="--sev-color: {color}; border-left-color: {color}">
  <div class="vuln-header">
    <div class="vuln-title">{v.title}</div>
    <span class="badge" style="background: {color}">{sev.upper()}</span>
  </div>
  <div class="detail"><strong>Tipo:</strong> {v.vuln_type}</div>
  <div class="detail"><strong>Endpoint:</strong> <span style="color:#60a5fa">{v.endpoint or 'N/A'}</span></div>
  {"<div class='detail'><strong>CWE:</strong> " + cwe + "</div>" if cwe else ""}
  {"<div class='detail'><strong>CVSS:</strong> " + str(cvss) + "</div>" if cvss else ""}
  <div class="detail"><strong>Descripción:</strong> {v.description or ''}</div>
  {"<div class='code'><strong>Payload:</strong> " + (v.payload or '') + "</div>" if v.payload else ""}
  {"<div class='detail'><strong>Evidencia:</strong> " + (v.evidence or '') + "</div>" if v.evidence else ""}
  <div class="solution">
    <div class="solution-title">Solución Recomendada</div>
    {solution_content}
  </div>
</div>"""


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/{scan_id}/json")
def report_json(scan_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Escaneo no encontrado")
    vulns = db.query(models.Vulnerability).filter(models.Vulnerability.scan_id == scan_id).all()

    return {
        "report_type": "VulnScan Professional Report",
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "scan": {
            "id": scan.id,
            "url": scan.target_url,
            "status": scan.status.value,
            "duration": scan.scan_duration,
            "technologies": scan.technologies or {},
        },
        "summary": {
            "total": scan.total_vulns or 0,
            "critical": scan.critical_count or 0,
            "high": scan.high_count or 0,
            "medium": scan.medium_count or 0,
            "low": scan.low_count or 0,
        },
        "ai_report": (scan.result_summary or {}).get("ai_report"),
        "vulnerabilities": [
            {
                "id": v.id,
                "type": v.vuln_type,
                "severity": v.severity.value,
                "title": v.title,
                "description": v.description,
                "endpoint": v.endpoint,
                "payload": v.payload,
                "evidence": v.evidence,
                "risk": v.risk,
                "solution": v.solution,
                "cwe_id": v.cwe_id,
                "cvss_score": v.cvss_score,
                "ai_analysis": v.ai_analysis,
                "false_positive": v.false_positive,
            }
            for v in vulns
        ],
    }


@router.get("/{scan_id}/html")
def report_html(scan_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Escaneo no encontrado")
    vulns = db.query(models.Vulnerability).filter(models.Vulnerability.scan_id == scan_id).all()

    techs = scan.technologies or {}
    tech_items = []
    for category, items in techs.items():
        if items:
            tech_items.append(f"<strong>{category.title()}:</strong> {', '.join(items)}")
    tech_section = ""
    if tech_items:
        tech_section = f"""
<div class="section">
  <div class="section-title">Tecnologías Detectadas</div>
  <div class="stat-card" style="text-align:left; padding: 20px">
    {'<br>'.join(tech_items)}
  </div>
</div>"""

    vulns_html = "".join(_build_vuln_html(v) for v in vulns) if vulns else "<p>No se encontraron vulnerabilidades.</p>"

    html = HTML_TEMPLATE.format(
        url=scan.target_url,
        date=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        duration=scan.scan_duration or "N/A",
        total=scan.total_vulns or 0,
        critical=scan.critical_count or 0,
        high=scan.high_count or 0,
        medium=scan.medium_count or 0,
        low=scan.low_count or 0,
        tech_section=tech_section,
        vulns_html=vulns_html,
    )

    filename = f"vulnscan_report_{scan_id}_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return FileResponse(filepath, media_type="text/html", filename=filename)


@router.get("/{scan_id}/pdf")
def report_pdf(scan_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Genera PDF usando WeasyPrint si está disponible, sino devuelve HTML."""
    scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Escaneo no encontrado")

    try:
        from weasyprint import HTML as WPhtml
        vulns = db.query(models.Vulnerability).filter(models.Vulnerability.scan_id == scan_id).all()
        vulns_html = "".join(_build_vuln_html(v) for v in vulns) if vulns else "<p>Sin vulnerabilidades.</p>"
        html_content = HTML_TEMPLATE.format(
            url=scan.target_url,
            date=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            duration=scan.scan_duration or "N/A",
            total=scan.total_vulns or 0,
            critical=scan.critical_count or 0,
            high=scan.high_count or 0,
            medium=scan.medium_count or 0,
            low=scan.low_count or 0,
            tech_section="",
            vulns_html=vulns_html,
        )

        filename = f"vulnscan_report_{scan_id}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)
        WPhtml(string=html_content).write_pdf(filepath)
        return FileResponse(filepath, media_type="application/pdf", filename=filename)
    except ImportError:
        return report_html(scan_id, db, _)
