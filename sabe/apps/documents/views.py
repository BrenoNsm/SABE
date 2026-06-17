import os
import logging

from django.views.generic import DetailView, CreateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse

from .models import Document
from sabe.apps.audit.models import Audit
from .services import calculate_sha256, process_document, DocumentProcessingError
from sabe.apps.audit_log.services import log_action

logger = logging.getLogger(__name__)


class DocumentUploadView(LoginRequiredMixin, CreateView):
    model = Document
    fields = ['file']
    template_name = 'documents/upload.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['audit'] = get_object_or_404(Audit, pk=self.kwargs['audit_id'])
        return context

    def get_success_url(self):
        return reverse('audit:detail', kwargs={'pk': self.kwargs['audit_id']})

    def form_valid(self, form):
        audit = get_object_or_404(Audit, pk=self.kwargs['audit_id'])
        form.instance.audit = audit
        form.instance.uploaded_by = self.request.user

        file = self.request.FILES['file']
        form.instance.original_filename = file.name
        form.instance.filename = file.name
        form.instance.file_size = file.size
        form.instance.mime_type = file.content_type or 'application/pdf'

        response = super().form_valid(form)

        sha256 = calculate_sha256(self.object.file.path)
        Document.objects.filter(pk=self.object.pk).update(sha256_hash=sha256)

        log_action(
            self.request.user, 'upload', 'Document', self.object.id,
            f'Documento enviado: {file.name} para auditoria {audit.numero}/{audit.exercicio}',
            self.request
        )
        messages.success(self.request, 'Documento enviado com sucesso.')

        try:
            process_document(self.object.pk)
            messages.info(self.request, 'Documento processado automaticamente.')
        except DocumentProcessingError as e:
            logger.error(f'Erro no processamento automático: {e}')
            messages.warning(self.request, 'Documento enviado, mas o processamento falhou.')

        return response


class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'documents/detail.html'
    context_object_name = 'doc'


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    template_name = 'documents/confirm_delete.html'

    def get_success_url(self):
        return reverse('audit:detail', kwargs={'pk': self.object.audit_id})

    def delete(self, request, *args, **kwargs):
        doc = self.get_object()
        log_action(
            request.user, 'delete', 'Document', doc.id,
            f'Documento excluído: {doc.original_filename}',
            request
        )
        messages.success(request, 'Documento excluído com sucesso.')
        return super().delete(request, *args, **kwargs)


class DocumentProcessView(LoginRequiredMixin, View):
    def post(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        try:
            process_document(pk)
            log_action(
                request.user, 'ocr', 'Document', pk,
                f'Documento reprocessado: {document.original_filename}',
                request
            )
            messages.success(request, 'Documento processado com sucesso.')
        except DocumentProcessingError as e:
            messages.error(request, f'Erro no processamento: {e}')
        return redirect('audit:detail', pk=document.audit_id)


class PDFViewerView(LoginRequiredMixin, View):
    def get(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        return render(request, 'documents/viewer.html', {
            'document': document,
            'pdf_url': document.file.url,
            'audit': document.audit,
        })
