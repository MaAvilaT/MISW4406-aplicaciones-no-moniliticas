from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import os
from src.handlers.lab_result_handler import LabResultHandler
from src.config import Config

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Ruta para recibir resultados de laboratorio
@app.route('/api/lab-results', methods=['POST'])
@metrics.counter('lab_results_received', 'Number of lab results received')
def process_lab_results():
    return LabResultHandler().handle_request()

# Endpoint de salud
@app.route('/health/live', methods=['GET'])
def liveness():
    return jsonify({"status": "ok", "service": "msvc-integrator-service"}), 200

@app.route('/health/ready', methods=['GET'])
def readiness():
    try:
        # Aquí podríamos verificar la conexión a RabbitMQ
        return jsonify({"status": "ok", "service": "msvc-integrator-service"}), 200
    except Exception as e:
        app.logger.error(f"Readiness check failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
