---
name: vuln-scanner
description: Escanea una URL en busca de vulnerabilidades web (XSS, SQLi, CSRF, cabeceras faltantes, open redirect, exposicion de informacion) usando el backend Web Vulnerability Scanner. Usar cuando el usuario pida escanear, auditar o analizar la seguridad de un sitio/URL, o pregunte por vulnerabilidades de una pagina web.
---

# Vuln Scanner

Lanza un escaneo de seguridad contra una URL objetivo usando la API de integraciones del
Web Vulnerability Scanner (`/api/integrations/scans`) y devuelve un reporte legible.

## Requisitos previos

El script lee `WVS_API_KEY` y `WVS_API_URL` en este orden: variables ya exportadas en la
sesion, o si no existen, el archivo `.claude/skills/vuln-scanner/.env.local` (no
versionado, ver `.gitignore` de la skill). Ya esta configurado y apunta al backend de
produccion desplegado en `https://vulnerabilidad-web.sytes.net/backend`, corriendo como
servicio systemd (`web-vulnerabilidad-backend.service`, `Restart=always`) en el VPS
149.34.48.176 — no requiere que el usuario tenga nada corriendo localmente.

- `WVS_API_KEY` (obligatoria): API key generada con `POST /api/api-keys` autenticado con
  tu usuario. Ya hay una configurada en `.env.local`.
- `WVS_API_URL` (opcional): URL base del backend. Por defecto usa el backend de
  produccion. Sobreescribir solo para pruebas contra un backend local
  (`http://127.0.0.1:8000`, ver `scripts/start-backend.sh`).

Si `WVS_API_KEY` no esta definida despues de intentar cargar `.env.local`, pide al
usuario que la configure (no existe ningun flujo de login automatico en esta skill: la
key se genera manualmente una sola vez y se reutiliza).

## Uso

Ejecutar el script con la URL objetivo:

```bash
python .claude/skills/vuln-scanner/scripts/scan.py <target_url> [--depth N] [--modules m1,m2,...] [--timeout N]
```

- `target_url` (obligatorio): URL completa a escanear, ej. `https://ejemplo.com`.
- `--depth`: profundidad de rastreo, 0-3 (default 1).
- `--modules`: lista separada por comas de modulos a ejecutar. Por defecto:
  `xss,sqli,headers,csrf,open_redirect,info_disclosure`.
- `--timeout`: timeout por request del scanner en segundos, 3-30 (default 10).

El script crea el escaneo, hace polling hasta que termina (`completed` o `failed`) y
finalmente imprime en stdout un reporte en Markdown con severidad, descripcion y
recomendacion de cada vulnerabilidad encontrada. Ese texto se puede mostrar al usuario
tal cual o resumirse.

## Notas

- Un escaneo puede tardar desde varios segundos hasta un par de minutos segun la
  profundidad y los modulos seleccionados; el script hace polling cada 3s sin limite de
  tiempo, informar al usuario que puede tomar un momento.
- Si el backend responde 401/403, la API key es invalida o fue revocada: pedir al
  usuario que genere una nueva.
- Solo se debe escanear URLs que el usuario tenga autorizacion para auditar.
