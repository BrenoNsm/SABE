import logging

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q

from .models import Audit
from sabe.apps.audit_log.services import log_action

logger = logging.getLogger(__name__)


class AuditListView(LoginRequiredMixin, ListView):
    model = Audit
    template_name = 'audit/list.html'
    context_object_name = 'audits'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('search', '')
        status_filter = self.request.GET.get('status', '')
        if search:
            qs = qs.filter(
                Q(numero__icontains=search) |
                Q(unidade_jurisdicionada__icontains=search) |
                Q(processo__icontains=search) |
                Q(responsavel__icontains=search)
            )
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class AuditCreateView(LoginRequiredMixin, CreateView):
    model = Audit
    template_name = 'audit/form.html'
    fields = [
        'numero', 'exercicio', 'processo', 'unidade_jurisdicionada',
        'responsavel', 'objeto', 'data_inicio', 'data_encerramento', 'observacoes'
    ]
    success_url = reverse_lazy('audit:list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        log_action(
            self.request.user, 'create', 'Audit', self.object.id,
            f'Auditoria criada: {self.object.numero}/{self.object.exercicio}',
            self.request
        )
        messages.success(self.request, 'Auditoria criada com sucesso.')
        return response


class AuditDetailView(LoginRequiredMixin, DetailView):
    model = Audit
    template_name = 'audit/detail.html'
    context_object_name = 'audit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = self.object.documents.all()
        context['findings'] = self.object.findings.all()
        context['reports'] = self.object.reports.all()
        return context


class AuditUpdateView(LoginRequiredMixin, UpdateView):
    model = Audit
    template_name = 'audit/form.html'
    fields = [
        'numero', 'exercicio', 'processo', 'unidade_jurisdicionada',
        'responsavel', 'objeto', 'data_inicio', 'data_encerramento', 'observacoes', 'status'
    ]
    success_url = reverse_lazy('audit:list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        log_action(
            self.request.user, 'update', 'Audit', self.object.id,
            f'Auditoria atualizada: {self.object.numero}/{self.object.exercicio}',
            self.request
        )
        messages.success(self.request, 'Auditoria atualizada com sucesso.')
        return response


class AuditDeleteView(LoginRequiredMixin, DeleteView):
    model = Audit
    template_name = 'audit/confirm_delete.html'
    success_url = reverse_lazy('audit:list')

    def delete(self, request, *args, **kwargs):
        audit = self.get_object()
        log_action(
            request.user, 'delete', 'Audit', audit.id,
            f'Auditoria excluída: {audit.numero}/{audit.exercicio}',
            request
        )
        messages.success(request, 'Auditoria excluída com sucesso.')
        return super().delete(request, *args, **kwargs)


class AuditDuplicateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        original = get_object_or_404(Audit, pk=pk)
        new_audit = Audit(
            numero=f'{original.numero}-copia',
            exercicio=original.exercicio,
            processo=original.processo,
            unidade_jurisdicionada=original.unidade_jurisdicionada,
            responsavel=original.responsavel,
            objeto=original.objeto,
            data_inicio=original.data_inicio,
            observacoes=f'Duplicata de {original.numero}/{original.exercicio}',
            created_by=request.user,
        )
        new_audit.save()
        log_action(
            request.user, 'create', 'Audit', new_audit.id,
            f'Auditoria duplicada de {original.numero}/{original.exercicio}',
            request
        )
        messages.success(request, 'Auditoria duplicada com sucesso.')
        return redirect('audit:detail', pk=new_audit.pk)


class AuditCloseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        audit = get_object_or_404(Audit, pk=pk)
        audit.status = 'closed'
        audit.updated_by = request.user
        audit.save(update_fields=['status', 'updated_by'])
        log_action(
            request.user, 'update', 'Audit', audit.id,
            f'Auditoria encerrada: {audit.numero}/{audit.exercicio}',
            request
        )
        messages.success(request, 'Auditoria encerrada com sucesso.')
        return redirect('audit:detail', pk=audit.pk)
