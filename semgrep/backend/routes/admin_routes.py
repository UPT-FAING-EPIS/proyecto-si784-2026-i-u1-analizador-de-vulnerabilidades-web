"""
Rutas del panel de administración: usuarios, estadísticas, logs.
"""
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models
from auth import get_current_user, require_admin, get_password_hash

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def admin_only(current_user: models.User = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(403, "Solo administradores")
    return current_user


# ── Dashboard stats ───────────────────────────────────────────────────────────

@router.get("/dashboard")
def dashboard_stats(db: Session = Depends(get_db), _=Depends(admin_only)):
    total_users = db.query(func.count(models.User.id)).scalar()
    total_scans = db.query(func.count(models.Scan.id)).scalar()
    total_vulns = db.query(func.count(models.Vulnerability.id)).scalar()
    critical_vulns = db.query(func.count(models.Vulnerability.id)).filter(
        models.Vulnerability.severity == models.SeverityLevel.critical
    ).scalar()

    recent_scans = db.query(models.Scan).order_by(models.Scan.id.desc()).limit(10).all()
    recent_logs = db.query(models.AuditLog).order_by(models.AuditLog.id.desc()).limit(20).all()

    # Scans by day (last 7 days)
    seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    daily_scans = db.query(
        func.date(models.Scan.created_at).label("date"),
        func.count(models.Scan.id).label("count")
    ).filter(
        models.Scan.created_at >= seven_days_ago
    ).group_by(func.date(models.Scan.created_at)).all()

    # Vulns by severity
    vuln_by_sev = db.query(
        models.Vulnerability.severity,
        func.count(models.Vulnerability.id).label("count")
    ).group_by(models.Vulnerability.severity).all()

    return {
        "stats": {
            "total_users": total_users,
            "total_scans": total_scans,
            "total_vulns": total_vulns,
            "critical_vulns": critical_vulns,
        },
        "recent_scans": [
            {
                "id": s.id,
                "url": s.target_url,
                "status": s.status.value,
                "total_vulns": s.total_vulns or 0,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in recent_scans
        ],
        "recent_activity": [
            {
                "id": l.id,
                "action": l.action,
                "user_id": l.user_id,
                "ip": l.ip_address,
                "success": l.success,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in recent_logs
        ],
        "daily_scans": [{"date": str(r.date), "count": r.count} for r in daily_scans],
        "vulns_by_severity": [{"severity": r.severity.value, "count": r.count} for r in vuln_by_sev],
    }


# ── Users management ──────────────────────────────────────────────────────────

@router.get("/users")
def list_users(
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    _=Depends(admin_only)
):
    users = db.query(models.User).offset(skip).limit(limit).all()
    total = db.query(func.count(models.User.id)).scalar()
    return {
        "total": total,
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role.value,
                "is_active": u.is_active,
                "last_login": u.last_login.isoformat() if u.last_login else None,
                "last_login_ip": u.last_login_ip,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "failed_attempts": u.failed_login_attempts or 0,
                "locked": u.locked_until is not None and u.locked_until > datetime.datetime.utcnow(),
            }
            for u in users
        ]
    }


@router.patch("/users/{user_id}/role")
def update_role(
    user_id: int,
    body: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_only)
):
    if user_id == current_user.id:
        raise HTTPException(400, "No puedes cambiar tu propio rol")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    new_role = body.get("role")
    if new_role not in ("admin", "analyst", "user"):
        raise HTTPException(400, "Rol inválido")
    user.role = models.UserRole(new_role)
    db.commit()
    return {"message": f"Rol actualizado a {new_role}"}


@router.patch("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_only)
):
    if user_id == current_user.id:
        raise HTTPException(400, "No puedes desactivar tu propia cuenta")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    user.is_active = not user.is_active
    db.commit()
    return {"is_active": user.is_active}


@router.patch("/users/{user_id}/unlock")
def unlock_user(user_id: int, db: Session = Depends(get_db), _=Depends(admin_only)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    user.locked_until = None
    user.failed_login_attempts = 0
    db.commit()
    return {"message": "Usuario desbloqueado"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_only)
):
    if user_id == current_user.id:
        raise HTTPException(400, "No puedes eliminar tu propia cuenta")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado"}


# ── Audit logs ────────────────────────────────────────────────────────────────

@router.get("/logs")
def get_logs(
    skip: int = 0, limit: int = 100,
    action: str = None,
    db: Session = Depends(get_db),
    _=Depends(admin_only)
):
    query = db.query(models.AuditLog).order_by(models.AuditLog.id.desc())
    if action:
        query = query.filter(models.AuditLog.action == action)
    total = query.count()
    logs = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "logs": [
            {
                "id": l.id,
                "user_id": l.user_id,
                "action": l.action,
                "resource": l.resource,
                "ip": l.ip_address,
                "success": l.success,
                "details": l.details,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in logs
        ]
    }
