# Funcionamiento de API Keys e integracion con sistemas externos

Este documento explica como otros sistemas pueden consumir los servicios del Web Vulnerability Scanner usando API Keys.

La API Key identifica al usuario propietario de la clave. Todas las consultas hechas con esa clave trabajan solamente sobre los escaneos, estadisticas y reportes del usuario que la genero.

## URL base

En desarrollo local:

```text
http://127.0.0.1:8000
```

Si el backend se despliega en otro servidor, se debe reemplazar esa URL por el dominio o IP real del backend FastAPI.

Ejemplo:

```text
https://scanner.mi-dominio.com
```

## Resumen del flujo

1. El usuario inicia sesion en el sistema web.
2. Entra al panel `API Keys`.
3. Genera una API Key con un nombre y una expiracion.
4. El sistema muestra la API Key completa una sola vez.
5. El usuario copia esa API Key y la configura en el sistema externo.
6. El sistema externo llama a los endpoints `/api/integrations/*`.
7. El backend valida la API Key, identifica al usuario propietario y responde solo con sus datos.

## Como se guarda una API Key

Por seguridad, el backend no guarda la API Key completa.

La tabla `api_keys` guarda:

| Campo | Descripcion |
| --- | --- |
| `id` | Identificador interno de la API Key. |
| `user_id` | Usuario propietario de la API Key. |
| `name` | Nombre descriptivo asignado por el usuario. |
| `key_prefix` | Primeros caracteres visibles de la clave, utiles para reconocerla. |
| `key_hash` | Hash SHA-256 de la API Key completa. |
| `scopes` | Permisos asignados a la clave. Actualmente: `scans:read`, `scans:write`, `stats:read`. |
| `is_active` | Indica si la clave esta activa. |
| `created_at` | Fecha de creacion. |
| `last_used_at` | Ultimo uso correcto de la clave. |
| `expires_at` | Fecha de expiracion, si aplica. |
| `revoked_at` | Fecha de revocacion, si aplica. |

Importante: si el usuario pierde la API Key completa, no se puede recuperar. Debe crear una nueva.

## Formas de enviar la API Key

Los endpoints de integracion aceptan cualquiera de estas dos formas:

### Opcion 1: header X-API-Key

```http
X-API-Key: TU_API_KEY
```

Ejemplo:

```bash
curl -H "X-API-Key: TU_API_KEY" \
  http://127.0.0.1:8000/api/integrations/stats
```

### Opcion 2: Authorization Bearer

```http
Authorization: Bearer TU_API_KEY
```

Ejemplo:

```bash
curl -H "Authorization: Bearer TU_API_KEY" \
  http://127.0.0.1:8000/api/integrations/scans
```

Tambien se acepta:

```http
Authorization: ApiKey TU_API_KEY
```

## Endpoints para sistemas externos

Estos endpoints son los que deben usar los sistemas de otros equipos. Se autentican con API Key.

### GET /api/integrations/catalog

Devuelve informacion publica sobre los endpoints disponibles.

No requiere API Key.

```bash
curl http://127.0.0.1:8000/api/integrations/catalog
```

Respuesta:

```json
{
  "service": "Web Vulnerability Scanner Integration API",
  "authentication": "Enviar X-API-Key: <api_key> o Authorization: Bearer <api_key>",
  "endpoints": [
    {
      "method": "GET",
      "path": "/api/integrations/me",
      "description": "Identifica al propietario de la API key"
    },
    {
      "method": "GET",
      "path": "/api/integrations/stats",
      "description": "Resumen de escaneos y hallazgos del usuario"
    },
    {
      "method": "GET",
      "path": "/api/integrations/scans",
      "description": "Lista los escaneos del usuario"
    },
    {
      "method": "POST",
      "path": "/api/integrations/scans",
      "description": "Crea un escaneo asincrono"
    },
    {
      "method": "GET",
      "path": "/api/integrations/scans/{scan_id}",
      "description": "Obtiene un reporte de escaneo"
    }
  ]
}
```

### GET /api/integrations/me

Identifica al usuario propietario de la API Key.

```bash
curl http://127.0.0.1:8000/api/integrations/me \
  -H "X-API-Key: TU_API_KEY"
```

Respuesta:

```json
{
  "id": 1,
  "email": "usuario@correo.com",
  "username": "Usuario",
  "is_admin": false,
  "created_at": "2026-06-09T00:00:00"
}
```

Uso recomendado: que el sistema externo valide al guardar la API Key que la clave pertenece a un usuario valido.

### GET /api/integrations/stats

Devuelve el resumen de escaneos y vulnerabilidades del usuario propietario de la API Key.

```bash
curl http://127.0.0.1:8000/api/integrations/stats \
  -H "X-API-Key: TU_API_KEY"
```

