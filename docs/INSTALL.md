# Instalación y Troubleshooting

## Requisitos del sistema

| Componente | Versión mínima | Verificar con |
|-----------|---------------|---------------|
| Python    | 3.10+         | `python3 --version` |
| Node.js   | 18+           | `node --version` |
| npm       | 9+            | `npm --version` |
| Docker    | 24+           | `docker --version` |
| Docker Compose | 2.20+   | `docker compose version` |

---

## Opción A: Ejecutar con Docker (recomendado)

```bash
# Clonar el proyecto
git clone https://github.com/tu-usuario/vulnscan.git
cd vulnscan

# Levantar todos los servicios
docker-compose up --build

# Verificar que todo está corriendo
docker-compose ps
```

Acceso:
- **Frontend:** http://localhost:4200
- **Backend API:** http://localhost:5000
- **App vulnerable:** http://localhost:8080

Para detener:
```bash
docker-compose down
```

---

## Opción B: Ejecutar localmente (desarrollo)

### Backend Flask

```bash
cd backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate.bat     # Windows CMD
# venv\Scripts\Activate.ps1     # Windows PowerShell

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
python app.py
# → API disponible en http://localhost:5000
```

### App vulnerable (para pruebas)

```bash
cd docker
pip install flask
python vulnapp.py
# → App disponible en http://localhost:8080
```

### Frontend Angular

```bash
cd frontend

# Instalar dependencias de Node.js
npm install

# Iniciar servidor de desarrollo (con proxy al backend)
npm start
# → Frontend en http://localhost:4200
# → Las llamadas a /api/* son proxeadas a http://localhost:5000
```

---

## Opción C: Script de inicio rápido

```bash
chmod +x start.sh
./start.sh
```

Esto levanta el backend y la app vulnerable automáticamente, e indica cómo iniciar el frontend en otra terminal.

---

## Ejecutar las pruebas

```bash
cd backend

# Activar entorno virtual (si no está activo)
source venv/bin/activate

# Instalar pytest (si no está instalado)
pip install pytest

# Ejecutar todas las pruebas
python -m pytest tests/ -v

# Con cobertura de código
pip install pytest-cov
python -m pytest tests/ --cov=. --cov-report=html
# Reporte en htmlcov/index.html
```

---

## Troubleshooting

### Error: `No module named flask`
```bash
# Asegurarse de tener el venv activado
source venv/bin/activate
pip install -r requirements.txt
```

### Error: `CORS` bloqueado en el browser
El backend incluye `flask-cors` configurado para aceptar cualquier origen.
Si persiste, verificar que el backend esté corriendo en el puerto 5000:
```bash
curl http://localhost:5000/health
```

### Error de Angular: `Cannot find module '@angular/core'`
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Docker: `port is already allocated`
Otro proceso usa el puerto. Cambiar los puertos en `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"  # backend en 5001
```
Y actualizar `frontend/src/environments/environment.ts`:
```typescript
apiUrl: 'http://localhost:5001/api'
```

### El escaneo no encuentra vulnerabilidades
1. Verificar que la URL objetivo sea accesible desde el backend:
   ```bash
   curl http://localhost:8080
   ```
2. Aumentar la profundidad del crawler (max_depth: 3)
3. Verificar los logs del backend en la terminal donde corre Flask

### Timeout durante el escaneo
Aumentar el timeout en la configuración del escaneo (10s → 20s) si el objetivo es lento.

---

## Variables de entorno (opcional)

Crea `backend/.env` para configurar el entorno:

```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=tu-clave-secreta
MAX_SCAN_DEPTH=3
DEFAULT_TIMEOUT=10
```

Carga automática con `python-dotenv` (agregar a `requirements.txt`).
