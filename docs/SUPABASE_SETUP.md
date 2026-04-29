# 🗄️ Guía de Configuración — Supabase

## ¿Por qué Supabase?

| | Sin Supabase | Con Supabase |
|---|---|---|
| Almacenamiento | RAM (se pierde al reiniciar) | PostgreSQL (persistente) |
| Historial | Solo en la sesión actual | Permanente |
| Costo | Gratis | **Gratis** (500MB) |
| Configuración | Ninguna | 10 minutos |

---

## PASO 1 — Crear cuenta en Supabase

1. Ve a https://supabase.com
2. Clic en **Start your project** → inicia sesión con GitHub
3. Clic en **New Project**
4. Configura:
   - **Nombre:** `vulnscan`
   - **Database Password:** elige una contraseña segura (guárdala)
   - **Region:** South America (São Paulo) — la más cercana a Perú
5. Clic en **Create new project** — espera ~2 minutos

---

## PASO 2 — Crear la tabla de escaneos

1. En tu proyecto de Supabase → menú izquierdo → **SQL Editor**
2. Clic en **New query**
3. Copia y pega el contenido del archivo `docs/supabase_setup.sql`
4. Clic en **Run** (o Ctrl+Enter)
5. Debes ver la lista de columnas de la tabla `scans`

---

## PASO 3 — Obtener las credenciales

1. En tu proyecto → **Settings** (ícono de engranaje) → **API**
2. Copia estos dos valores:

```
Project URL:   https://xxxxxxxxxxxx.supabase.co
               ↑ esto es tu SUPABASE_URL

anon public:   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
               ↑ esto es tu SUPABASE_KEY
```

> ⚠️ Usa la key **anon/public**, NO la service_role key.

---

## PASO 4A — Configurar en local (.env)

Crea un archivo `.env` en la carpeta `backend/`:

```env
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Instala python-dotenv:
```bash
pip install python-dotenv
```

Agrega al inicio de `backend/app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

Ejecuta el backend normalmente:
```bash
python app.py
```

Verás en la consola:
```
[DB] Conectando a Supabase: https://xxxx.supabase.co...
Supabase conectado correctamente ✅
```

---

## PASO 4B — Configurar en Azure App Service

1. Ve a tu App Service en Azure Portal
2. **Configuración** → **Configuración de la aplicación**
3. Agrega estas dos variables:

| Nombre | Valor |
|--------|-------|
| `SUPABASE_URL` | `https://xxxxxxxxxxxx.supabase.co` |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1...` |

4. Clic en **Guardar** → el servidor se reinicia automáticamente

---

## PASO 5 — Verificar que funciona

Haz un escaneo desde el frontend. Luego ve a Supabase:

1. **Table Editor** → tabla `scans`
2. Deberías ver el escaneo guardado con todos sus resultados

---

## ¿Qué pasa si no configuro Supabase?

**Nada.** Si las variables `SUPABASE_URL` y `SUPABASE_KEY` no están configuradas, el sistema usa automáticamente el almacenamiento en memoria como antes. Es completamente transparente.

```
Con variables → usa Supabase (persistente)
Sin variables → usa memoria RAM (temporal)
```

---

## Límites del plan gratuito de Supabase

| Recurso | Límite | ¿Suficiente? |
|---------|--------|--------------|
| Base de datos | 500 MB | ✅ ~10,000 escaneos |
| Ancho de banda | 5 GB/mes | ✅ Sí para académico |
| Proyectos | 2 | ✅ Sí |
| Pausa por inactividad | 7 días | ⚠️ Reactivar en dashboard |
| Filas | Ilimitadas | ✅ Sí |

> Si el proyecto se pausa, entra al dashboard de Supabase y clic en **Restore project**.