Respuesta:

```json
{
  "total_scans": 4,
  "completed_scans": 3,
  "running_scans": 1,
  "total_vulnerabilities": 12,
  "by_severity": {
    "high": 2,
    "medium": 5,
    "low": 5
  },
  "by_module": {
    "xss": 4,
    "sqli": 2,
    "headers": 6
  }
}
```

### GET /api/integrations/scans

Lista los ultimos 50 escaneos del usuario propietario de la API Key.

```bash
curl http://127.0.0.1:8000/api/integrations/scans \
  -H "X-API-Key: TU_API_KEY"
```

Respuesta:

```json
[
  {
    "id": 25,
    "target_url": "https://example.com/",
    "status": "completed",
    "modules": ["xss", "sqli", "headers"],
    "depth": 1,
    "timeout": 10,
    "progress": 100,
    "risk_score": 65,
    "ai_summary": "Resumen generado por IA...",
    "error_message": null,
    "created_at": "2026-06-09T00:00:00",
    "started_at": "2026-06-09T00:00:01",
    "completed_at": "2026-06-09T00:00:15",
    "vulnerability_count": 3
  }
]
```

Estados posibles de un escaneo:

| Estado | Significado |
| --- | --- |
| `pending` | El escaneo fue creado y esta esperando iniciar. |
| `running` | El escaneo esta ejecutandose. |
| `completed` | El escaneo termino correctamente. |
| `failed` | El escaneo fallo. Revisar `error_message`. |

### POST /api/integrations/scans

Crea un nuevo escaneo para el usuario propietario de la API Key.

El escaneo se ejecuta en segundo plano. La respuesta llega rapido con estado `pending`; luego el sistema externo debe consultar el detalle usando `GET /api/integrations/scans/{scan_id}`.

Body:

```json
{
  "target_url": "https://example.com/",
  "modules": ["xss", "sqli", "headers", "csrf", "open_redirect", "info_disclosure"],
  "depth": 1,
  "timeout": 10
}
```

Reglas:

| Campo | Tipo | Reglas |
| --- | --- | --- |
| `target_url` | URL | Debe ser una URL valida con `http` o `https`. |
| `modules` | array de string | Opcional. Si no se envia, usa todos los modulos disponibles. |
| `depth` | number | Entre 0 y 3. Valor por defecto: 1. |
| `timeout` | number | Entre 3 y 30 segundos. Valor por defecto: 10. |

Modulos disponibles:

```json
["xss", "sqli", "headers", "csrf", "open_redirect", "info_disclosure"]
```

Ejemplo:

```bash
curl -X POST http://127.0.0.1:8000/api/integrations/scans \
  -H "X-API-Key: TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/",
    "modules": ["xss", "sqli", "headers"],
    "depth": 1,
    "timeout": 10
  }'
```

Respuesta `201 Created`:

```json
{
  "id": 26,
  "target_url": "https://example.com/",
  "status": "pending",
  "modules": ["xss", "sqli", "headers"],
  "depth": 1,
  "timeout": 10,
  "progress": 0,
  "risk_score": 0,
  "ai_summary": null,
  "error_message": null,
  "created_at": "2026-06-09T00:00:00",
  "started_at": null,
  "completed_at": null,
  "vulnerability_count": 0
}
```

### GET /api/integrations/scans/{scan_id}

Obtiene el detalle de un escaneo especifico y sus vulnerabilidades.

```bash
curl http://127.0.0.1:8000/api/integrations/scans/26 \
  -H "X-API-Key: TU_API_KEY"
```

Respuesta:

```json
{
  "id": 26,
  "target_url": "https://example.com/",
  "status": "completed",
  "modules": ["xss", "sqli", "headers"],
  "depth": 1,
  "timeout": 10,
  "progress": 100,
  "risk_score": 65,
  "ai_summary": "Resumen generado por IA...",
  "error_message": null,
  "created_at": "2026-06-09T00:00:00",
  "started_at": "2026-06-09T00:00:01",
  "completed_at": "2026-06-09T00:00:15",
  "vulnerability_count": 1,
  "vulnerabilities": [
    {
      "id": 90,
      "module": "headers",
      "severity": "medium",
      "title": "Cabecera de seguridad faltante",
      "description": "El sitio no presenta una cabecera de seguridad recomendada.",
      "evidence": "Missing header: Content-Security-Policy",
      "remediation": "Configurar las cabeceras HTTP de seguridad recomendadas.",
      "url": "https://example.com/",
      "parameter": null,
      "created_at": "2026-06-09T00:00:15"
    }
  ]
}
```

Si el escaneo no existe o pertenece a otro usuario, responde:

```json
{
  "detail": "Escaneo no encontrado"
}
```

con codigo HTTP `404`.

