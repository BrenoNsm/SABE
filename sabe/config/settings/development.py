from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

MIDDLEWARE += [
    'sabe.apps.core.middleware.DebugRequestLoggingMiddleware',
]

# CSP relaxado para desenvolvimento
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'", "'unsafe-eval'", "https://cdn.tailwindcss.com", "https://cdnjs.cloudflare.com"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com"]
CSP_IMG_SRC = ["'self'", "data:", "blob:"]
CSP_FONT_SRC = ["'self'"]
CSP_CONNECT_SRC = ["'self'"]
CSP_FRAME_SRC = ["'self'"]
CSP_OBJECT_SRC = ["'none'"]
CSP_WORKER_SRC = ["'self'", "blob:"]

# Desabilitar HSTS em dev
SECURE_HSTS_SECONDS = 0
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
