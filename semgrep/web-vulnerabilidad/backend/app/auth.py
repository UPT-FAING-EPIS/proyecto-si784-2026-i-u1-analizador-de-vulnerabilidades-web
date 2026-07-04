from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import ApiKey, User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
API_KEY_SCOPES = ["scans:read", "scans:write", "stats:read"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def generate_api_key() -> str:
    return f"wvs_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def extract_api_key(x_api_key: str | None, authorization: str | None) -> str | None:
    if x_api_key:
        return x_api_key.strip()
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() in {"bearer", "apikey"} and token:
        return token.strip()
    return None


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la sesion",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        subject = payload.get("sub")
        if subject is None:
            raise credentials_error
    except JWTError as exc:
        raise credentials_error from exc

    user = db.query(User).filter(User.id == int(subject)).first()
    if user is None:
        raise credentials_error
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere rol de administrador")
    return current_user


def get_api_key_user(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User:
    raw_api_key = extract_api_key(x_api_key, authorization)
    if not raw_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key requerida. Usa X-API-Key o Authorization: Bearer <api_key>.",
        )

    api_key = db.query(ApiKey).filter(ApiKey.key_hash == hash_api_key(raw_api_key)).first()
    if api_key is None or not api_key.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key invalida o revocada")
    if api_key.expires_at and api_key.expires_at < utc_now():
        api_key.is_active = False
        api_key.revoked_at = utc_now()
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key expirada")

    api_key.last_used_at = utc_now()
    db.commit()
    db.refresh(api_key)
    return api_key.owner
