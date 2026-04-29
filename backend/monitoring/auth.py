"""
monitoring/auth.py
Autenticación con Supabase Auth.
Solo se activa si SUPABASE_URL y SUPABASE_KEY están configurados.

Uso en rutas protegidas:
    from monitoring.auth import require_auth

    @api_blueprint.route('/scan', methods=['POST'])
    @require_auth          ← agrega esto para proteger el endpoint
    def start_scan():
        ...
"""

import os
import logging
import functools
from flask import request, jsonify
import requests as http_requests

logger = logging.getLogger(__name__)


def _get_supabase_user(token: str) -> dict | None:
    """
    Verifica el JWT de Supabase y retorna los datos del usuario.
    Retorna None si el token es inválido o expiró.
    """
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    key = os.environ.get('SUPABASE_KEY', '')

    if not url or not key:
        return None

    try:
        resp = http_requests.get(
            f"{url}/auth/v1/user",
            headers={
                'apikey':        key,
                'Authorization': f'Bearer {token}',
            },
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as e:
        logger.warning(f"Auth check failed: {e}")
        return None


def require_auth(f):
    """
    Decorador que protege un endpoint con autenticación Supabase.

    El cliente debe enviar:
        Authorization: Bearer <supabase_jwt_token>

    Si AUTH_REQUIRED=false en el entorno → no verifica (modo dev).
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # En desarrollo local se puede desactivar
        if os.environ.get('AUTH_REQUIRED', 'true').lower() == 'false':
            return f(*args, **kwargs)

        # Si Supabase no está configurado, pasar sin verificar
        if not os.environ.get('SUPABASE_URL'):
            return f(*args, **kwargs)

        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autorización requerido'}), 401

        token = auth_header.replace('Bearer ', '').strip()
        user = _get_supabase_user(token)

        if not user:
            return jsonify({'error': 'Token inválido o expirado'}), 401

        # Pasar usuario a la función de la ruta
        request.current_user = user
        return f(*args, **kwargs)

    return decorated
