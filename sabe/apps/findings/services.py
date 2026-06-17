import hashlib
import json
import logging

from django.db import transaction
from django.contrib.postgres.search import SearchVector

from .models import Evidence, Finding

logger = logging.getLogger(__name__)


def create_evidence(document, finding, page_number, captured_text, coordinates=None,
                    created_by=None):
    evidence_data = {
        'document_id': document.id if hasattr(document, 'id') else document,
        'finding_id': finding.id if hasattr(finding, 'id') else finding,
        'page_number': page_number,
        'captured_text': captured_text,
        'coordinates': coordinates or {},
    }

    hash_input = f'{evidence_data["document_id"]}|{evidence_data["finding_id"]}|{page_number}|{captured_text}|{coordinates}'
    evidence_data['hash'] = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

    if created_by:
        evidence_data['created_by'] = created_by

    evidence = Evidence.objects.create(**evidence_data)
    update_finding_search_vector(evidence.finding)
    logger.info(
        f'Evidência criada: doc={evidence_data["document_id"]}, '
        f'finding={evidence_data["finding_id"]}, page={page_number}'
    )
    return evidence


def update_finding_search_vector(finding):
    evidence_texts = finding.evidences.values_list('captured_text', flat=True)
    full_text = ' '.join([
        finding.title, finding.description, finding.criterio,
        finding.condicao, finding.causa, finding.efeito,
        finding.recomendacao, ' '.join(evidence_texts)
    ])
    sv = SearchVector('title', 'description', 'criterio',
                      'condicao', 'causa', 'efeito',
                      'recomendacao', config='portuguese')
    Finding.objects.filter(pk=finding.pk).update(search_vector=sv)
