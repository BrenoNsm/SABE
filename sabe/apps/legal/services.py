import logging

from django.contrib.postgres.search import SearchVector

from .models import LegalFramework

logger = logging.getLogger(__name__)


def update_legal_search_vector(instance):
    sv = SearchVector('numero', 'ementa', 'texto', config='portuguese')
    LegalFramework.objects.filter(pk=instance.pk).update(search_vector=sv)


def create_legal_framework(tipo, numero, ementa='', texto=''):
    obj, created = LegalFramework.objects.get_or_create(
        tipo=tipo,
        numero=numero,
        defaults={'ementa': ementa, 'texto': texto}
    )
    if created:
        update_legal_search_vector(obj)
        logger.info(f'Fundamentação legal criada: {obj}')
    return obj, created
