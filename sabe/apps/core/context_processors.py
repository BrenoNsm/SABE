from django.conf import settings as django_settings


def settings(request):
    return {
        'APP_NAME': 'SABE',
        'APP_TITLE': 'Sistema de Auditoria Baseado em Evidências',
        'INSTITUTION': 'Tribunal de Contas do Estado de Roraima',
        'INSTITUTION_ACRONYM': 'TCE-RR',
        'DEBUG': django_settings.DEBUG,
        'STATIC_URL': django_settings.STATIC_URL,
        'MEDIA_URL': django_settings.MEDIA_URL,
    }
