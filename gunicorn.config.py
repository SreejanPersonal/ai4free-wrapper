workers = 9  # (2 * CPU cores) + 1 = 9 for 4 vCPUs
worker_class = "gevent"  # Asynchronous worker class
threads = 2  # Threads per worker
bind = "0.0.0.0:5000"  # Bind to all interfaces on port 5000
timeout = 300  # Timeout for worker processes
max_requests = 1000  # Restart worker after handling 1000 requests
max_requests_jitter = 50  # Add randomness to max_requests to avoid simultaneous restarts