#!/bin/bash
# ============================================================
# VulnScan Pro - Script de Despliegue Completo en VPS Linux
# Nativo, sin Docker. Ubuntu/Debian 22.04+
# Servidor: 149.34.48.176
# ============================================================

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

APP_DIR="/opt/vulnscan"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
LOG_DIR="/var/log/vulnscan"
REPORTS_DIR="/var/lib/vulnscan/reports"
DB_NAME="vulnscan"; DB_USER="vulnuser"; DB_PASS=""; VPS_IP="149.34.48.176"; DOMAIN=""

check_root() { [[ $EUID -ne 0 ]] && log_error "Ejecutar como root: sudo bash deploy.sh"; }

prompt_config() {
  echo ""
  echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║     VulnScan Pro - Configuración Inicial     ║${NC}"
  echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
  echo ""
  read -p "Contraseña para usuario MySQL '$DB_USER': " -s DB_PASS; echo ""
  [[ -z "$DB_PASS" ]] && log_error "La contraseña no puede estar vacía"
  read -p "API Key de DeepSeek (opcional, Enter para omitir): " DEEPSEEK_KEY; echo ""
  read -p "Dominio (opcional, Enter para usar IP $VPS_IP): " DOMAIN; echo ""
  SECRET_KEY=$(openssl rand -hex 32)
  log_success "Secret key generada"
}

install_system_deps() {
  log_info "Instalando dependencias del sistema..."
  apt-get update -qq
  apt-get install -y -qq curl wget git python3 python3-pip python3-venv python3-dev \
    nginx certbot python3-certbot-nginx mysql-server mysql-client \
    build-essential libssl-dev libffi-dev pkg-config default-libmysqlclient-dev \
    ufw lsof net-tools > /dev/null 2>&1
  log_success "Dependencias instaladas"
}

install_nodejs() {
  if ! command -v node &> /dev/null; then
    log_info "Instalando Node.js 20 LTS..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - > /dev/null 2>&1
    apt-get install -y nodejs > /dev/null 2>&1
    log_success "Node.js $(node --version) instalado"
  else
    log_success "Node.js ya instalado: $(node --version)"
  fi
  if ! command -v pm2 &> /dev/null; then
    npm install -g pm2 > /dev/null 2>&1
    pm2 startup systemd -u root --hp /root > /dev/null 2>&1
    log_success "PM2 instalado"
  fi
}

setup_mysql() {
  log_info "Configurando MySQL..."
  systemctl start mysql 2>/dev/null || true
  systemctl enable mysql 2>/dev/null || true
  mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || true
  mysql -e "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';" 2>/dev/null || true
  mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';" 2>/dev/null || true
  mysql -e "FLUSH PRIVILEGES;" 2>/dev/null || true
  mysql -u "$DB_USER" -p"$DB_PASS" -e "USE $DB_NAME; SELECT 1;" > /dev/null 2>&1 || log_error "No se puede conectar a MySQL"
  log_success "MySQL configurado"
}

