import logging

from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchRank

from sabe.apps.audit.models import Audit
from sabe.apps.documents.models import Document
from sabe.apps.findings.models import Finding, Evidence
from sabe.apps.legal.models import LegalFramework

logger = logging.getLogger(__name__)


class SearchView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        search_type = request.GET.get('type', 'all')

        results = {
            'audits': [],
            'documents': [],
            'findings': [],
            'legal': [],
            'total': 0,
        }

        if query:
            search_query = SearchQuery(query, config='portuguese')

            if search_type in ('all', 'audits'):
                audits = Audit.objects.filter(
                    Q(numero__icontains=query) |
                    Q(unidade_jurisdicionada__icontains=query) |
                    Q(processo__icontains=query) |
                    Q(objeto__icontains=query) |
                    Q(responsavel__icontains=query)
                )[:20]
                results['audits'] = audits

            if search_type in ('all', 'documents'):
                documents = Document.objects.filter(
                    Q(original_filename__icontains=query) |
                    Q(extracted_text__icontains=query) |
                    Q(sha256_hash__icontains=query)
                )[:20]
                results['documents'] = documents

            if search_type in ('all', 'findings'):
                findings = Finding.objects.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(criterio__icontains=query) |
                    Q(condicao__icontains=query) |
                    Q(causa__icontains=query) |
                    Q(efeito__icontains=query) |
                    Q(recomendacao__icontains=query)
                )[:20]
                results['findings'] = findings

            if search_type in ('all', 'legal'):
                legal = LegalFramework.objects.filter(
                    Q(numero__icontains=query) |
                    Q(ementa__icontains=query) |
                    Q(texto__icontains=query)
                )[:20]
                results['legal'] = legal

            results['total'] = (
                len(results['audits']) +
                len(results['documents']) +
                len(results['findings']) +
                len(results['legal'])
            )

        return render(request, 'search/results.html', {
            'query': query,
            'results': results,
            'search_type': search_type,
        })
