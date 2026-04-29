# 🚀 Guía de Despliegue en Azure — VulnScan

## Arquitectura en Azure

```
Internet
   │
   ├── Frontend → Azure Static Web Apps (GRATIS)
   │              https://vulnscan.azurestaticapps.net
   │
   └── Backend  → Azure App Service F1 (GRATIS con créditos)
                  https://vulnscan-backend.azurewebsites.net
```

---

## PASO 1 — Subir código a GitHub

```bash
# En la carpeta del proyecto
cd vulnscan-fixed3

git init
git add .
git commit -m "VulnScan v1.0.0 - initial commit"

# Crear repo en github.com, luego:
git remote add origin https://github.com/TU_USUARIO/vulnscan.git
git push -u origin main
```

---

## PASO 2 — Desplegar el Backend (Azure App Service)

### 2.1 Crear el App Service

1. Ve a https://portal.azure.com
2. Busca **"App Services"** → clic en **+ Crear**
3. Configura:

| Campo | Valor |
|-------|-------|
| Suscripción | Tu suscripción con créditos |
| Grupo de recursos | Crear nuevo → `vulnscan-rg` |
| Nombre | `vulnscan-backend` (será vulnscan-backend.azurewebsites.net) |
| Publicar | Código |
| Pila en tiempo de ejecución | **Python 3.11** |
| Sistema operativo | Linux |
| Región | East US (o la más cercana) |
| Plan de App Service | F1 Gratis |

4. Clic en **Revisar y crear** → **Crear**

### 2.2 Configurar el comando de inicio

1. En tu App Service → **Configuración** → **Configuración general**
2. En **Comando de inicio** escribe:
```
gunicorn --bind=0.0.0.0:8000 --timeout=120 --workers=2 "app:create_app()"
```
3. Clic en **Guardar**

### 2.3 Conectar GitHub para despliegue automático

1. En tu App Service → **Centro de implementación**
2. Fuente: **GitHub**
3. Autoriza el acceso a tu cuenta
4. Selecciona:
   - Organización: tu usuario
   - Repositorio: `vulnscan`
   - Rama: `main`
   - **Carpeta de la aplicación**: `backend`  ← importante
5. Clic en **Guardar**

Azure creará automáticamente el workflow en `.github/workflows/`

### 2.4 Agregar variable de entorno

1. App Service → **Configuración** → **Configuración de la aplicación**
2. Clic en **+ Nueva configuración de la aplicación**:

| Nombre | Valor |
|--------|-------|
| `FRONTEND_URL` | `https://TU-APP.azurestaticapps.net` (lo sabrás en el paso 3) |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |

3. Clic en **Guardar**

### 2.5 Verificar que funciona

Abre en el navegador:
```
https://vulnscan-backend.azurewebsites.net/health
```
Debe responder:
```json
{"status": "ok", "service": "vulnscan-backend"}
```

---

## PASO 3 — Desplegar el Frontend (Azure Static Web Apps)

### 3.1 Actualizar la URL del backend

Edita el archivo `frontend/src/environments/environment.prod.ts`:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://vulnscan-backend.azurewebsites.net/api',
};
```

Haz commit y push:
```bash
git add .
git commit -m "chore: update backend URL for production"
git push
```

### 3.2 Crear el Static Web App

1. En Azure Portal → busca **"Static Web Apps"** → **+ Crear**
2. Configura:

| Campo | Valor |
|-------|-------|
| Grupo de recursos | `vulnscan-rg` (el mismo) |
| Nombre | `vulnscan` |
| Plan de hospedaje | **Gratis** |
| Región | East US 2 |
| Origen de implementación | **GitHub** |

3. Conecta GitHub:
   - Organización: tu usuario
   - Repositorio: `vulnscan`
   - Rama: `main`

4. Detalles de compilación:
   - Valores preestablecidos: **Angular**
   - Ubicación de la aplicación: `/frontend`
   - Ubicación de salida: `dist/vulnscan-frontend/browser`

5. Clic en **Revisar y crear** → **Crear**

### 3.3 Verificar el despliegue

1. En tu Static Web App → **URL** (algo como `https://xxx.azurestaticapps.net`)
2. Abre esa URL en el navegador
3. Deberías ver VulnScan funcionando

### 3.4 Actualizar FRONTEND_URL en el backend

Ahora que tienes la URL del frontend, ve a tu App Service y actualiza:
- `FRONTEND_URL` = `https://xxx.azurestaticapps.net`

---

## PASO 4 — Configurar GitHub Secrets (para CI/CD)

En tu repositorio de GitHub → **Settings** → **Secrets and variables** → **Actions**:

| Secret | Cómo obtenerlo |
|--------|----------------|
| `AZURE_BACKEND_APP_NAME` | El nombre que pusiste: `vulnscan-backend` |
| `AZURE_BACKEND_PUBLISH_PROFILE` | App Service → **Obtener perfil de publicación** (descarga el XML y pégalo completo) |
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Static Web App → **Administrar token de implementación** |

---

## PASO 5 — Verificación final

| Prueba | URL | Resultado esperado |
|--------|-----|-------------------|
| Backend health | `https://vulnscan-backend.azurewebsites.net/health` | `{"status":"ok"}` |
| API scans | `https://vulnscan-backend.azurewebsites.net/api/scans` | `[]` |
| Frontend | `https://xxx.azurestaticapps.net` | Interfaz VulnScan |
| Escaneo completo | Ingresar URL en el frontend | Resultados de vulnerabilidades |

---

## Solución de problemas comunes

### Error 500 en el backend
```bash
# Ver logs en Azure
App Service → Herramientas de desarrollo → Consola
cat /home/LogFiles/kudu/trace/*.xml
```

### CORS error en el frontend
Verifica que `FRONTEND_URL` en el App Service coincida exactamente con la URL de tu Static Web App.

### El build de Angular falla
Verifica en GitHub → Actions → el workflow fallido → ver logs.
El error más común es que `output_location` no coincida con la salida real de `ng build`.

### Timeout en escaneos
En App Service → Configuración → agrega:
- `WEBSITES_CONTAINER_START_TIME_LIMIT` = `1800`

---

## Costos estimados

| Servicio | Plan | Costo |
|----------|------|-------|
| App Service (Backend) | F1 Free | **$0/mes** |
| Static Web Apps (Frontend) | Free | **$0/mes** |
| **Total** | | **$0/mes** |

Con el plan F1 gratuito tienes 60 minutos de CPU/día y 1GB RAM. Es suficiente para demostraciones y pruebas académicas.
