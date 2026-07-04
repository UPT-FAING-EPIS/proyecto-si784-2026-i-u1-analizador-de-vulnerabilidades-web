# Guía Paso a Paso: Skill para Claude (Servidor MCP)

El Model Context Protocol (MCP) permite que asistentes como Claude interactúen con herramientas locales de tu computadora. Hemos creado un servidor MCP en Python que conecta Claude con tu Web Vulnerability Scanner.

## 1. Requisitos previos
- Tener **Python 3.10 o superior** instalado.
- Tener **Claude Desktop** instalado en tu computadora.
- El backend del escáner (FastAPI) debe estar corriendo en `http://127.0.0.1:8000`.

## 2. Preparar el servidor MCP local
1. Abre tu terminal y ve a la carpeta del servidor MCP:
   ```bash
   cd integraciones/mcp-server
   ```
2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Mac/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

## 3. Configurar Claude Desktop
Para que Claude sepa que existe tu escáner de vulnerabilidades, debes modificar su archivo de configuración.

1. Localiza el archivo de configuración de Claude Desktop:
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Abre ese archivo en VS Code u otro editor. Si no existe, créalo. Debe tener esta estructura:

```json
{
  "mcpServers": {
    "web-vulnerability-scanner": {
      "command": "C:\\ruta\\absoluta\\a\\tu\\python.exe",
      "args": [
        "C:\\ruta\\absoluta\\a\\integraciones\\mcp-server\\server.py"
      ],
      "env": {
        "WVS_API_URL": "http://127.0.0.1:8000",
        "WVS_API_KEY": "pega_aqui_tu_api_key_del_escaner"
      }
    }
  }
}
```
*Asegúrate de reemplazar las rutas por las reales en tu PC (si estás en Windows usa doble barra `\\` en las rutas) y coloca tu API Key real.*

## 4. Probar la Integración
1. **Reinicia completamente Claude Desktop** (ciérralo desde la bandeja del sistema/tray icon y vuélvelo a abrir).
2. Abre un nuevo chat en Claude.
3. Haz clic en el icono del "martillo" (Tools) que aparece en la interfaz. Deberías ver que tu herramienta `scan_vulnerabilities` está disponible.
4. Escríbele a Claude: *"Por favor, usa la herramienta de escaneo para analizar la seguridad de la página web http://ejemplo.com y resúmeme los resultados."*
5. Claude llamará a tu script de Python de fondo, el script hará el Polling a FastAPI, y Claude te explicará las vulnerabilidades detectadas de forma amigable.
