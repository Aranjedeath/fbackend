import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 2000
backlog = 2048
daemon = True
loglevel = 'debug'
accesslog = '/tmp/guni_access.log'
errorlog = '/tmp/guni_error.log'
max_requests = 1000
graceful_timeout = 30
