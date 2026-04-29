"""
db/__init__.py
Exporta get_store() que devuelve el store activo según configuración.
Si SUPABASE_URL y SUPABASE_KEY están en el entorno → usa Supabase.
Si no → usa el store en memoria (comportamiento original).
"""

import os
from .memory_store import MemoryStore
from .supabase_store import SupabaseStore

_store = None


def get_store():
    """
    Singleton: devuelve siempre la misma instancia del store.
    Se configura automáticamente según las variables de entorno.
    """
    global _store
    if _store is None:
        url = os.environ.get('SUPABASE_URL', '').strip()
        key = os.environ.get('SUPABASE_KEY', '').strip()

        if url and key:
            print(f"[DB] Conectando a Supabase: {url[:40]}...")
            _store = SupabaseStore(url, key)
        else:
            print("[DB] Usando almacenamiento en memoria (sin Supabase)")
            _store = MemoryStore()

    return _store
