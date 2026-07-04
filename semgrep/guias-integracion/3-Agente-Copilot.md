# Guía Paso a Paso: Agente para GitHub Copilot

El agente ya está desplegado y activo 24/7 en:

**`https://vulnerabilidad-web.sytes.net/copilot-agent/`**

Corre como servicio systemd (`wvs-copilot-agent.service`, `Restart=always`) en el mismo
VPS que el backend. No necesitas ngrok, no necesitas tener nada corriendo en tu PC —
solo registrar la GitHub App apuntando a esa URL.

## 1. Requisitos previos
- Una cuenta de **GitHub** con acceso a Copilot.
- Nada más. El agente ya cumple el protocolo real de Copilot Extensions: responde en
  streaming (Server-Sent Events) y verifica la firma de las peticiones de GitHub.

## 2. Configurar la GitHub App (Copilot Extension)

1. Ve a **GitHub > Settings > Developer settings > GitHub Apps**.
2. Haz clic en **"New GitHub App"**.
3. Rellena los datos:
   - **GitHub App name:** `WVS Scanner Agent` (o el nombre que prefieras, debe ser único
     en todo GitHub)
   - **Homepage URL:** `https://vulnerabilidad-web.sytes.net`
   - **Webhook:** desmarca "Active" (no lo necesitas)
4. En **Permissions**, no necesitas permisos adicionales para esta version simple del
   agente.
5. Baja a la sección **"Copilot"**:
   - En **App Type**, selecciona **Agent**.
   - En **URL**, pega: `https://vulnerabilidad-web.sytes.net/copilot-agent/`
6. En **Where can this GitHub App be installed?**, elige **Only on this account**
   (la dejamos privada/no listada, sin pasar por revisión de GitHub).
7. Dale a **Create GitHub App**.
8. En el menú izquierdo de la App recién creada, ve a **Install App** y haz clic en
   Install para tu cuenta.

## 3. Probar en Visual Studio Code

1. Abre VS Code con sesión iniciada en la cuenta de GitHub donde instalaste la App.
2. Abre el panel de **Copilot Chat**.
3. Escribe `@`. Debería aparecer el nombre de tu agente en las sugerencias
   (ej. `@wvs-scanner-agent`).
4. Pruébalo:
   ```text
   @wvs-scanner-agent analiza la seguridad de https://ejemplo.com
   ```
5. El mensaje llega firmado a `https://vulnerabilidad-web.sytes.net/copilot-agent/`,
   el agente verifica que sea realmente GitHub quien pregunta, lanza el escaneo contra
   el backend y transmite el resultado en Markdown de vuelta al chat.

## Administración (en el VPS)

```bash
ssh root@149.34.48.176
systemctl status wvs-copilot-agent.service
journalctl -u wvs-copilot-agent.service -f
systemctl restart wvs-copilot-agent.service
```

## Nota sobre la verificacion de firma

Si durante las pruebas ves errores 401 "Firma invalida" y quieres descartar que el
problema sea la verificacion (en vez de la GitHub App mal configurada), puedes
desactivarla temporalmente editando el servicio:

```bash
# en /etc/systemd/system/wvs-copilot-agent.service, agregar:
Environment="WVS_COPILOT_VERIFY_SIGNATURE=false"
# luego:
systemctl daemon-reload && systemctl restart wvs-copilot-agent.service
```

Vuelve a activarla (quitando esa linea) una vez que confirmes que el resto del flujo
funciona — sin verificacion de firma, cualquiera que conozca la URL podria enviarle
peticiones al agente haciendose pasar por GitHub.
