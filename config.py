import os

# Load .env file manually if it exists to synchronize environment variables
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    try:
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    # Strip quotes if present
                    val = val.strip().strip('"').strip("'")
                    os.environ[key.strip()] = val
    except Exception as e:
        print(f"Warning: Failed to load .env file manually: {e}")


# Server Configuration
PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

# Security Configurations
API_KEY = os.environ.get("API_KEY", "sys-monitor-secret-token")

# Daemon and App Settings
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", 5))        # JavaScript refresh and agent interval in seconds
HISTORY_LIMIT = int(os.environ.get("HISTORY_LIMIT", 20))       # In-memory metrics history limit
LOG_FILE = os.environ.get("LOG_FILE", "logs/app.log")          # Output destination for log files

# System Health Warning Thresholds (Percentage)
CPU_THRESHOLD = int(os.environ.get("CPU_THRESHOLD", 80))      # Warning threshold for CPU
MEMORY_THRESHOLD = int(os.environ.get("MEMORY_THRESHOLD", 85))  # Warning threshold for RAM
DISK_THRESHOLD = int(os.environ.get("DISK_THRESHOLD", 90))      # Warning threshold for Disk
