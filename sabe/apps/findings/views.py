import logging

from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django import forms

from .models import Finding, Evidence
from sabe.apps.legal.models import FindingLegalFramework
from sabe.apps.audit.models import Audit
from sabe.apps.documents.models import Document
from sabe.apps.legal.models import LegalFramework
from .services import create_evidence
from sabe.apps.audit_log.services import log_action

logger = logging.getLogger(__name__)


class FindingCreateView(LoginRequiredMixin, CreateView):
    model = Finding
    template_name = 'findings/form.html'
    fields = [
        'title', 'description', 'criterio', 'condicao',
        'causa', 'efeito', 'recomendacao', 'classificacao'
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['audit'] = get_object_or_404(Audit, pk=self.kwargs['audit_id'])
        return context

    def get_success_url(self):
        return reverse('audit:detail', kwargs={'pk': self.object.audit_id})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['legal_frameworks'] = forms.ModelMultipleChoiceField(
            label='Fundamentações Legais',
            queryset=LegalFramework.objects.all(),
            required=False,
            widget=forms.CheckboxSelectMultiple,
        )
        return form

    def form_valid(self, form):
        audit = get_object_or_404(Audit, pk=self.kwargs['audit_id'])
        form.instance.audit = audit
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        for lf in form.cleaned_data.get('legal_frameworks', []):
            FindingLegalFramework.objects.create(
                finding=self.object, legal_framework=lf
            )
        log_action(
            self.request.user, 'create', 'Finding', self.object.id,
            f'Achado criado: {self.object.title}',
            self.request
        )
        messages.success(self.request, 'Achado criado com sucesso.')
        return response


class FindingDetailView(LoginRequiredMixin, DetailView):
    model = Finding
    template_name = 'findings/detail.html'
    context_object_name = 'finding'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['evidences'] = self.object.evidences.select_related('document').all()
        context['legal_frameworks'] = self.object.legal_frameworks.select_related('legal_framework').all()
        return context


class FindingUpdateView(LoginRequiredMixin, UpdateView):
    model = Finding
    template_name = 'findings/form.html'
    fields = [
        'title', 'description', 'criterio', 'condicao',
        'causa', 'efeito', 'recomendacao', 'classificacao'
    ]

    def get_success_url(self):
        return reverse('findings:detail', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['legal_frameworks'] = forms.ModelMultipleChoiceField(
            label='Fundamentações Legais',
            queryset=LegalFramework.objects.all(),
            required=False,
            widget=forms.CheckboxSelectMultiple,
            initial=self.object.legal_frameworks.values_list('legal_framework_id', flat=True),
        )
        return form

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        self.object.legal_frameworks.exclude(
            legal_framework__in=form.cleaned_data.get('legal_frameworks', [])
        ).delete()
        existing = set(
            self.object.legal_frameworks.values_list('legal_framework_id', flat=True)
        )
        for lf in form.cleaned_data.get('legal_frameworks', []):
            if lf.pk not in existing:
                FindingLegalFramework.objects.create(
                    finding=self.object, legal_framework=lf
                )
        log_action(
            self.request.user, 'update', 'Finding', self.object.id,
            f'Achado atualizado: {self.object.title}',
            self.request
        )
        messages.success(self.request, 'Achado atualizado com sucesso.')
        return response


class FindingDeleteView(LoginRequiredMixin, DeleteView):
    model = Finding
    template_name = 'findings/confirm_delete.html'

    def get_success_url(self):
        return reverse('audit:detail', kwargs={'pk': self.object.audit_id})

    def delete(self, request, *args, **kwargs):
        finding = self.get_object()
        log_action(
            request.user, 'delete', 'Finding', finding.id,
            f'Achado excluído: {finding.title}',
            request
        )
        messages.success(request, 'Achado excluído com sucesso.')
        return super().delete(request, *args, **kwargs)


class EvidenceCreateView(LoginRequiredMixin, View):
    def post(self, request):
        document_id = request.POST.get('document_id')
        finding_id = request.POST.get('finding_id')
        page_number = request.POST.get('page_number')
        captured_text = request.POST.get('captured_text')
        coordinates = request.POST.get('coordinates', '{}')

        if not all([document_id, finding_id, page_number, captured_text]):
            return JsonResponse({'error': 'Campos obrigatórios faltando'}, status=400)

        import json
        try:
            coords = json.loads(coordinates)
        except (ValueError, TypeError):
            coords = {}

        document = get_object_or_404(Document, pk=document_id)
        finding = get_object_or_404(Finding, pk=finding_id)

        evidence = create_evidence(
            document=document,
            finding=finding,
            page_number=int(page_number),
            captured_text=captured_text,
            coordinates=coords,
            created_by=request.user,
        )

        log_action(
            request.user, 'create', 'Evidence', evidence.id,
            f'Evidência criada para achado: {finding.title}',
            request
        )

        return JsonResponse({
            'id': evidence.id,
            'hash': evidence.hash,
            'page_number': evidence.page_number,
            'captured_text': evidence.captured_text[:100],
            'created_at': evidence.created_at.isoformat(),
        })


class EvidenceDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        evidence = get_object_or_404(Evidence, pk=pk)
        finding_id = evidence.finding_id
        log_action(
            request.user, 'delete', 'Evidence', pk,
            f'Evidência excluída do achado: {evidence.finding.title}',
            request
        )
        evidence.delete()
        messages.success(request, 'Evidência excluída com sucesso.')
        return redirect('findings:detail', pk=finding_id)
