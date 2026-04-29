"""
VulnScan - Web Vulnerability Analysis System
app.py — Entry point con Sentry + Health checks integrados
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from api.routes import api_blueprint
from monitoring.health import health_blueprint
from monitoring.sentry import init_sentry

# Cargar .env si existe (solo en desarrollo local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv no instalado, usar variables del sistema

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)


def create_app():
    app = Flask(__name__)

    # ── Sentry: monitoreo de errores ───────────────────────────
    # Solo se activa si SENTRY_DSN está en el entorno
    init_sentry(app)

    # ── CORS ───────────────────────────────────────────────────
    allowed_origins = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ]
    frontend_url = os.environ.get('FRONTEND_URL', '').strip()
    if frontend_url:
        allowed_origins.append(frontend_url)

    CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
    app.config['JSON_SORT_KEYS'] = False

    # ── Blueprints ─────────────────────────────────────────────
    app.register_blueprint(api_blueprint,    url_prefix='/api')
    app.register_blueprint(health_blueprint)   # /health y /ping

    # ── Página de inicio ───────────────────────────────────────
    @app.route('/')
    def index():
        return {
            'service':  'VulnScan API',
            'version':  '1.0.0',
            'endpoints': {
                'health':     '/health',
                'ping':       '/ping',
                'start_scan': 'POST /api/scan',
                'get_scan':   'GET /api/scan/{id}',
                'list_scans': 'GET /api/scans',
                'report':     'GET /api/scan/{id}/report',
            }
        }

    return app


# Gunicorn necesita el objeto app en el módulo
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
