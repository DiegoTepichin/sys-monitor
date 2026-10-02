# pyrefly: ignore [missing-import]
import hmac
import logging
import os
import threading
import time
from collections import deque
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler

import psutil
from flask import Flask, jsonify, redirect, request

# Load configuration values
from config import (
    API_KEY,
    CPU_THRESHOLD,
    DEBUG,
    DISK_THRESHOLD,
    HISTORY_LIMIT,
    HOST,
    LOG_FILE,
    MEMORY_THRESHOLD,
    PORT,
)
from scripts.monitor_cpu import get_cpu_usage
from scripts.monitor_disk import get_disk_usage
from scripts.monitor_memory import get_memory_usage
from scripts.monitor_network import get_network_usage
from scripts.monitor_processes import get_top_processes

# Create directory for logs if specified and missing
if LOG_FILE:
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

# Configure logging to both console and file handler
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

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
        # Cap disk usage: 5 MB per file, 3 backups
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to initialize logging file handler: {e}")

app = Flask(__name__)

# Bounded FIFO of normalized snapshots; the lock guards concurrent request threads
metrics_history: deque[dict] = deque(maxlen=HISTORY_LIMIT)
_history_lock = threading.Lock()


def record_snapshot(payload: dict) -> None:
    snapshot = normalize_payload(payload)
    with _history_lock:
        metrics_history.append(snapshot)


def format_current_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def evaluate_thresholds(cpu_pct: float, mem_pct: float, disk_pct: float) -> list:
    alerts = []
    if cpu_pct > CPU_THRESHOLD:
        alerts.append(f"High CPU utilization: {cpu_pct}% (Threshold: {CPU_THRESHOLD}%)")
    if mem_pct > MEMORY_THRESHOLD:
        alerts.append(f"High Memory utilization: {mem_pct}% (Threshold: {MEMORY_THRESHOLD}%)")
    if disk_pct > DISK_THRESHOLD:
        alerts.append(f"High Disk utilization: {disk_pct}% (Threshold: {DISK_THRESHOLD}%)")
    return alerts


def is_valid_metrics_payload(payload: dict) -> str | None:
    if not isinstance(payload, dict):
        return "Payload must be a JSON object"
    for key in ("cpu", "memory", "disk"):
        section = payload.get(key)
        if not isinstance(section, dict):
            return f"'{key}' must be a JSON object"
        percent = section.get("percent")
        # bool is a subclass of int, so reject it explicitly
        if isinstance(percent, bool) or not isinstance(percent, int | float):
            return f"'{key}.percent' must be a number"
        if not 0 <= percent <= 100:
            return f"'{key}.percent' must be between 0 and 100"
    return None


def is_authorized(provided_key: str | None) -> bool:
    # Constant-time comparison prevents timing attacks on the API key
    return bool(provided_key) and hmac.compare_digest(provided_key.encode(), API_KEY.encode())


def normalize_payload(source: dict) -> dict:
    return {
        "timestamp": source.get("timestamp", format_current_timestamp()),
        "cpu": source.get("cpu", {"percent": 0.0, "error": "No data"}),
        "memory": source.get("memory", {"percent": 0.0, "error": "No data"}),
        "disk": source.get("disk", {"percent": 0.0, "error": "No data"}),
        "network": source.get("network", {"download_mb": 0.0, "upload_mb": 0.0}),
        "processes": source.get("processes", []),
        "alerts": source.get("alerts", []),
        "status": source.get("status", "healthy"),
    }


@app.route("/")
def dashboard():
    logger.debug("Redirecting root to Vite frontend.")
    return redirect("http://localhost:3000", code=302)


@app.route("/api/health", methods=["GET"])
def api_health():
    logger.debug("Health check endpoint hit.")
    return jsonify({"status": "ok", "timestamp": format_current_timestamp()}), 200


@app.route("/api/metrics", methods=["GET", "POST"])
def api_metrics():
    if request.method == "POST":
        if not is_authorized(request.headers.get("X-API-Key")):
            logger.warning(
                f"Unauthorized metrics POST attempt. API Key mismatch or missing. IP: {request.remote_addr}"
            )
            return jsonify({"error": "Forbidden. Invalid or missing X-API-Key."}), 403

        try:
            payload = request.get_json(silent=True)
            if not payload:
                return jsonify({"error": "Bad Request. Missing JSON body."}), 400

            validation_error = is_valid_metrics_payload(payload)
            if validation_error:
                return jsonify({"error": "Bad Request", "details": validation_error}), 400

            if "timestamp" not in payload:
                payload["timestamp"] = format_current_timestamp()

            cpu_pct = payload.get("cpu", {}).get("percent", 0.0)
            mem_pct = payload.get("memory", {}).get("percent", 0.0)
            disk_pct = payload.get("disk", {}).get("percent", 0.0)
            payload["alerts"] = evaluate_thresholds(cpu_pct, mem_pct, disk_pct)
            payload["status"] = "warning" if payload["alerts"] else "healthy"

            record_snapshot(payload)

            logger.debug("Received and recorded external metrics from agent.")
            return jsonify({"status": "success", "message": "Metrics recorded"}), 201

        except Exception as e:
            logger.error(f"Failed to parse agent metrics payload: {e}", exc_info=True)
            return jsonify(
                {"error": "Bad Request", "details": "Could not process metrics payload"}
            ), 400

    else:
        try:
            cpu_data = get_cpu_usage()
            memory_data = get_memory_usage()
            disk_data = get_disk_usage()
            processes_data = get_top_processes(5)
            network_data = get_network_usage()

            uptime = time.time() - psutil.boot_time()
            total_processes = len(psutil.pids())

            cpu_pct = cpu_data.get("percent", 0.0)
            mem_pct = memory_data.get("percent", 0.0)
            disk_pct = disk_data.get("percent", 0.0)

            alerts = evaluate_thresholds(cpu_pct, mem_pct, disk_pct)

            for name, data in [
                ("CPU", cpu_data),
                ("Memory", memory_data),
                ("Disk", disk_data),
                ("Network", network_data),
            ]:
                if isinstance(data, dict) and data.get("error"):
                    alerts.append(f"{name} sensor error: {data['error']}")

            metrics_payload = {
                "timestamp": format_current_timestamp(),
                "uptime": uptime,
                "total_processes": total_processes,
                "cpu": cpu_data,
                "memory": memory_data,
                "disk": disk_data,
                "network": network_data,
                "processes": processes_data,
                "alerts": alerts,
                "status": "warning" if alerts else "healthy",
            }

            record_snapshot(metrics_payload)

            logger.debug("Retrieved current local system metrics.")
            return jsonify(metrics_payload), 200

        except Exception as e:
            logger.error(f"Uncaught exception while calculating local metrics: {e}", exc_info=True)
            fallback_payload = {
                "timestamp": format_current_timestamp(),
                "cpu": {"percent": 0.0, "cores": 0, "error": str(e)},
                "memory": {"percent": 0.0, "error": str(e)},
                "disk": {"percent": 0.0, "error": str(e)},
                "processes": [],
                "alerts": [f"Monitoring service error: {str(e)}"],
                "status": "warning",
                "degraded": True,
            }
            return jsonify(fallback_payload), 500


@app.route("/api/metrics/history", methods=["GET"])
def api_metrics_history():
    with _history_lock:
        snapshot = list(metrics_history)
    return jsonify(snapshot), 200


if __name__ == "__main__":
    logger.info(f"Starting Sys-Monitor Flask server on http://{HOST}:{PORT} (Debug={DEBUG})")
    app.run(host=HOST, port=PORT, debug=DEBUG)