deploy_backend() {
  log_info "Desplegando backend FastAPI..."
  mkdir -p "$BACKEND_DIR" "$LOG_DIR" "$REPORTS_DIR"
  cp -r backend/* "$BACKEND_DIR/"
  rm -rf "$BACKEND_DIR/venv" 2>/dev/null || true
  python3 -m venv "$BACKEND_DIR/venv"
  "$BACKEND_DIR/venv/bin/pip" install --quiet --upgrade pip
  "$BACKEND_DIR/venv/bin/pip" install --quiet -r "$BACKEND_DIR/requirements.txt" 2>/dev/null || {
    log_warn "Instalando sin WeasyPrint..."
    grep -v "weasyprint" "$BACKEND_DIR/requirements.txt" > /tmp/req_light.txt
    "$BACKEND_DIR/venv/bin/pip" install --quiet -r /tmp/req_light.txt
  }
  FRONTEND_URL="http://${DOMAIN:-$VPS_IP}"
  cat > "$BACKEND_DIR/.env" <<EOF
DATABASE_URL=mysql+pymysql://$DB_USER:$DB_PASS@localhost:3306/$DB_NAME
DB_HOST=localhost
DB_PORT=3306
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASS
DB_NAME=$DB_NAME
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEEPSEEK_API_KEY=${DEEPSEEK_KEY:-}
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
API_HOST=127.0.0.1
API_PORT=8000
ENVIRONMENT=production
ALLOWED_ORIGINS=${FRONTEND_URL},http://localhost:3000
LOG_LEVEL=INFO
LOG_FILE=$LOG_DIR/backend.log
REPORTS_DIR=$REPORTS_DIR
EOF
  chmod 600 "$BACKEND_DIR/.env"
  log_success "Backend configurado"
}

deploy_frontend() {
  log_info "Compilando frontend Next.js..."
  mkdir -p "$FRONTEND_DIR"
  cp -r frontend/* "$FRONTEND_DIR/"
  cat > "$FRONTEND_DIR/.env.local" <<EOF
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
EOF
  cd "$FRONTEND_DIR"
  npm install --silent > /dev/null 2>&1
  npm run build > /dev/null 2>&1
  log_success "Frontend compilado"
}

create_systemd_backend() {
  log_info "Creando servicio systemd para backend..."
  cat > /etc/systemd/system/vulnscan-backend.service <<EOF
[Unit]
Description=VulnScan Pro Backend (FastAPI)
After=network.target mysql.service
Requires=mysql.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$BACKEND_DIR/venv/bin"
ExecStart=$BACKEND_DIR/venv/bin/gunicorn main:app \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --workers 4 \\
    --bind 127.0.0.1:8000 \\
    --timeout 120 \\
    --access-logfile $LOG_DIR/access.log \\
    --error-logfile $LOG_DIR/error.log \\
    --log-level info
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vulnscan-backend
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
EOF
  chown -R www-data:www-data "$BACKEND_DIR" "$LOG_DIR" "$REPORTS_DIR"
  chmod -R 750 "$BACKEND_DIR"
  chmod 600 "$BACKEND_DIR/.env"
  chmod -R 755 "$LOG_DIR" "$REPORTS_DIR"
  systemctl daemon-reload
  systemctl enable vulnscan-backend
  systemctl start vulnscan-backend
  sleep 4
  if systemctl is-active --quiet vulnscan-backend; then
    log_success "Backend corriendo en puerto 8000"
  else
    log_warn "Backend no iniciado — revisar: journalctl -u vulnscan-backend -n 30"
  fi
}

create_pm2_frontend() {
  log_info "Configurando frontend con PM2..."
  cat > "$APP_DIR/ecosystem.config.js" <<EOF
module.exports = {
  apps: [{
    name: 'vulnscan-frontend',
    cwd: '$FRONTEND_DIR',
    script: 'node_modules/.bin/next',
    args: 'start -p 3000',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '512M',
    env: { NODE_ENV: 'production', PORT: 3000 },
    log_file: '$LOG_DIR/frontend.log',
    error_file: '$LOG_DIR/frontend-error.log',
  }]
};
EOF
  cd "$APP_DIR"
  pm2 start ecosystem.config.js
  pm2 save
  sleep 3
  pm2 list | grep -q "vulnscan-frontend.*online" && log_success "Frontend corriendo en puerto 3000" || log_warn "Frontend no iniciado — revisar: pm2 logs vulnscan-frontend"
}

configure_nginx() {
  log_info "Configurando Nginx..."
  SERVER_NAME="${DOMAIN:-$VPS_IP}"
  cat > /etc/nginx/sites-available/vulnscan <<NGINXEOF
limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;

server {
    listen 80;
    server_name $SERVER_NAME;

    access_log /var/log/nginx/vulnscan_access.log;
    error_log /var/log/nginx/vulnscan_error.log;

    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_comp_level 6;

    location /api/auth/login {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location ~ ^/(api|health|docs) {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 10;
    }

    location /_next/static/ {
        proxy_pass http://127.0.0.1:3000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_cache_bypass \$http_upgrade;
    }

    location ~ /\. { deny all; }
    location ~ \.(env|git|sql|bak)\$ { deny all; }
}
NGINXEOF
  ln -sf /etc/nginx/sites-available/vulnscan /etc/nginx/sites-enabled/
  rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
  nginx -t && systemctl reload nginx
  log_success "Nginx configurado para $SERVER_NAME"
}

configure_firewall() {
  log_info "Configurando firewall UFW..."
  ufw --force reset > /dev/null 2>&1
  ufw default deny incoming > /dev/null 2>&1
  ufw default allow outgoing > /dev/null 2>&1
  ufw allow ssh > /dev/null 2>&1
  ufw allow 80/tcp > /dev/null 2>&1
  ufw allow 443/tcp > /dev/null 2>&1
  ufw --force enable > /dev/null 2>&1
  log_success "Firewall configurado (22, 80, 443)"
}

verify_ports() {
  log_info "Verificando puertos..."
  echo ""
  ss -tlnp 2>/dev/null | grep -E ":(80|443|8000|3000|3306) " || echo "  (sin puertos activos detectados)"
  echo ""
}

print_summary() {
  FRONTEND_URL="http://${DOMAIN:-$VPS_IP}"
  echo ""
  echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║          VulnScan Pro - Despliegue Completado         ║${NC}"
  echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
  echo ""
  echo -e "  ${BLUE}Plataforma:${NC}    $FRONTEND_URL"
  echo -e "  ${BLUE}API Docs:${NC}      http://127.0.0.1:8000/api/docs"
  echo -e "  ${BLUE}Health:${NC}        http://127.0.0.1:8000/health"
  echo ""
  echo -e "  ${YELLOW}PRIMER USUARIO → ADMIN automáticamente${NC}"
  echo -e "  Accede a $FRONTEND_URL/register para registrarte"
  echo ""
  echo -e "  ${BLUE}Comandos útiles:${NC}"
  echo "    systemctl status vulnscan-backend"
  echo "    pm2 status && pm2 logs vulnscan-frontend"
  echo "    journalctl -u vulnscan-backend -f"
  echo "    tail -f /var/log/vulnscan/backend.log"
  echo ""
  if [[ -n "$DOMAIN" ]]; then
    echo -e "  ${YELLOW}SSL con Let's Encrypt:${NC}"
    echo "    certbot --nginx -d $DOMAIN"
    echo ""
  fi
  echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
}

main() {
  check_root
  prompt_config
  install_system_deps
  install_nodejs
  setup_mysql
  deploy_backend
  deploy_frontend
  create_systemd_backend
  create_pm2_frontend
  configure_nginx
  configure_firewall
  verify_ports
  print_summary
}

main "$@"
