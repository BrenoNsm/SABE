import logging

from django.contrib.postgres.search import SearchVector

from .models import Audit

logger = logging.getLogger(__name__)


def update_audit_search_vector(instance):
    sv = SearchVector(
        'numero', 'processo', 'unidade_jurisdicionada',
        'responsavel', 'objeto', 'observacoes',
        config='portuguese'
    )
    type(instance).objects.filter(pk=instance.pk).update(search_vector=sv)
