import logging
import time

from django.conf import settings


logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'

        if not settings.DEBUG:
            if hasattr(settings, 'SECURE_HSTS_SECONDS') and settings.SECURE_HSTS_SECONDS:
                response['Strict-Transport-Security'] = (
                    f'max-age={settings.SECURE_HSTS_SECONDS}'
                    f'{"; includeSubDomains" if getattr(settings, "SECURE_HSTS_INCLUDE_SUBDOMAINS", False) else ""}'
                    f'{"; preload" if getattr(settings, "SECURE_HSTS_PRELOAD", False) else ""}'
                )

        if hasattr(settings, 'CSP_DEFAULT_SRC'):
            csp_parts = []
            csp_directives = {
                'default-src': getattr(settings, 'CSP_DEFAULT_SRC', []),
                'script-src': getattr(settings, 'CSP_SCRIPT_SRC', []),
                'style-src': getattr(settings, 'CSP_STYLE_SRC', []),
                'img-src': getattr(settings, 'CSP_IMG_SRC', []),
                'font-src': getattr(settings, 'CSP_FONT_SRC', []),
                'connect-src': getattr(settings, 'CSP_CONNECT_SRC', []),
                'frame-src': getattr(settings, 'CSP_FRAME_SRC', []),
                'object-src': getattr(settings, 'CSP_OBJECT_SRC', []),
                'worker-src': getattr(settings, 'CSP_WORKER_SRC', []),
            }
            if hasattr(settings, 'CSP_FORM_ACTION'):
                csp_directives['form-action'] = settings.CSP_FORM_ACTION
            if hasattr(settings, 'CSP_BASE_URI'):
                csp_directives['base-uri'] = settings.CSP_BASE_URI

            for directive, sources in csp_directives.items():
                if sources:
                    csp_parts.append(f"{directive} {' '.join(sources)}")

            if csp_parts:
                response['Content-Security-Policy'] = '; '.join(csp_parts)

        return response


class DebugRequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        if settings.DEBUG:
            logger.info(
                f'{request.method} {request.path} -> {response.status_code} '
                f'({duration:.3f}s)'
            )
        return response
