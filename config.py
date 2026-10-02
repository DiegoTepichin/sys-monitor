import os

# Load .env file manually if it exists to synchronize environment variables
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip().strip('"').strip("'")
                    os.environ[key.strip()] = val
    except Exception as e:
        print(f"Warning: Failed to load .env file manually: {e}")


def safe_int(value, default):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# Server Configuration
PORT = safe_int(os.environ.get("PORT"), 5002)
HOST = os.environ.get("HOST", "0.0.0.0")
# Debug mode exposes the Werkzeug debugger; never enable it on a public interface
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Where "/" redirects when no frontend build (frontend/dist) is present
FRONTEND_DEV_URL = os.environ.get("FRONTEND_DEV_URL", "http://localhost:3000")

# Security Configurations
API_KEY = os.environ.get("API_KEY", "sys-monitor-secret-token")
if API_KEY == "sys-monitor-secret-token":
    print(
        "WARNING: Using default API key 'sys-monitor-secret-token'. Set API_KEY in .env for production."
    )

# Daemon and App Settings
POLL_INTERVAL = safe_int(os.environ.get("POLL_INTERVAL"), 5)
HISTORY_LIMIT = safe_int(os.environ.get("HISTORY_LIMIT"), 20)
LOG_FILE = os.environ.get("LOG_FILE", "logs/app.log")

# System Health Warning Thresholds (Percentage)
CPU_THRESHOLD = safe_int(os.environ.get("CPU_THRESHOLD"), 80)
MEMORY_THRESHOLD = safe_int(os.environ.get("MEMORY_THRESHOLD"), 85)
DISK_THRESHOLD = safe_int(os.environ.get("DISK_THRESHOLD"), 90)
