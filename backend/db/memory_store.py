"""
db/memory_store.py
Almacenamiento en memoria RAM. Igual al comportamiento original.
Los datos se pierden al reiniciar el servidor.
"""

import time
from typing import Optional


class MemoryStore:
    """Store de escaneos en memoria (sin persistencia)."""

    def __init__(self):
        self._scans: dict = {}

    def create_scan(self, scan_id: str, url: str) -> dict:
        """Crea un nuevo registro de escaneo."""
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
        self._scans[scan_id] = scan
        return scan

    def get_scan(self, scan_id: str) -> Optional[dict]:
        """Obtiene un escaneo por ID. Retorna None si no existe."""
        return self._scans.get(scan_id)

    def update_scan(self, scan_id: str, **fields) -> bool:
        """Actualiza campos de un escaneo existente."""
        if scan_id not in self._scans:
            return False
        self._scans[scan_id].update(fields)
        return True

    def list_scans(self, limit: int = 50) -> list:
        """Lista todos los escaneos ordenados por fecha (más reciente primero)."""
        scans = list(self._scans.values())
        scans.sort(key=lambda s: s.get('started_at', 0), reverse=True)
        # Excluir resultados completos de la lista (payload grande)
        return [
            {k: v for k, v in s.items() if k != 'results'}
            for s in scans[:limit]
        ]

    def delete_scan(self, scan_id: str) -> bool:
        """Elimina un escaneo."""
        if scan_id in self._scans:
            del self._scans[scan_id]
            return True
        return False
