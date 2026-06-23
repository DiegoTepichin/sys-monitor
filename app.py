from flask import Flask, jsonify, render_template
import logging

# Load configuration values
from config import PORT, HOST, DEBUG, CPU_THRESHOLD, MEMORY_THRESHOLD, DISK_THRESHOLD
from scripts.monitor_cpu import get_cpu_usage
from scripts.monitor_memory import get_memory_usage
from scripts.monitor_disk import get_disk_usage
from scripts.monitor_processes import get_top_processes

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def dashboard():
    """
    Renders the web-based monitoring dashboard interface.
    """
    return render_template('dashboard.html')

@app.route('/api/metrics')
def api_metrics():
    """
    API endpoint that collects, validates, and serves system performance metrics.
    Compares metrics against preset thresholds to flag warnings.
    """
    try:
        cpu = get_cpu_usage()
        memory = get_memory_usage()
        disk = get_disk_usage()
        processes = get_top_processes(5)

        # Analyze metrics against safety thresholds to detect anomalies
        alerts = []
        if cpu > CPU_THRESHOLD:
            alerts.append(f"High CPU utilization: {cpu}% (Threshold: {CPU_THRESHOLD}%)")
        
        mem_percent = memory.get("percent", 0.0)
        if mem_percent > MEMORY_THRESHOLD:
            alerts.append(f"High Memory utilization: {mem_percent}% (Threshold: {MEMORY_THRESHOLD}%)")
            
        disk_percent = disk.get("percent", 0.0)
        if disk_percent > DISK_THRESHOLD:
            alerts.append(f"High Disk utilization: {disk_percent}% (Threshold: {DISK_THRESHOLD}%)")

        metrics_payload = {
            "cpu": cpu,
            "memory": memory,
            "disk": disk,
            "processes": processes,
            "alerts": alerts,
            "status": "warning" if alerts else "healthy"
        }
        
        return jsonify(metrics_payload), 200
        
    except Exception as e:
        logger.error(f"Uncaught exception while fetching API metrics: {e}", exc_info=True)
        return jsonify({
            "error": "Failed to collect system metrics",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    logger.info(f"Launching Sys-Monitor Flask server on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
