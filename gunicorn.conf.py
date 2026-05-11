import os

preload_app = True
workers = 1

timeout = 120
graceful_timeout = 30

accesslog = "-"
errorlog = "-"
loglevel = "info"

wsgi_app = "jewelryshop.wsgi"
