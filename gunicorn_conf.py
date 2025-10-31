import os

# Gunicorn configuration for Render / minimal memory usage
bind = "0.0.0.0:" + os.environ.get("PORT", "10000")
workers = 1  # keep workers small when model is loaded in memory
threads = 2
timeout = 120  # allow longer startup/loads
preload_app = False  # avoid loading model in master if memory is tight
