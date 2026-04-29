# 🛠️ Guía de Servicios Externos — VulnScan
## Todo gratis, sin cargos ocultos

---

## RESUMEN — Qué vas a crear

| # | Servicio | Para qué | Tiempo | Costo |
|---|----------|----------|--------|-------|
| 1 | **Supabase** | Base de datos PostgreSQL | 10 min | $0 |
| 2 | **Sentry** | Captura errores automáticamente | 5 min | $0 |
| 3 | **UptimeRobot** | Te avisa si la app se cae | 3 min | $0 |

---

# SERVICIO 1 — Supabase (Base de datos)

## ¿Para qué sirve?
Sin Supabase los escaneos se pierden cuando reinicias el servidor.
Con Supabase quedan guardados para siempre en PostgreSQL.

## Plan gratuito incluye
- ✅ 500 MB de base de datos PostgreSQL
- ✅ 2 proyectos activos
- ✅ API REST automática
- ✅ Autenticación de usuarios
- ⚠️ Pausa si no hay actividad en 7 días (se reactiva gratis)

## Pasos para crear la cuenta

### Paso 1.1 — Registrarse
1. Ve a https://supabase.com
2. Clic en **"Start your project"**
3. Inicia sesión con tu cuenta de **GitHub** (más fácil)

### Paso 1.2 — Crear el proyecto
1. Clic en **"New project"**
2. Elige tu organización (tu usuario de GitHub)
3. Completa:
   - **Name:** `vulnscan`
   - **Database Password:** escribe una contraseña segura y **guárdala**
   - **Region:** `South America (São Paulo)` — la más cercana
4. Clic en **"Create new project"**
5. Espera 2 minutos mientras se crea

### Paso 1.3 — Crear la tabla
1. En el menú izquierdo → **"SQL Editor"**
2. Clic en **"New query"**
3. Pega este SQL y presiona **"Run"** (Ctrl+Enter):

```sql
CREATE TABLE IF NOT EXISTS scans (
    id            TEXT PRIMARY KEY,
    url           TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'pending',
    progress      INTEGER DEFAULT 0,
    current_task  TEXT,
    started_at    DOUBLE PRECISION,
    completed_at  DOUBLE PRECISION,
    results       TEXT,
    error         TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE scans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "allow_all_with_service_key"
  ON scans FOR ALL
  USING (true) WITH CHECK (true);
```

Debes ver: `Success. No rows returned`

### Paso 1.4 — Obtener las credenciales
1. Menú izquierdo → **"Settings"** (ícono de engranaje)
2. → **"API"**
3. Copia estos dos valores:

```
Project URL   →  https://XXXXXXXXXXXX.supabase.co
anon / public →  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Paso 1.5 — Configurar en el proyecto

**En local** — crea el archivo `backend/.env`:
```env
SUPABASE_URL=https://XXXXXXXXXXXX.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**En Azure** — App Service → Configuración → Nueva configuración:
- `SUPABASE_URL` = `https://XXXXXXXXXXXX.supabase.co`
- `SUPABASE_KEY` = `eyJhbGciOiJIUzI1...`

### Verificación
Reinicia el backend. En la consola verás:
```
[DB] Conectando a Supabase: https://xxxx.supabase.co...
Supabase conectado correctamente ✅
```

---

# SERVICIO 2 — Sentry (Monitoreo de errores)

## ¿Para qué sirve?
Cuando el backend da un error en Azure, Sentry te manda un email
con el stack trace completo, el archivo, la línea y el contexto.
Sin Sentry no te enteras de los errores hasta que alguien se queja.

## Plan gratuito incluye
- ✅ 5,000 errores por mes
- ✅ Alertas por email
- ✅ Stack traces completos
- ✅ Historial de 30 días
- ✅ 1 usuario (suficiente para proyecto académico)

## Pasos para crear la cuenta

### Paso 2.1 — Registrarse
1. Ve a https://sentry.io/signup/
2. Elige **"Continue with GitHub"**
3. Autoriza el acceso

### Paso 2.2 — Crear el proyecto
1. Clic en **"Create Project"**
2. Selecciona la plataforma: **"Flask"**
3. Alert frequency: **"Alert me on every new issue"**
4. Project name: `vulnscan-backend`
5. Clic en **"Create Project"**

### Paso 2.3 — Copiar el DSN
Después de crear el proyecto verás una pantalla con código.
Busca y copia la línea que empieza con `dsn=`:

```
dsn="https://XXXXXXXXXX@oXXXXXX.ingest.sentry.io/XXXXXXX"
```

Solo necesitas el valor entre comillas.

### Paso 2.4 — Configurar en el proyecto

**En local** — agrega a `backend/.env`:
```env
SENTRY_DSN=https://XXXXXXXXXX@oXXXXXX.ingest.sentry.io/XXXXXXX
```

**En Azure** — App Service → Configuración → Nueva configuración:
- `SENTRY_DSN` = `https://XXXXXXXXXX@oXXXXXX.ingest.sentry.io/XXXXXXX`

### Verificación
Reinicia el backend. En la consola verás:
```
[Sentry] ✅ Monitoreo de errores activado.
```

### ¿Cómo confirmar que funciona?
Abre en el navegador:
```
https://vulnscan-backend.azurewebsites.net/api/scan/id-que-no-existe
```
Luego entra a https://sentry.io → tu proyecto → verás el error registrado.

---

# SERVICIO 3 — UptimeRobot (Monitoreo de disponibilidad)

## ¿Para qué sirve?
UptimeRobot hace un ping a tu backend cada 5 minutos.
Si no responde, te manda un email de alerta inmediatamente.
También evita que Azure pause tu App Service por inactividad.

## Plan gratuito incluye
- ✅ 50 monitores
- ✅ Checks cada 5 minutos
- ✅ Alertas por email
- ✅ Página de status pública
- ✅ Historial de 7 días

## Pasos para crear la cuenta

### Paso 3.1 — Registrarse
1. Ve a https://uptimerobot.com
2. Clic en **"Register for FREE"**
3. Completa nombre, email y contraseña
4. Verifica tu email (te llega un correo)

### Paso 3.2 — Crear monitor del backend
1. Clic en **"+ Add New Monitor"**
2. Configura:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `VulnScan Backend`
   - **URL:** `https://vulnscan-backend.azurewebsites.net/ping`
   - **Monitoring Interval:** `5 minutes`
3. Clic en **"Create Monitor"**

### Paso 3.3 — Crear monitor del frontend
1. Clic en **"+ Add New Monitor"** otra vez
2. Configura:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `VulnScan Frontend`
   - **URL:** `https://TU-APP.azurestaticapps.net`
   - **Monitoring Interval:** `5 minutes`
3. Clic en **"Create Monitor"**

### Verificación
Después de 5 minutos verás ambos monitores en verde:
```
✅ VulnScan Backend  — Up  — Response: 200ms
✅ VulnScan Frontend — Up  — Response: 150ms
```

Si algo falla, recibirás un email como este:
```
Subject: [DOWN] VulnScan Backend is DOWN
Your monitor "VulnScan Backend" is DOWN.
URL: https://vulnscan-backend.azurewebsites.net/ping
```

---

# CONFIGURACIÓN FINAL — Variables de entorno completas

## En local (archivo backend/.env)
```env
# Supabase
SUPABASE_URL=https://XXXXXXXXXXXX.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Sentry
SENTRY_DSN=https://XXXXXXXXXX@oXXXXXX.ingest.sentry.io/XXXXXXX

# CORS
FRONTEND_URL=https://TU-APP.azurestaticapps.net

# Desactivar auth en desarrollo
AUTH_REQUIRED=false
```

## En Azure (App Service → Configuración)
| Variable | Valor |
|----------|-------|
| `SUPABASE_URL` | `https://XXXX.supabase.co` |
| `SUPABASE_KEY` | `eyJhbGci...` |
| `SENTRY_DSN` | `https://XXX@sentry.io/XXX` |
| `FRONTEND_URL` | `https://TU-APP.azurestaticapps.net` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |

---

# CHECKLIST FINAL

Antes de considerar el proyecto desplegado:

- [ ] Supabase: tabla `scans` creada
- [ ] Supabase: credenciales en Azure App Service
- [ ] Backend en Azure: `/health` responde 200
- [ ] Sentry: proyecto creado, DSN en Azure
- [ ] Sentry: recibir un error de prueba
- [ ] UptimeRobot: monitor del backend en verde
- [ ] UptimeRobot: monitor del frontend en verde
- [ ] Frontend: puede hacer un escaneo completo
- [ ] Historial: los escaneos aparecen en Supabase Table Editor
