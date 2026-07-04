# Guía Paso a Paso: Publicar la extensión en el VS Code Marketplace

Las Fases 1-3 (scaffold, ajustes, empaquetado `.vsix`) ya están listas en
`integraciones/vscode-extension/`. Esta guía cubre solo la Fase 4: publicarla para que
cualquiera la instale buscando "Web Vulnerability Scanner" dentro de VS Code.

## 1. Crear cuenta en Azure DevOps (gratis)

1. Ve a https://dev.azure.com y entra con una cuenta Microsoft (o crea una).
2. Si te pide crear una organización, acepta el nombre por defecto o pon uno propio
   (da igual cuál, no afecta el nombre público de la extensión).

## 2. Generar un Personal Access Token (PAT)

1. Dentro de Azure DevOps, arriba a la derecha: icono de usuario → **Personal access
   tokens**.
2. **New Token**:
   - Name: `vsce-publish` (o el que quieras)
   - Organization: **All accessible organizations** (importante, no solo la tuya)
   - Expiration: la que prefieras (ej. 90 días; si expira, se genera uno nuevo)
   - Scopes: **Custom defined** → busca **Marketplace** → marca **Manage**
3. Copia el token generado — solo se muestra una vez. Trátalo como una contraseña.

## 3. Registrar el publisher

1. Ve a https://marketplace.visualstudio.com/manage y entra con la misma cuenta.
2. **Create publisher**:
   - ID: debe coincidir EXACTO con el campo `"publisher"` de
     `integraciones/vscode-extension/package.json` (ahora mismo dice `mary010-sky`).
     Si el ID ya está tomado o prefieres otro, cambialo en el `package.json` para que
     coincida antes de publicar.
   - Display name: el nombre que se ve en la ficha de la extensión.

## 4. Publicar

Desde `integraciones/vscode-extension/`, con el token del paso 2:

```bash
npx @vscode/vsce publish -p <TU_TOKEN>
```

Esto compila, empaqueta y sube la extensión en un solo paso. Tarda unos minutos en
indexarse y aparecer en las búsquedas dentro de VS Code.

## 5. Publicar una nueva version despues

Cada publish necesita una version mayor a la anterior. Formas de hacerlo:

```bash
# sube el patch (0.0.1 -> 0.0.2) y publica
npx @vscode/vsce publish patch -p <TU_TOKEN>
```

## Notas de seguridad

- No compartas el PAT en chats, commits ni capturas de pantalla — quien lo tenga puede
  publicar/actualizar tu extensión.
- Si el token quedó expuesto en algún lado, revócalo desde Azure DevOps y genera uno
  nuevo antes de seguir usándolo.
