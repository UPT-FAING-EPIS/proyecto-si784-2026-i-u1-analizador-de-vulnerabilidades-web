"""
API Routes - REST endpoints for VulnScan
Ahora usa db.get_store() que puede ser MemoryStore o SupabaseStore
según las variables de entorno SUPABASE_URL y SUPABASE_KEY.
"""

from flask import Blueprint, request, jsonify
from core.engine import ScanEngine
from db import get_store
import uuid
import threading
import time

api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/scan', methods=['POST'])
def start_scan():
    """Inicia un nuevo escaneo de vulnerabilidades."""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Falta el campo requerido: url'}), 400

    url = data['url'].strip()
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    scan_id = str(uuid.uuid4())
    options = {
        'scan_xss':              data.get('scan_xss', True),
        'scan_sqli':             data.get('scan_sqli', True),
        'scan_headers':          data.get('scan_headers', True),
        'scan_csrf':             data.get('scan_csrf', True),
        'scan_redirect':         data.get('scan_redirect', True),
        'scan_info_disclosure':  data.get('scan_info_disclosure', True),
        'max_depth':             data.get('max_depth', 2),
        'timeout':               data.get('timeout', 10),
    }

    # Crear registro en el store (memoria o Supabase)
    store = get_store()
    store.create_scan(scan_id, url)

    # Ejecutar escaneo en hilo de fondo
    thread = threading.Thread(
        target=_run_scan,
        args=(scan_id, url, options),
        daemon=True
    )
    thread.start()

    return jsonify({'scan_id': scan_id, 'status': 'pending'}), 202


@api_blueprint.route('/scan/<scan_id>', methods=['GET'])
def get_scan(scan_id):
    """Obtiene el estado y resultados de un escaneo."""
    scan = get_store().get_scan(scan_id)
    if not scan:
        return jsonify({'error': 'Escaneo no encontrado'}), 404
    return jsonify(scan)


@api_blueprint.route('/scans', methods=['GET'])
def list_scans():
    """Lista todos los escaneos (más recientes primero)."""
    scans = get_store().list_scans(limit=50)
    return jsonify(scans)


@api_blueprint.route('/scan/<scan_id>', methods=['DELETE'])
def delete_scan(scan_id):
    """Elimina un escaneo."""
    ok = get_store().delete_scan(scan_id)
    if not ok:
        return jsonify({'error': 'Escaneo no encontrado'}), 404
    return jsonify({'message': 'Escaneo eliminado'}), 200


@api_blueprint.route('/scan/<scan_id>/report', methods=['GET'])
def get_report(scan_id):
    """Retorna el reporte HTML de un escaneo completado."""
    from reports.generator import ReportGenerator
    scan = get_store().get_scan(scan_id)
    if not scan:
        return jsonify({'error': 'Escaneo no encontrado'}), 404
    if scan['status'] != 'completed':
        return jsonify({'error': 'El escaneo aún no ha finalizado'}), 400

    html = ReportGenerator().generate_html(scan)
    return html, 200, {'Content-Type': 'text/html'}


def _run_scan(scan_id: str, url: str, options: dict):
    """Función interna — ejecuta el pipeline de escaneo en background."""
    store = get_store()
    try:
        store.update_scan(scan_id, status='running')
        engine = ScanEngine(options=options)

        def progress_cb(pct, msg):
            store.update_scan(scan_id, progress=pct, current_task=msg)

        results = engine.run(url, progress_callback=progress_cb)

        store.update_scan(
            scan_id,
            status='completed',
            progress=100,
            completed_at=time.time(),
            results=results,
            current_task='Escaneo completo.',
        )
    except Exception as e:
        store.update_scan(
            scan_id,
            status='error',
            error=str(e),
            completed_at=time.time(),
        )
