# Gunicorn configuration for production deployment

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('FLASK_PORT', '5000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120  # Increased timeout for AI processing
keepalive = 5

# Logging
accesslog = '/var/log/voice-assistant/access.log'
errorlog = '/var/log/voice-assistant/error.log'
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'voice-assistant'

# Server mechanics
daemon = False
pidfile = '/var/run/voice-assistant.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# Development mode
reload = os.getenv('FLASK_ENV', 'production') == 'development'
