import asyncio
from datetime import date, datetime, timedelta, timezone

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session

from .ai import analyze_with_deepseek
from .auth import (
    API_KEY_SCOPES,
    authenticate_user,
    create_access_token,
    generate_api_key,
    get_api_key_user,
    get_current_admin,
    get_current_user,
    get_password_hash,
    hash_api_key,
    utc_now,
)
from .config import settings
from .database import SessionLocal, get_db
from .init_db import init_database
from .models import ApiKey, Scan, User, Vulnerability
from .scanner import scan_target
from .schemas import (
    DEFAULT_MODULES,
    AdminOverviewOut,
    AdminUserOut,
    ApiKeyCreate,
    ApiKeyCreatedOut,
    ApiKeyOut,
    DailyRegistrationOut,
    IntegrationCatalogOut,
    RegisterRequest,
    ScanCreate,
    ScanDetailOut,
    ScanOut,
    StatsOut,
    TokenResponse,
    UserOut,
)


app = FastAPI(title="Web Vulnerability Scanner API", version="1.0.0")

allowed_origins = {
    settings.frontend_origin,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_database()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def serialize_scan(scan: Scan) -> ScanOut:
    return ScanOut(
        id=scan.id,
        target_url=scan.target_url,
        status=scan.status,
        modules=scan.modules,
        depth=scan.depth,
        timeout=scan.timeout,
        progress=scan.progress,
        risk_score=scan.risk_score,
        ai_summary=scan.ai_summary,
        error_message=scan.error_message,
        created_at=scan.created_at,
        started_at=scan.started_at,
        completed_at=scan.completed_at,
        vulnerability_count=len(scan.vulnerabilities),
    )


def create_scan_for_user(
    payload: ScanCreate,
    background_tasks: BackgroundTasks,
    db: Session,
    user: User,
) -> ScanOut:
    modules = [module for module in payload.modules if module in DEFAULT_MODULES]
    if not modules:
        modules = DEFAULT_MODULES.copy()

    scan = Scan(
        user_id=user.id,
        target_url=str(payload.target_url),
        modules=modules,
        depth=payload.depth,
        timeout=payload.timeout,
        status="pending",
        progress=0,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    background_tasks.add_task(run_scan_task, scan.id)
    return serialize_scan(scan)


def build_stats_for_user(db: Session, user: User) -> StatsOut:
    scan_query = db.query(Scan).filter(Scan.user_id == user.id)
    total_scans = scan_query.count()
    completed_scans = scan_query.filter(Scan.status == "completed").count()
    running_scans = scan_query.filter(Scan.status.in_(["pending", "running"])).count()

    severity_rows = (
        db.query(Vulnerability.severity, func.count(Vulnerability.id))
        .join(Scan, Vulnerability.scan_id == Scan.id)
        .filter(Scan.user_id == user.id)
        .group_by(Vulnerability.severity)
        .all()
    )
    module_rows = (
        db.query(Vulnerability.module, func.count(Vulnerability.id))
        .join(Scan, Vulnerability.scan_id == Scan.id)
        .filter(Scan.user_id == user.id)
        .group_by(Vulnerability.module)
        .all()
    )

    by_severity = {severity: count for severity, count in severity_rows}
    by_module = {module: count for module, count in module_rows}
    return StatsOut(
        total_scans=total_scans,
        completed_scans=completed_scans,
        running_scans=running_scans,
        total_vulnerabilities=sum(by_severity.values()),
        by_severity=by_severity,
        by_module=by_module,
    )


@app.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="El correo ya esta registrado")

    user = User(
        email=payload.email.lower(),
        username=payload.username.strip(),
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@app.post("/api/auth/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Correo o contrasena incorrectos")
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@app.get("/api/auth/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@app.post("/api/scans", response_model=ScanOut, status_code=status.HTTP_201_CREATED)
def create_scan(
    payload: ScanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScanOut:
    return create_scan_for_user(payload, background_tasks, db, current_user)


@app.get("/api/scans", response_model=list[ScanOut])
def list_scans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ScanOut]:
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .limit(50)
        .all()
    )
    return [serialize_scan(scan) for scan in scans]


@app.get("/api/scans/{scan_id}", response_model=ScanDetailOut)
def get_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScanDetailOut:
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if scan is None:
        raise HTTPException(status_code=404, detail="Escaneo no encontrado")
    base = serialize_scan(scan).model_dump()
    base["vulnerabilities"] = scan.vulnerabilities
    return ScanDetailOut.model_validate(base)


@app.get("/api/stats", response_model=StatsOut)
def stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StatsOut:
    return build_stats_for_user(db, current_user)


@app.get("/api/api-keys", response_model=list[ApiKeyOut])
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ApiKey]:
    return (
        db.query(ApiKey)
        .filter(ApiKey.user_id == current_user.id)
        .order_by(ApiKey.created_at.desc())
        .all()
    )


@app.post("/api/api-keys", response_model=ApiKeyCreatedOut, status_code=status.HTTP_201_CREATED)
def create_api_key(
    payload: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiKeyCreatedOut:
    active_key_count = (
        db.query(ApiKey)
        .filter(ApiKey.user_id == current_user.id, ApiKey.is_active.is_(True))
        .count()
    )
    if active_key_count >= 10:
        raise HTTPException(status_code=400, detail="Limite de 10 API keys activas alcanzado")

    expires_at = None
    if payload.expires_in_days:
        expires_at = utc_now() + timedelta(days=payload.expires_in_days)

    raw_key = ""
    key_hash = ""
    for _ in range(5):
        raw_key = generate_api_key()
        key_hash = hash_api_key(raw_key)
        if db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first() is None:
            break
    else:
        raise HTTPException(status_code=500, detail="No se pudo generar una API key unica")

    api_key = ApiKey(
        user_id=current_user.id,
        name=payload.name.strip(),
        key_prefix=raw_key[:16],
        key_hash=key_hash,
        scopes=API_KEY_SCOPES.copy(),
        expires_at=expires_at,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    response = ApiKeyOut.model_validate(api_key).model_dump()
    response["api_key"] = raw_key
    return ApiKeyCreatedOut.model_validate(response)


@app.delete("/api/api-keys/{api_key_id}", response_model=ApiKeyOut)
def revoke_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiKey:
    api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id, ApiKey.user_id == current_user.id).first()
    if api_key is None:
        raise HTTPException(status_code=404, detail="API key no encontrada")

    api_key.is_active = False
    api_key.revoked_at = utc_now()
    db.commit()
    db.refresh(api_key)
    return api_key


@app.get("/api/integrations/catalog", response_model=IntegrationCatalogOut)
def integration_catalog() -> IntegrationCatalogOut:
    return IntegrationCatalogOut(
        service="Web Vulnerability Scanner Integration API",
        authentication="Enviar X-API-Key: <api_key> o Authorization: Bearer <api_key>",
        endpoints=[
            {"method": "GET", "path": "/api/integrations/me", "description": "Identifica al propietario de la API key"},
            {"method": "GET", "path": "/api/integrations/stats", "description": "Resumen de escaneos y hallazgos del usuario"},
            {"method": "GET", "path": "/api/integrations/scans", "description": "Lista los escaneos del usuario"},
            {"method": "POST", "path": "/api/integrations/scans", "description": "Crea un escaneo asincrono"},
            {"method": "GET", "path": "/api/integrations/scans/{scan_id}", "description": "Obtiene un reporte de escaneo"},
        ],
    )


@app.get("/api/integrations/me", response_model=UserOut)
def integration_me(current_user: User = Depends(get_api_key_user)) -> User:
    return current_user


@app.get("/api/integrations/stats", response_model=StatsOut)
def integration_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_key_user),
) -> StatsOut:
    return build_stats_for_user(db, current_user)


