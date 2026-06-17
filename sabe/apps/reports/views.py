import os
import logging

from django.views.generic import View, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import FileResponse, HttpResponse
from django.conf import settings
from django.core.files import File

from .models import Report
from sabe.apps.audit.models import Audit
from sabe.apps.audit_log.services import log_action
from .services import generate_docx_report, generate_pdf_report

logger = logging.getLogger(__name__)


class ReportGenerateView(LoginRequiredMixin, View):
    def post(self, request, audit_id):
        audit = get_object_or_404(Audit, pk=audit_id)
        report_format = request.POST.get('format', 'docx')

        try:
            if report_format == 'docx':
                file_path = generate_docx_report(audit, request.user)
            else:
                file_path = generate_pdf_report(audit, request.user)

            relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
            report = Report.objects.create(
                audit=audit,
                title=f'Relatório de Auditoria - {audit.numero}/{audit.exercicio}',
                format=report_format,
                file=relative_path,
                generated_by=request.user,
            )

            log_action(
                request.user, 'report', 'Report', report.id,
                f'Relatório gerado para auditoria {audit.numero}/{audit.exercicio} ({report_format})',
                request
            )
            messages.success(request, 'Relatório gerado com sucesso.')
        except Exception as e:
            logger.exception(f'Erro ao gerar relatório: {e}')
            messages.error(request, f'Erro ao gerar relatório: {e}')

        return redirect('audit:detail', pk=audit_id)


class ReportDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        if report.file:
            return FileResponse(
                report.file.open('rb'),
                as_attachment=True,
                filename=os.path.basename(report.file.name),
            )
        messages.error(request, 'Arquivo do relatório não encontrado.')
        return redirect('audit:detail', pk=report.audit_id)


class ReportDeleteView(LoginRequiredMixin, DeleteView):
    model = Report
    template_name = 'reports/confirm_delete.html'

    def get_success_url(self):
        return reverse('audit:detail', kwargs={'pk': self.object.audit_id})

    def delete(self, request, *args, **kwargs):
        report = self.get_object()
        log_action(
            request.user, 'delete', 'Report', report.id,
            f'Relatório excluído: {report.title}',
            request
        )
        messages.success(request, 'Relatório excluído com sucesso.')
        return super().delete(request, *args, **kwargs)
