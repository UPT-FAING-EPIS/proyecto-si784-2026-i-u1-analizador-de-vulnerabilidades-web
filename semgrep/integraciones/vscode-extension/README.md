# Web Vulnerability Scanner para VS Code

Escanea una URL en busca de vulnerabilidades web (XSS, SQLi, CSRF, cabeceras de
seguridad faltantes, open redirect, exposicion de informacion) sin salir de VS Code,
usando el backend de [Web Vulnerability Scanner](https://vulnerabilidad-web.sytes.net).

## Uso

1. `Ctrl+Shift+P` → **WVS: Registrarse y Configurar** → correo, usuario y contrasena.
   Crea tu cuenta (o inicia sesion si ya la tenias) y guarda tu API key automaticamente,
   sin salir de VS Code ni tocar ningun dashboard.
2. `Ctrl+Shift+P` → **WVS: Iniciar Escaneo** → introduce la URL objetivo.
3. Al terminar, aparece una notificacion con el resumen y el reporte completo
   (severidad, descripcion, recomendacion de cada hallazgo) en el panel de salida
   **"Web Vulnerability Scanner"** (`View > Output`).

## Alternativa: ya tengo una API Key

Si prefieres usar una key generada desde el dashboard web o por `POST /api/api-keys`,
usa **WVS: Configurar API Key** en vez del paso 1.

## Configuracion

| Setting | Default | Descripcion |
|---|---|---|
| `wvs.apiUrl` | `https://vulnerabilidad-web.sytes.net/backend` | URL base del backend del scanner |

Cambiala en `Settings > Extensions > Web Vulnerability Scanner` si usas tu propia
instancia (por ejemplo un backend local en `http://127.0.0.1:8000`).

## Solo escanea sitios que tengas autorizacion para auditar.