## Polling recomendado para escaneos

Como los escaneos son asincronos, el sistema externo debe consultar el detalle hasta que el estado sea `completed` o `failed`.

Flujo:

1. Crear escaneo con `POST /api/integrations/scans`.
2. Guardar el `id` recibido.
3. Consultar cada 3 a 5 segundos `GET /api/integrations/scans/{id}`.
4. Detener el polling cuando `status` sea `completed` o `failed`.
5. Leer `vulnerabilities`, `risk_score`, `ai_summary` y `error_message`.

Ejemplo simple:

```bash
SCAN_ID=26

curl http://127.0.0.1:8000/api/integrations/scans/$SCAN_ID \
  -H "X-API-Key: TU_API_KEY"
```

## Ejemplo de integracion en JavaScript

```js
const API_BASE_URL = "http://127.0.0.1:8000";
const API_KEY = process.env.WVS_API_KEY;

async function requestScanner(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...(options.headers || {})
    }
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Error HTTP ${response.status}`);
  }

  return response.json();
}

async function createScan(targetUrl) {
  return requestScanner("/api/integrations/scans", {
    method: "POST",
    body: JSON.stringify({
      target_url: targetUrl,
      modules: ["xss", "sqli", "headers"],
      depth: 1,
      timeout: 10
    })
  });
}

async function getStats() {
  return requestScanner("/api/integrations/stats");
}
```

## Ejemplo de integracion en Python

```python
import os
import time
import requests

API_BASE_URL = "http://127.0.0.1:8000"
API_KEY = os.environ["WVS_API_KEY"]

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}

response = requests.post(
    f"{API_BASE_URL}/api/integrations/scans",
    headers=headers,
    json={
        "target_url": "https://example.com/",
        "modules": ["xss", "sqli", "headers"],
        "depth": 1,
        "timeout": 10,
    },
    timeout=30,
)
response.raise_for_status()
scan = response.json()

scan_id = scan["id"]

while True:
    detail_response = requests.get(
        f"{API_BASE_URL}/api/integrations/scans/{scan_id}",
        headers=headers,
        timeout=30,
    )
    detail_response.raise_for_status()
    detail = detail_response.json()

    if detail["status"] in {"completed", "failed"}:
        print(detail)
        break

    time.sleep(5)
```

## Codigos de respuesta comunes

| Codigo | Causa |
| --- | --- |
| `200 OK` | Consulta exitosa. |
| `201 Created` | Recurso creado, por ejemplo una API Key o un escaneo. |
| `400 Bad Request` | Se alcanzo el limite de 10 API Keys activas. |
| `401 Unauthorized` | Falta API Key, API Key invalida, revocada o expirada. |
| `403 Forbidden` | El JWT no tiene permisos suficientes para endpoints administrativos. |
| `404 Not Found` | El recurso no existe o no pertenece al usuario autenticado. |
| `409 Conflict` | El correo ya existe durante registro. |
| `422 Unprocessable Entity` | El body enviado no cumple las validaciones. |
| `500 Internal Server Error` | Error interno inesperado. |

## Errores de API Key

### Falta API Key

```json
{
  "detail": "API key requerida. Usa X-API-Key o Authorization: Bearer <api_key>."
}
```

HTTP `401`.

### API Key invalida o revocada

```json
{
  "detail": "API key invalida o revocada"
}
```

HTTP `401`.

### API Key expirada

```json
{
  "detail": "API key expirada"
}
```

HTTP `401`.

## Recomendaciones para otros sistemas

- Guardar la API Key en variables de entorno o en un gestor de secretos.
- No guardar la API Key en el frontend publico.
- No imprimir la API Key en logs.
- Validar la clave con `GET /api/integrations/me` al configurar la integracion.
- Usar HTTPS en produccion.
- Implementar reintentos moderados solo para errores temporales de red.
- No repetir automaticamente peticiones `POST /api/integrations/scans` sin control, porque cada llamada crea un escaneo nuevo.
- Revocar claves que ya no se usen.
- Crear una clave diferente por cada sistema externo para poder revocarlas individualmente.

## Prueba rapida de integracion

Con una API Key ya generada:

```bash
export WVS_API_KEY="TU_API_KEY"
export WVS_BASE_URL="http://127.0.0.1:8000"

curl "$WVS_BASE_URL/api/integrations/me" \
  -H "X-API-Key: $WVS_API_KEY"

curl "$WVS_BASE_URL/api/integrations/stats" \
  -H "X-API-Key: $WVS_API_KEY"

curl "$WVS_BASE_URL/api/integrations/scans" \
  -H "X-API-Key: $WVS_API_KEY"
```

Si estas tres consultas responden `200 OK`, el sistema externo ya puede consumir nuestros servicios.
