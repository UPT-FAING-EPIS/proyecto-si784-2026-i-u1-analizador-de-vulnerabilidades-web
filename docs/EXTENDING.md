# Guía de Extensión de VulnScan

## Cómo agregar un nuevo módulo scanner

VulnScan está diseñado para ser 100% extensible. Agregar soporte para un nuevo tipo
de vulnerabilidad requiere modificar **exactamente 3 archivos**.

---

## Paso 1: Crear el scanner

Crea `backend/scanners/mi_scanner.py`:

```python
"""
Mi Scanner - Detecta [tipo de vulnerabilidad].
"""
import logging

logger = logging.getLogger(__name__)


class MiScanner:
    """
    Implementa la interfaz estándar de todos los scanners de VulnScan.
    El método scan() recibe el contexto del crawl y retorna hallazgos raw.
    """

    def __init__(self, http_client):
        self.http = http_client

    def scan(self, base_url: str, urls: list, forms: list,
             endpoints: list, **kwargs) -> list[dict]:
        """
        Ejecuta las pruebas de vulnerabilidad.

        Retorna una lista de dicts con al menos:
          - type: str         → identificador único del tipo ('mi_vuln')
          - subtype: str      → variante específica ('reflected', 'stored', etc.)
          - url: str          → URL donde se encontró
          - evidence: str     → extracto de la evidencia
          - severity_hint: str → 'critical'|'high'|'medium'|'low'|'info'

        Campos opcionales:
          - parameter: str    → parámetro vulnerable
          - payload: str      → payload utilizado
          - header: str       → cabecera involucrada
          - description: str  → descripción personalizada
        """
        findings = []

        for url in urls:
            # Tu lógica de detección aquí
            result = self._test_url(url)
            if result:
                findings.append(result)

        return findings

    def _test_url(self, url: str) -> dict | None:
        """Prueba una URL individual."""
        try:
            resp = self.http.get(url)
            if resp and self._is_vulnerable(resp):
                return {
                    'type':         'mi_vuln',
                    'subtype':      'variante_especifica',
                    'url':          url,
                    'evidence':     'Evidencia encontrada...',
                    'severity_hint': 'medium',
                }
        except Exception as e:
            logger.debug(f"Error en test: {e}")
        return None

    @staticmethod
    def _is_vulnerable(resp) -> bool:
        """Lógica de detección."""
        return False  # Implementar
```

---

## Paso 2: Registrar la regla OWASP

En `backend/rules/engine.py`, agrega al diccionario `VULNERABILITY_RULES`:

```python
VULNERABILITY_RULES['mi_vuln'] = {
    'name':        'Nombre de la Vulnerabilidad',
    'owasp':       'A0X:2021 – Categoría OWASP',
    'cwe':         'CWE-XXX',
    'severity':    'medium',          # default severity
    'cvss_range':  '4.0 – 7.5',
    'description': 'Descripción técnica de la vulnerabilidad...',
    'remediation': [
        'Recomendación de remediación 1.',
        'Recomendación de remediación 2.',
    ],
    'references': [
        'https://owasp.org/...',
        'https://cwe.mitre.org/data/definitions/XXX.html',
    ],
}
```

---

## Paso 3: Registrar en el Core Engine

En `backend/core/engine.py`, agrega una línea en el bloque de scanners:

```python
from scanners.mi_scanner import MiScanner

# ... dentro del método run(), junto a los demás scanners:
if self.options.get('scan_mi_vuln', True):
    scanners.append(('Mi Vulnerabilidad', MiScanner(self.http), 'mi_vuln'))
```

---

## Paso 4 (opcional): Agregar opción al frontend Angular

En `frontend/src/app/components/scanner/scanner.component.ts`:

```typescript
this.form = this.fb.group({
  // ... opciones existentes ...
  scan_mi_vuln: [true],   // ← agregar aquí
});
```

En `frontend/src/app/components/scanner/scanner.component.html`:

```html
<label class="check-label">
  <input type="checkbox" formControlName="scan_mi_vuln" /> Mi Vuln
</label>
```

En `frontend/src/app/services/scan.service.ts`, agregar al interface:

```typescript
export interface ScanOptions {
  // ... opciones existentes ...
  scan_mi_vuln?: boolean;
}
```

---

## Principios de diseño para scanners

### 1. Idempotencia
Los scanners no deben modificar el estado de la aplicación objetivo de forma permanente.

### 2. Conservadurismo
Preferir falsos negativos sobre falsos positivos. Solo reportar cuando la evidencia sea clara.

### 3. Manejo de errores
Usar `try/except` en todas las peticiones HTTP. Un scanner que falla no debe detener el pipeline.

### 4. Eficiencia
- Limitar el número de payloads por parámetro
- Detener la prueba de un parámetro tan pronto se confirme la vulnerabilidad
- Respetar el timeout configurado por el usuario

### 5. Evidencia clara
El campo `evidence` debe contener suficiente contexto para que un analista pueda
verificar manualmente el hallazgo sin re-ejecutar el escaneo.

---

## Scanners disponibles

| Archivo | Tipo | OWASP | Estado |
|---------|------|-------|--------|
| `xss_scanner.py` | `xss` | A03:2021 | ✅ Activo |
| `sqli_scanner.py` | `sqli` | A03:2021 | ✅ Activo |
| `header_scanner.py` | `misconfiguration` | A05:2021 | ✅ Activo |
| `csrf_scanner.py` | `csrf` | A01:2021 | ✅ Activo |
| `redirect_scanner.py` | `redirect` | A01:2021 | ✅ Activo |
| `info_disclosure_scanner.py` | `info_disclosure` | A05:2021 | ✅ Activo |

---

## Próximos módulos sugeridos

- `ssrf_scanner.py` — Server-Side Request Forgery (CWE-918)
- `xxe_scanner.py` — XML External Entity (CWE-611)  
- `idor_scanner.py` — Insecure Direct Object Reference (CWE-639)
- `auth_scanner.py` — Autenticación débil / credenciales por defecto (CWE-287)
- `cors_scanner.py` — CORS mal configurado (CWE-942)
