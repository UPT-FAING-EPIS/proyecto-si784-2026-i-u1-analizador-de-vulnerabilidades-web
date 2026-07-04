# Guía Paso a Paso: Extensión de Visual Studio Code

Esta guía detalla los pasos para probar, ejecutar y publicar la extensión de VS Code que hemos creado para el Web Vulnerability Scanner.

## 1. Requisitos previos
- Tener **Node.js** instalado (versión 16 o superior).
- La extensión apunta por defecto al backend de producción
  (`https://vulnerabilidad-web.sytes.net/backend`), no necesitas nada corriendo
  localmente. Solo cambia `wvs.apiUrl` en la configuración si quieres usar un backend
  local.
- Tener una **API Key** generada desde el panel web de tu escáner.

## 2. Preparar el entorno
1. Abre tu terminal y navega a la carpeta de la extensión:
   ```bash
   cd integraciones/vscode-extension
   ```
2. Instala las dependencias necesarias:
   ```bash
   npm install
   ```

## 3. Probar la extensión localmente
1. Abre la carpeta `integraciones/vscode-extension` en una nueva ventana de VS Code.
2. Presiona la tecla **F5** (o ve al menú Run > Start Debugging).
3. Se abrirá una **nueva ventana de VS Code** con el título "[Extension Development Host]". Esta es tu ventana de pruebas con la extensión cargada.
4. En esta nueva ventana, presiona `Ctrl+Shift+P` (o `Cmd+Shift+P` en Mac) para abrir la paleta de comandos.
5. Escribe y selecciona: **`WVS: Configurar API Key`**. Pega la API Key que generaste en el panel de tu escáner.
6. Vuelve a abrir la paleta de comandos y selecciona: **`WVS: Iniciar Escaneo`**.
7. Introduce la URL que quieres analizar (ej. `http://localhost:3000`).
8. Verás una notificación en la esquina inferior derecha mostrando el progreso. Al terminar, te notificará cuántas vulnerabilidades se encontraron.

## 4. Empaquetar para producción
Si quieres compartir esta extensión con tu equipo o instalarla permanentemente:
1. Instala la herramienta de empaquetado de VS Code:
   ```bash
   npm install -g @vscode/vsce
   ```
2. Ejecuta el comando para crear el archivo instalable:
   ```bash
   vsce package
   ```
3. Esto generará un archivo `wvs-vscode-0.0.1.vsix` (ya generado y probado en este repo).
4. En cualquier VS Code, ve a la pestaña de Extensiones, haz clic en el menú de los 3 puntos (...) y selecciona **"Install from VSIX..."**, luego selecciona tu archivo.

## 5. Publicarla en el Marketplace (para que se instale buscando el nombre)
Ver [`4-Publicar-Marketplace.md`](4-Publicar-Marketplace.md) — requiere crear cuenta de
publisher en Azure DevOps/Marketplace (no se puede hacer por ti).
