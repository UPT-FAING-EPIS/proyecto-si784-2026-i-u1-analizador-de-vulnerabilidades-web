from datetime import datetime

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, Field, HttpUrl, field_validator


DEFAULT_MODULES = ["xss", "sqli", "headers", "csrf", "open_redirect", "info_disclosure"]


class RegisterRequest(BaseModel):
    email: str
    username: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email_address(cls, value: str) -> str:
        try:
            result = validate_email(value, check_deliverability=False, test_environment=True)
        except EmailNotValidError as exc:
            raise ValueError(str(exc)) from exc
        return result.normalized.lower()


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ScanCreate(BaseModel):
    target_url: HttpUrl
    modules: list[str] = Field(default_factory=lambda: DEFAULT_MODULES.copy())
    depth: int = Field(default=1, ge=0, le=3)
    timeout: int = Field(default=10, ge=3, le=30)


class VulnerabilityOut(BaseModel):
    id: int
    module: str
    severity: str
    title: str
    description: str
    evidence: str | None
    remediation: str
    url: str
    parameter: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ScanOut(BaseModel):
    id: int
    target_url: str
    status: str
    modules: list[str]
    depth: int
    timeout: int
    progress: int
    risk_score: int
    ai_summary: str | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    vulnerability_count: int = 0

    model_config = {"from_attributes": True}


class ScanDetailOut(ScanOut):
    vulnerabilities: list[VulnerabilityOut] = Field(default_factory=list)


class StatsOut(BaseModel):
    total_scans: int
    completed_scans: int
    running_scans: int
    total_vulnerabilities: int
    by_severity: dict[str, int]
    by_module: dict[str, int]


class DailyRegistrationOut(BaseModel):
    date: str
    count: int


class AdminUserOut(BaseModel):
    id: int
    email: str
    username: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminOverviewOut(BaseModel):
    total_users: int
    total_admins: int
    total_scans: int
    total_vulnerabilities: int
    daily_registrations: list[DailyRegistrationOut]
    recent_users: list[AdminUserOut]


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    expires_in_days: int | None = Field(default=None, ge=1, le=365)


class ApiKeyOut(BaseModel):
    id: int
    name: str
    key_prefix: str
    scopes: list[str]
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None
    expires_at: datetime | None
    revoked_at: datetime | None

    model_config = {"from_attributes": True}


class ApiKeyCreatedOut(ApiKeyOut):
    api_key: str


class IntegrationCatalogOut(BaseModel):
    service: str
    authentication: str
    endpoints: list[dict[str, str]]
