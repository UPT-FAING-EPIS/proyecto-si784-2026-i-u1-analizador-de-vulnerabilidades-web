# Vuln Scanner (Agent Skill)

Skill de Claude Code que escanea una URL en busca de vulnerabilidades usando el
Web Vulnerability Scanner. Ver `SKILL.md` para la definicion que usa Claude.

## Estado actual

Activa contra el backend de produccion: `https://vulnerabilidad-web.sytes.net/backend`.

- VPS: `149.34.48.176` (host `chambilla.sytes.net`), servidor compartido con otros
  proyectos.
- Servicio: `web-vulnerabilidad-backend.service` (systemd, `Restart=always`,
  `enabled` para arrancar en el boot). Antes corria como proceso suelto sin supervisor;
  se migro a systemd para que sobreviva caidas y reinicios del VPS.
- Codigo desplegado en `/var/www/html/web-vulnerabilidad/backend` en el VPS (venv en
  `.venv/`), escuchando en `127.0.0.1:8051`, expuesto afuera via Nginx + Certbot en
  `https://vulnerabilidad-web.sytes.net/backend/`.
- No se toco el resto del VPS: el proxy `/api/` -> `127.0.0.1:8001` que usa la IP pelada
  (`149.34.48.176`) sigue intacto, es una app distinta y no se modifico.
- Misma base de datos MySQL (`149.34.48.176:3307`) que el backend local, por eso la
  API key generada en local tambien sirve aqui.

Comandos utiles en el VPS (via `ssh root@149.34.48.176`):
```bash
systemctl status web-vulnerabilidad-backend.service
journalctl -u web-vulnerabilidad-backend.service -f
systemctl restart web-vulnerabilidad-backend.service
```

## Alternativa: correr contra un backend local

Solo si quieres probar cambios de codigo antes de desplegarlos:
```bash
bash .claude/skills/vuln-scanner/scripts/start-backend.sh
export WVS_API_URL="http://127.0.0.1:8000"
```

## Regenerar la API key (si expira o se revoca)

1. Login (contra produccion o local, cambia el host):
   ```bash
   curl -s -X POST https://vulnerabilidad-web.sytes.net/backend/api/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=<tu_email>&password=<tu_password>"
   ```
2. Crear key con el `access_token` de la respuesta:
   ```bash
   curl -s -X POST https://vulnerabilidad-web.sytes.net/backend/api/api-keys \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{"name": "claude-skill"}'
   ```
3. Reemplaza `WVS_API_KEY` en `.env.local` con el nuevo `api_key` de la respuesta.

## Prueba manual

```bash
python .claude/skills/vuln-scanner/scripts/scan.py https://ejemplo.com --depth 1
```

## Relacion con otras integraciones

Esta skill es independiente del servidor MCP en `integraciones/mcp-server/`
(pensado para Claude Desktop). Ambas usan la misma API `/api/integrations/*`
pero no comparten proceso ni configuracion.
