# pyrefly: ignore [missing-import]
from flask import Flask, jsonify, render_template, request
import logging
import os
from datetime import datetime

# Load configuration values
from config import (
    PORT, HOST, DEBUG, API_KEY, POLL_INTERVAL, 
    HISTORY_LIMIT, LOG_FILE, CPU_THRESHOLD, 
    MEMORY_THRESHOLD, DISK_THRESHOLD
)
from scripts.monitor_cpu import get_cpu_usage
from scripts.monitor_memory import get_memory_usage
from scripts.monitor_disk import get_disk_usage
from scripts.monitor_processes import get_top_processes

# Create directory for logs if specified and missing
if LOG_FILE:
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

# Configure logging to both console and file handler
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Clear existing handlers to prevent duplicate logging
if logger.hasHandlers():
    logger.handlers.clear()

# Stream (console) handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler
if LOG_FILE:
    try:
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to initialize logging file handler: {e}")

app = Flask(__name__)

# Global in-memory thread-safe-ish list for metrics history
metrics_history = []

def format_current_timestamp() -> str:
    """Helper to get current time in ISO 8601 UTC format."""
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def evaluate_thresholds(cpu_pct: float, mem_pct: float, disk_pct: float) -> list:
    """Check performance percentages against defined thresholds and compile alerts."""
    alerts = []
    if cpu_pct > CPU_THRESHOLD:
        alerts.append(f"High CPU utilization: {cpu_pct}% (Threshold: {CPU_THRESHOLD}%)")
    if mem_pct > MEMORY_THRESHOLD:
        alerts.append(f"High Memory utilization: {mem_pct}% (Threshold: {MEMORY_THRESHOLD}%)")
    if disk_pct > DISK_THRESHOLD:
        alerts.append(f"High Disk utilization: {disk_pct}% (Threshold: {DISK_THRESHOLD}%)")
    return alerts

@app.route('/')
def dashboard():
    """Renders the HTML monitoring dashboard interface."""
    logger.info("Serving root dashboard page.")
    try:
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}", exc_info=True)
        return "Internal Server Error", 500

@app.route('/api/health', methods=['GET'])
def api_health():
    """Endpoint representing server status check."""
    logger.info("Health check endpoint hit.")
    return jsonify({
        "status": "ok",
        "timestamp": format_current_timestamp()
    }), 200

@app.route('/api/metrics', methods=['GET', 'POST'])
def api_metrics():
    """API endpoint to collect, push, and query system metrics.

    - GET: Query current host metrics, append to history, and return JSON payload.
    - POST: Allow external agents to send metric payloads (protected by API Key header).
    """
    if request.method == 'POST':
        # Security check for POST request
        provided_key = request.headers.get("X-API-Key")
        if not provided_key or provided_key != API_KEY:
            logger.warning(f"Unauthorized metrics POST attempt. API Key mismatch or missing. IP: {request.remote_addr}")
            return jsonify({"error": "Unauthorized. Invalid X-API-Key."}), 401
        
        try:
            payload = request.get_json()
            if not payload:
                return jsonify({"error": "Bad Request. Missing JSON body."}), 400
            
            # Ensure timestamp is present
            if "timestamp" not in payload:
                payload["timestamp"] = format_current_timestamp()
                
            # Evaluate thresholds on the POSTed payload if not already calculated
            cpu_pct = payload.get("cpu", {}).get("percent", 0.0)
            mem_pct = payload.get("memory", {}).get("percent", 0.0)
            disk_pct = payload.get("disk", {}).get("percent", 0.0)
            
            payload["alerts"] = evaluate_thresholds(cpu_pct, mem_pct, disk_pct)
            payload["status"] = "warning" if payload["alerts"] else "healthy"

            # Append to in-memory history list (FIFO queue structure)
            metrics_history.append(payload)
            if len(metrics_history) > HISTORY_LIMIT:
                metrics_history.pop(0)
                
            logger.info("Received and recorded external metrics from agent.")
            return jsonify({"status": "success", "message": "Metrics recorded"}), 201
            
        except Exception as e:
            logger.error(f"Failed to parse agent metrics payload: {e}", exc_info=True)
            return jsonify({"error": "Bad Request", "details": str(e)}), 400

    else:
        # GET metrics method: calculate locally
        try:
            cpu_data = get_cpu_usage()
            memory_data = get_memory_usage()
            disk_data = get_disk_usage()
            processes_data = get_top_processes(5)

            cpu_pct = cpu_data.get("percent", 0.0)
            mem_pct = memory_data.get("percent", 0.0)
            disk_pct = disk_data.get("percent", 0.0)

            alerts = evaluate_thresholds(cpu_pct, mem_pct, disk_pct)
            
            # If sub-modules returned errors, bubble them up into alerts
            for name, data in [("CPU", cpu_data), ("Memory", memory_data), ("Disk", disk_data)]:
                if data.get("error"):
                    alerts.append(f"{name} sensor error: {data['error']}")

            metrics_payload = {
                "timestamp": format_current_timestamp(),
                "cpu": cpu_data,
                "memory": memory_data,
                "disk": disk_data,
                "processes": processes_data,
                "alerts": alerts,
                "status": "warning" if alerts else "healthy"
            }

            # Update metrics history
            metrics_history.append(metrics_payload)
            if len(metrics_history) > HISTORY_LIMIT:
                metrics_history.pop(0)

            logger.info("Retrieved current local system metrics.")
            return jsonify(metrics_payload), 200

        except Exception as e:
            logger.error(f"Uncaught exception while calculating local metrics: {e}", exc_info=True)
            # Fallback degraded response
            fallback_payload = {
                "timestamp": format_current_timestamp(),
                "cpu": {"percent": 0.0, "cores": 0, "error": str(e)},
                "memory": {"percent": 0.0, "error": str(e)},
                "disk": {"percent": 0.0, "error": str(e)},
                "processes": [],
                "alerts": [f"Monitoring service error: {str(e)}"],
                "status": "warning"
            }
            return jsonify(fallback_payload), 200

@app.route('/api/metrics/history', methods=['GET'])
def api_metrics_history():
    """Returns the in-memory array of recorded performance metrics."""
    logger.info("Serving metrics history list.")
    try:
        return jsonify(metrics_history), 200
    except Exception as e:
        logger.error(f"Error fetching metrics history: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == '__main__':
    logger.info(f"Starting Sys-Monitor Flask server on http://{HOST}:{PORT} (Debug={DEBUG})")
    app.run(host=HOST, port=PORT, debug=DEBUG)
