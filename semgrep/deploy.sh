#!/bin/bash

# ==============================================================================
# Script de Despliegue para VulnScan (Next.js + FastAPI) en Debian VPS
# ==============================================================================

set -e # Detener el script si hay algún error

echo "Actualizando el sistema operativo..."
sudo apt update && sudo apt upgrade -y

echo "Instalando dependencias base (git, curl, nginx, python3)..."
sudo apt install -y curl git python3 python3-pip python3-venv nginx

echo "Instalando Node.js (v20 LTS)..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

echo "Instalando PM2 para manejo de procesos en segundo plano..."
sudo npm install -g pm2

echo "Clonando el repositorio..."
cd /opt
sudo rm -rf vulnerabilidad-web
sudo git clone https://github.com/CarlosAyala1989/vulnerabilidad-web.git
# Dar permisos al usuario actual para poder instalar dependencias sin ser root
sudo chown -R $USER:$USER vulnerabilidad-web
cd vulnerabilidad-web

echo "---------------------------------------------------"
echo "Configurando Backend (FastAPI)..."
echo "---------------------------------------------------"
cd backend
python3 -m venv venv
source venv/bin/activate
# Instalar dependencias (asume que si no hay requirements, instala las manuales)
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install fastapi uvicorn sqlalchemy pydantic aiosqlite requests
fi
# Arrancar el backend con PM2
pm2 start "uvicorn main:app --host 127.0.0.1 --port 8000" --name "vuln-backend"
cd ..

echo "---------------------------------------------------"
echo "Configurando Frontend (Next.js)..."
echo "---------------------------------------------------"
cd frontend
# Corregir URLs hardcodeadas de localhost para que usen la ruta relativa del Nginx proxy
echo "Ajustando URLs de la API para producción..."
find src -type f -exec sed -i 's|http://127.0.0.1:8000/api|/api|g' {} +
find src -type f -exec sed -i 's|http://localhost:8000/api|/api|g' {} +

npm install
echo "Compilando la aplicación Next.js para producción..."
npm run build
# Arrancar el frontend con PM2
pm2 start "npm start" --name "vuln-frontend"
cd ..

echo "---------------------------------------------------"
echo "Configurando Nginx (Reverse Proxy)..."
echo "---------------------------------------------------"
# Configurar Nginx para rutear el tráfico hacia Next.js (/) y FastAPI (/api/)
sudo bash -c 'cat > /etc/nginx/sites-available/vulnerabilidad-web <<EOF
server {
    listen 80;
    server_name _; # Responde a cualquier IP/dominio

    # Bloque para Frontend (Next.js)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    # Bloque para Backend API (FastAPI)
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF'

# Activar el sitio y reiniciar nginx
sudo ln -sf /etc/nginx/sites-available/vulnerabilidad-web /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

echo "---------------------------------------------------"
echo "Configurando auto-arranque..."
echo "---------------------------------------------------"
# Guardar lista de pm2
pm2 save
# Generar script de inicio para que PM2 arranque al prender el servidor
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u $USER --hp /home/$USER

echo "=================================================================="
echo "¡DESPLIEGUE COMPLETADO CON ÉXITO!"
echo "Tu aplicación está corriendo y siendo servida por Nginx."
echo "Puedes acceder introduciendo la IP pública de tu VPS en el navegador."
echo "=================================================================="
