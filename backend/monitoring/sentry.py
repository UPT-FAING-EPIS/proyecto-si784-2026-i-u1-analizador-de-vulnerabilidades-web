"""
monitoring/sentry.py
Configura Sentry para captura de errores en producción.
Solo se activa si la variable SENTRY_DSN está configurada.
Si no está → no hace nada, el sistema sigue funcionando normal.
"""

import os
import logging

logger = logging.getLogger(__name__)


def init_sentry(app):
    """
    Inicializa Sentry si SENTRY_DSN está en las variables de entorno.
    Llama esta función dentro de create_app() en app.py.
    """
    dsn = os.environ.get('SENTRY_DSN', '').strip()

    if not dsn:
        logger.info("[Sentry] SENTRY_DSN no configurado — monitoreo desactivado.")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration

        # Captura logs de nivel WARNING y superior en Sentry
        logging_integration = LoggingIntegration(
            level=logging.WARNING,        # captura warnings como breadcrumbs
            event_level=logging.ERROR,    # envía errores como eventos
        )

        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                FlaskIntegration(),
                logging_integration,
            ],
            # Porcentaje de transacciones a rastrear para performance
            # 0.1 = 10% — suficiente para proyecto académico sin gastar cuota
            traces_sample_rate=0.1,

            # No enviar datos sensibles
            send_default_pii=False,

            # Entorno — útil para filtrar en el dashboard
            environment=os.environ.get('FLASK_ENV', 'production'),

            # Release para rastrear qué versión tiene el error
            release="vulnscan@1.0.0",
        )

        logger.info("[Sentry] ✅ Monitoreo de errores activado.")

    except ImportError:
        logger.warning("[Sentry] Librería sentry-sdk no instalada. "
                       "Ejecuta: pip install sentry-sdk[flask]")
    except Exception as e:
        logger.error(f"[Sentry] Error al inicializar: {e}")
