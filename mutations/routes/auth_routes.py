"""
Rutas de autenticación con roles, brute-force protection y audit logs.
"""
import datetime
import secrets
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, handle_failed_login, reset_failed_login
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("username")
    @classmethod
    def val_username(cls, v):
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Mínimo 3 caracteres")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Solo letras, números, guiones y guiones bajos")
        return v

    @field_validator("password")
    @classmethod
    def val_password(cls, v):
        if len(v) < 8:
            raise ValueError("Mínimo 8 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("Debe contener al menos una mayúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Debe contener al menos un número")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    user_id: int
    role: str


class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime.datetime
    last_login: datetime.datetime | None = None

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def val_new(cls, v):
        if len(v) < 8:
            raise ValueError("Mínimo 8 caracteres")
        return v


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def val_new(cls, v):
        if len(v) < 8:
            raise ValueError("Mínimo 8 caracteres")
        return v


# ── Helpers ───────────────────────────────────────────────────────────────────

def log_action(db: Session, user_id: int | None, action: str, ip: str, success: bool, details: dict = None):
    entry = models.AuditLog(
        user_id=user_id,
        action=action,
        ip_address=ip,
        success=success,
        details=details or {},
        created_at=datetime.datetime.utcnow(),
    )
    db.add(entry)
    db.commit()


def get_client_ip(request: Request) -> str:
    fwd = request.headers.get("X-Forwarded-For")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, req: Request, db: Session = Depends(get_db)):
    ip = get_client_ip(req)

    if db.query(models.User).filter(models.User.username == request.username).first():
        raise HTTPException(400, "Username ya en uso")
    if db.query(models.User).filter(models.User.email == request.email).first():
        raise HTTPException(400, "Email ya registrado")

    # Primer usuario es admin
    is_first = db.query(models.User).count() == 0
    role = models.UserRole.admin if is_first else models.UserRole.user

    user = models.User(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    log_action(db, user.id, "register", ip, True, {"username": user.username})

    return {
        "message": "Usuario registrado exitosamente",
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "user_id": user.id,
        "role": user.role.value,
    }


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    req: Request = None,
    db: Session = Depends(get_db),
):
    ip = get_client_ip(req) if req else "unknown"

    user = db.query(models.User).filter(
        (models.User.username == form_data.username) | (models.User.email == form_data.username)
    ).first()

    if not user:
        log_action(db, None, "login_failed", ip, False, {"username": form_data.username})
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas")

    # Check lockout
    if user.locked_until and user.locked_until > datetime.datetime.utcnow():
        minutes = int((user.locked_until - datetime.datetime.utcnow()).seconds / 60) + 1
        raise HTTPException(403, f"Cuenta bloqueada. Intenta en {minutes} minutos.")

    if not verify_password(form_data.password, user.hashed_password):
        handle_failed_login(db, user)
        log_action(db, user.id, "login_failed", ip, False)
        attempts_left = max(0, 5 - (user.failed_login_attempts or 0))
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            f"Credenciales inválidas. Intentos restantes: {attempts_left}")

    if not user.is_active:
        raise HTTPException(400, "Cuenta desactivada")

    reset_failed_login(db, user)
    user.last_login = datetime.datetime.utcnow()
    user.last_login_ip = ip
    db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    log_action(db, user.id, "login", ip, True)

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "user_id": user.id,
        "role": user.role.value,
    }


@router.get("/me", response_model=UserProfile)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("/change-password")
def change_password(
    body: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(400, "Contraseña actual incorrecta")
    current_user.hashed_password = get_password_hash(body.new_password)
    db.commit()
    return {"message": "Contraseña actualizada exitosamente"}


@router.post("/forgot-password")
def forgot_password(
    body: ForgotPasswordRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user:
        return {"message": "Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña"}

    token = secrets.token_urlsafe(32)
    expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    reset_entry = models.PasswordReset(
        user_id=user.id,
        token=token,
        expires_at=expires
    )
    db.add(reset_entry)
    db.commit()

    log_action(db, user.id, "forgot_password_requested", get_client_ip(req), True, {"token": token})

    return {
        "message": "Instrucciones enviadas al correo",
        "dev_token": token
    }


@router.post("/reset-password")
def reset_password(
    body: ResetPasswordRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    reset_entry = db.query(models.PasswordReset).filter(
        models.PasswordReset.token == body.token,
        models.PasswordReset.used == False,
        models.PasswordReset.expires_at > datetime.datetime.utcnow()
    ).first()

    if not reset_entry:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token inválido o expirado")

    user = db.query(models.User).filter(models.User.id == reset_entry.user_id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")

    user.hashed_password = get_password_hash(body.new_password)
    reset_entry.used = True
    db.commit()

    log_action(db, user.id, "password_reset_success", get_client_ip(req), True)

    return {"message": "Contraseña restablecida exitosamente"}
