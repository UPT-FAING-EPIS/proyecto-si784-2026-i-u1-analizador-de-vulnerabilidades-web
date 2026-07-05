"""
Rutas de escaneo: lanzar, consultar, obtener vulnerabilidades.
"""
import datetime
import threading
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user, get_optional_user
from scanner import run_full_scan
from ai_service import analyze_vulnerability, generate_scan_report, prioritize_vulnerabilities

router = APIRouter(prefix="/api/scans", tags=["Scans"])

ALL_MODULES = [
    "Headers", "SSL", "XSS", "SQLi", "CSRF", "OpenRedirect",
    "LFI", "CommandInjection", "SSRF", "SensitiveFiles",
    "HttpMethods", "ErrorDisclosure", "Crawling",
]


# ── Schemas ───────────────────────────────────────────────────────────────────

class ScanRequest(BaseModel):
    url: str
    modules: List[str] = ["All"]
    depth: int = 2
    timeout: int = 10
    use_ai: bool = True
    stack: str = "generic"


class ScanResponse(BaseModel):
    id: int
    target_url: str
    status: str
    total_vulns: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ── Background scan ───────────────────────────────────────────────────────────

def _run_scan_background(scan_id: int, url: str, modules: list, depth: int, timeout: int, use_ai: bool, stack: str):
    from database import SessionLocal
    db = SessionLocal()
    try:
        scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
        if not scan:
            return

        scan.status = models.ScanStatus.running
        db.commit()

        result = run_full_scan(url, modules, depth, timeout)
        vulns_data = prioritize_vulnerabilities(result.get("vulnerabilities", []))

        # Guardar vulnerabilidades
        for v in vulns_data:
            ai_data = None
            if use_ai:
                try:
                    ai_data = analyze_vulnerability(v, stack)
                except Exception:
                    pass

            vuln_obj = models.Vulnerability(
                scan_id=scan_id,
                vuln_type=v.get("vuln_type", "Unknown"),
                severity=models.SeverityLevel(v.get("severity", "info")),
                title=v.get("title", ""),
                description=v.get("description", ""),
                endpoint=v.get("endpoint", "")[:2000],
                parameter=v.get("parameter", ""),
                payload=v.get("payload", ""),
                evidence=v.get("evidence", ""),
                risk=v.get("risk", ""),
                solution=v.get("solution", ""),
                ai_analysis=ai_data,
                cwe_id=v.get("cwe_id", ai_data.get("cwe_id") if ai_data else None),
                cvss_score=ai_data.get("cvss_score") if ai_data else None,
            )
            db.add(vuln_obj)

        counts = result.get("counts", {})
        ai_report = None
        if use_ai:
            try:
                ai_report = generate_scan_report(result)
            except Exception:
                pass

        scan.status = models.ScanStatus.completed
        scan.total_vulns = result.get("total", 0)
        scan.critical_count = counts.get("critical", 0)
        scan.high_count = counts.get("high", 0)
        scan.medium_count = counts.get("medium", 0)
        scan.low_count = counts.get("low", 0)
        scan.technologies = result.get("technologies", {})
        scan.crawled_urls = [c.get("url") for c in result.get("crawled_urls", [])][:50]
        scan.scan_duration = result.get("duration")
        scan.result_summary = {"ai_report": ai_report, "counts": counts}
        scan.completed_at = datetime.datetime.utcnow()
        db.commit()

    except Exception as e:
        db = SessionLocal()
        scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
        if scan:
            scan.status = models.ScanStatus.failed
            scan.error_message = str(e)[:500]
            db.commit()
    finally:
        db.close()


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/", status_code=201)
def start_scan(
    req: ScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_optional_user),
):
    url = req.url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    modules = req.modules
    if "All" in modules:
        modules = ALL_MODULES

    scan = models.Scan(
        target_url=url,
        status=models.ScanStatus.pending,
        user_id=current_user.id if current_user else None,
        modules=modules,
        depth=req.depth,
        timeout=req.timeout,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    background_tasks.add_task(
        _run_scan_background,
        scan.id, url, modules, req.depth, req.timeout, req.use_ai, req.stack
    )

    return {"id": scan.id, "status": "pending", "message": "Escaneo iniciado en segundo plano"}


@router.get("/")
def list_scans(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_optional_user),
):
    query = db.query(models.Scan).order_by(models.Scan.id.desc())
    if current_user and current_user.role.value == "user":
        query = query.filter(models.Scan.user_id == current_user.id)

    total = query.count()
    scans = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "scans": [
            {
                "id": s.id,
                "target_url": s.target_url,
                "status": s.status.value,
                "total_vulns": s.total_vulns or 0,
                "critical_count": s.critical_count or 0,
                "high_count": s.high_count or 0,
                "medium_count": s.medium_count or 0,
                "low_count": s.low_count or 0,
                "scan_duration": s.scan_duration,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            }
            for s in scans
        ]
    }


@router.get("/{scan_id}")
def get_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_optional_user),
):
    scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Escaneo no encontrado")

    vulns = db.query(models.Vulnerability).filter(models.Vulnerability.scan_id == scan_id).all()

    return {
        "id": scan.id,
        "target_url": scan.target_url,
        "status": scan.status.value,
        "modules": scan.modules,
        "total_vulns": scan.total_vulns or 0,
        "critical_count": scan.critical_count or 0,
        "high_count": scan.high_count or 0,
        "medium_count": scan.medium_count or 0,
        "low_count": scan.low_count or 0,
        "technologies": scan.technologies or {},
        "crawled_urls": scan.crawled_urls or [],
        "scan_duration": scan.scan_duration,
        "result_summary": scan.result_summary or {},
        "error_message": scan.error_message,
        "created_at": scan.created_at.isoformat() if scan.created_at else None,
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        "vulnerabilities": [
            {
                "id": v.id,
                "vuln_type": v.vuln_type,
                "severity": v.severity.value,
                "title": v.title,
                "description": v.description,
                "endpoint": v.endpoint,
                "payload": v.payload,
                "evidence": v.evidence,
                "risk": v.risk,
                "solution": v.solution,
                "ai_analysis": v.ai_analysis,
                "cwe_id": v.cwe_id,
                "cvss_score": v.cvss_score,
                "false_positive": v.false_positive,
            }
            for v in vulns
        ],
    }


@router.delete("/{scan_id}")
def delete_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Escaneo no encontrado")
    if current_user.role.value == "user" and scan.user_id != current_user.id:
        raise HTTPException(403, "No tienes permiso para eliminar este escaneo")
    db.delete(scan)
    db.commit()
    return {"message": "Escaneo eliminado"}


@router.patch("/{scan_id}/vulnerabilities/{vuln_id}/false-positive")
def mark_false_positive(
    scan_id: int,
    vuln_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    vuln = db.query(models.Vulnerability).filter(
        models.Vulnerability.id == vuln_id,
        models.Vulnerability.scan_id == scan_id,
    ).first()
    if not vuln:
        raise HTTPException(404, "Vulnerabilidad no encontrada")
    vuln.false_positive = not vuln.false_positive
    db.commit()
    return {"false_positive": vuln.false_positive}
