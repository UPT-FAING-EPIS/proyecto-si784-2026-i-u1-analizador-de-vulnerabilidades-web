"""
monitoring/health.py
Endpoint /health enriquecido para UptimeRobot y Azure.
Verifica que todos los componentes críticos estén operativos.
"""

import os
import time
import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

health_blueprint = Blueprint('health', __name__)

# Timestamp de inicio del servidor
_START_TIME = time.time()


@health_blueprint.route('/health')
def health_check():
    """
    Endpoint de salud para UptimeRobot.
    UptimeRobot hace GET a esta URL cada 5 minutos.
    Si responde 200 → todo bien.
    Si responde 500 o no responde → te manda email de alerta.
    """
    checks = {}
    overall_ok = True

    # ── Check 1: Base de datos (Supabase o memoria) ───────────
    try:
        from db import get_store
        store = get_store()
        store_type = type(store).__name__

        if store_type == 'SupabaseStore':
            # Ping a Supabase con una consulta liviana
            result = store.list_scans(limit=1)
            checks['database'] = {
                'status': 'ok',
                'type': 'supabase',
            }
        else:
            checks['database'] = {
                'status': 'ok',
                'type': 'memory',
            }
    except Exception as e:
        checks['database'] = {'status': 'error', 'detail': str(e)}
        overall_ok = False

    # ── Check 2: Módulos core ─────────────────────────────────
    try:
        from core.engine import ScanEngine
        from rules.engine import RuleEngine
        checks['core'] = {'status': 'ok'}
    except Exception as e:
        checks['core'] = {'status': 'error', 'detail': str(e)}
        overall_ok = False

    # ── Check 3: Variables de entorno importantes ─────────────
    env_vars = {
        'SUPABASE_URL':  bool(os.environ.get('SUPABASE_URL')),
        'SUPABASE_KEY':  bool(os.environ.get('SUPABASE_KEY')),
        'SENTRY_DSN':    bool(os.environ.get('SENTRY_DSN')),
        'FRONTEND_URL':  bool(os.environ.get('FRONTEND_URL')),
    }
    checks['config'] = {
        'status': 'ok',
        'env_vars_set': env_vars,
    }

    # ── Respuesta ─────────────────────────────────────────────
    uptime_seconds = round(time.time() - _START_TIME)
    hours, rem = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    response = {
        'status':  'ok' if overall_ok else 'degraded',
        'service': 'vulnscan-backend',
        'version': '1.0.0',
        'uptime':  f"{hours}h {minutes}m {seconds}s",
        'checks':  checks,
    }

    status_code = 200 if overall_ok else 500
    return response, status_code


@health_blueprint.route('/ping')
def ping():
    """Endpoint ultra-ligero. Solo responde 'pong'. Para checks rápidos."""
    return {'pong': True}, 200
