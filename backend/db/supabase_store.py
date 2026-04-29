"""
db/supabase_store.py
Almacenamiento persistente en Supabase (PostgreSQL).
Usa la REST API de Supabase directamente con requests,
sin necesidad de instalar el SDK de Supabase.

Tabla requerida en Supabase (ver docs/SUPABASE_SETUP.md):
  scans (id, url, status, progress, current_task,
         started_at, completed_at, results, error)
"""

import json
import time
import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)


class SupabaseStore:
    """
    Store de escaneos persistente usando la REST API de Supabase.
    Compatible con el mismo contrato que MemoryStore.
    """

    TABLE = 'scans'

    def __init__(self, supabase_url: str, supabase_key: str):
        self.base = f"{supabase_url.rstrip('/')}/rest/v1"
        self.headers = {
            'apikey':        supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type':  'application/json',
            'Prefer':        'return=representation',
        }
        # Verify connection on startup
        try:
            r = requests.get(
                f"{self.base}/{self.TABLE}?limit=1",
                headers=self.headers,
                timeout=5
            )
            if r.status_code == 200:
                logger.info("Supabase conectado correctamente ✅")
            else:
                logger.error(f"Supabase error al conectar: {r.status_code} {r.text}")
        except Exception as e:
            logger.error(f"No se pudo conectar a Supabase: {e}")

    # ── CREATE ────────────────────────────────────────────────────

    def create_scan(self, scan_id: str, url: str) -> dict:
        """Inserta un nuevo registro de escaneo en Supabase."""
        scan = {
            'id':           scan_id,
            'url':          url,
            'status':       'pending',
            'progress':     0,
            'current_task': 'En espera...',
            'started_at':   time.time(),
            'completed_at': None,
            'results':      None,
            'error':        None,
        }
        try:
            r = requests.post(
                f"{self.base}/{self.TABLE}",
                headers=self.headers,
                json=self._serialize(scan),
                timeout=10
            )
            if r.status_code in (200, 201):
                return scan
            else:
                logger.error(f"create_scan error: {r.status_code} {r.text}")
                return scan   # return in-memory version as fallback
        except Exception as e:
            logger.error(f"create_scan exception: {e}")
            return scan

    # ── READ ──────────────────────────────────────────────────────

    def get_scan(self, scan_id: str) -> Optional[dict]:
        """Obtiene un escaneo por ID desde Supabase."""
        try:
            r = requests.get(
                f"{self.base}/{self.TABLE}?id=eq.{scan_id}&limit=1",
                headers=self.headers,
                timeout=10
            )
            if r.status_code == 200:
                rows = r.json()
                if rows:
                    return self._deserialize(rows[0])
            return None
        except Exception as e:
            logger.error(f"get_scan exception: {e}")
            return None

    def list_scans(self, limit: int = 50) -> list:
        """Lista escaneos recientes (sin results para ahorrar ancho de banda)."""
        try:
            r = requests.get(
                f"{self.base}/{self.TABLE}"
                f"?select=id,url,status,progress,started_at,completed_at,error"
                f"&order=started_at.desc&limit={limit}",
                headers=self.headers,
                timeout=10
            )
            if r.status_code == 200:
                return r.json()
            logger.error(f"list_scans error: {r.status_code} {r.text}")
            return []
        except Exception as e:
            logger.error(f"list_scans exception: {e}")
            return []

    # ── UPDATE ────────────────────────────────────────────────────

    def update_scan(self, scan_id: str, **fields) -> bool:
        """Actualiza campos de un escaneo en Supabase."""
        try:
            payload = self._serialize(fields)
            r = requests.patch(
                f"{self.base}/{self.TABLE}?id=eq.{scan_id}",
                headers=self.headers,
                json=payload,
                timeout=15
            )
            if r.status_code in (200, 204):
                return True
            logger.error(f"update_scan error: {r.status_code} {r.text}")
            return False
        except Exception as e:
            logger.error(f"update_scan exception: {e}")
            return False

    # ── DELETE ────────────────────────────────────────────────────

    def delete_scan(self, scan_id: str) -> bool:
        """Elimina un escaneo de Supabase."""
        try:
            r = requests.delete(
                f"{self.base}/{self.TABLE}?id=eq.{scan_id}",
                headers=self.headers,
                timeout=10
            )
            return r.status_code in (200, 204)
        except Exception as e:
            logger.error(f"delete_scan exception: {e}")
            return False

    # ── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def _serialize(data: dict) -> dict:
        """Convierte results (dict) a JSON string para PostgreSQL."""
        out = dict(data)
        if 'results' in out and isinstance(out['results'], dict):
            out['results'] = json.dumps(out['results'])
        return out

    @staticmethod
    def _deserialize(row: dict) -> dict:
        """Convierte results (JSON string) de vuelta a dict."""
        if row.get('results') and isinstance(row['results'], str):
            try:
                row['results'] = json.loads(row['results'])
            except Exception:
                pass
        return row