@app.get("/api/integrations/scans", response_model=list[ScanOut])
def integration_list_scans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_key_user),
) -> list[ScanOut]:
    return list_scans(db=db, current_user=current_user)


@app.post("/api/integrations/scans", response_model=ScanOut, status_code=status.HTTP_201_CREATED)
def integration_create_scan(
    payload: ScanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_key_user),
) -> ScanOut:
    return create_scan_for_user(payload, background_tasks, db, current_user)


@app.get("/api/integrations/scans/{scan_id}", response_model=ScanDetailOut)
def integration_get_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_key_user),
) -> ScanDetailOut:
    return get_scan(scan_id=scan_id, db=db, current_user=current_user)


@app.get("/api/admin/overview", response_model=AdminOverviewOut)
def admin_overview(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> AdminOverviewOut:
    del current_admin

    total_users = db.query(User).count()
    total_admins = db.query(User).filter(User.is_admin.is_(True)).count()
    total_scans = db.query(Scan).count()
    total_vulnerabilities = db.query(Vulnerability).count()

    start_day = date.today() - timedelta(days=13)
    rows = (
        db.query(func.date(User.created_at).label("day"), func.count(User.id))
        .filter(User.created_at >= datetime.combine(start_day, datetime.min.time()))
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
        .all()
    )
    counts_by_day = {str(day): count for day, count in rows}
    daily_registrations = [
        DailyRegistrationOut(
            date=str(start_day + timedelta(days=offset)),
            count=counts_by_day.get(str(start_day + timedelta(days=offset)), 0),
        )
        for offset in range(14)
    ]

    recent_users = db.query(User).order_by(User.created_at.desc()).limit(10).all()

    return AdminOverviewOut(
        total_users=total_users,
        total_admins=total_admins,
        total_scans=total_scans,
        total_vulnerabilities=total_vulnerabilities,
        daily_registrations=daily_registrations,
        recent_users=[AdminUserOut.model_validate(user) for user in recent_users],
    )


def run_scan_task(scan_id: int) -> None:
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan is None:
            return

        scan.status = "running"
        scan.progress = 15
        scan.started_at = datetime.now(timezone.utc)
        scan.error_message = None
        db.commit()
        db.refresh(scan)

        vulnerabilities, risk_score = scan_target(scan.target_url, scan.modules, scan.depth, scan.timeout)
        scan.progress = 80
        db.commit()

        for item in vulnerabilities:
            db.add(Vulnerability(scan_id=scan.id, **item))
        db.commit()

        ai_summary = asyncio.run(analyze_with_deepseek(vulnerabilities, scan.target_url))
        scan.status = "completed"
        scan.progress = 100
        scan.risk_score = risk_score
        scan.ai_summary = ai_summary
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as exc:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            scan.status = "failed"
            scan.progress = 100
            scan.error_message = str(exc)
            scan.completed_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()
