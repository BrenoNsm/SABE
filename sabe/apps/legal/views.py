import logging

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django import forms

from .models import LegalFramework
from sabe.apps.audit_log.services import log_action

logger = logging.getLogger(__name__)


class LegalFrameworkListView(LoginRequiredMixin, ListView):
    model = LegalFramework
    template_name = 'legal/list.html'
    context_object_name = 'frameworks'
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset()
        tipo = self.request.GET.get('tipo', '')
        search = self.request.GET.get('search', '')
        if tipo:
            qs = qs.filter(tipo=tipo)
        if search:
            qs = qs.filter(numero__icontains=search) | qs.filter(ementa__icontains=search)
        return qs


class LegalFrameworkCreateView(LoginRequiredMixin, CreateView):
    model = LegalFramework
    template_name = 'legal/form.html'
    fields = ['tipo', 'numero', 'ementa', 'texto']
    success_url = reverse_lazy('legal:list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['tipo'] = forms.ChoiceField(
            label='Tipo', choices=LegalFramework.TIPO_CHOICES
        )
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(
            self.request.user, 'create', 'LegalFramework', self.object.id,
            f'Fundamentação legal criada: {self.object}',
            self.request
        )
        messages.success(self.request, 'Fundamentação legal cadastrada com sucesso.')
        return response


class LegalFrameworkUpdateView(LoginRequiredMixin, UpdateView):
    model = LegalFramework
    template_name = 'legal/form.html'
    fields = ['tipo', 'numero', 'ementa', 'texto']
    success_url = reverse_lazy('legal:list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['tipo'] = forms.ChoiceField(
            label='Tipo', choices=LegalFramework.TIPO_CHOICES
        )
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(
            self.request.user, 'update', 'LegalFramework', self.object.id,
            f'Fundamentação legal atualizada: {self.object}',
            self.request
        )
        messages.success(self.request, 'Fundamentação legal atualizada com sucesso.')
        return response


class LegalFrameworkDeleteView(LoginRequiredMixin, DeleteView):
    model = LegalFramework
    template_name = 'legal/confirm_delete.html'
    success_url = reverse_lazy('legal:list')

    def delete(self, request, *args, **kwargs):
        framework = self.get_object()
        log_action(
            request.user, 'delete', 'LegalFramework', framework.id,
            f'Fundamentação legal excluída: {framework}',
            request
        )
        messages.success(request, 'Fundamentação legal excluída com sucesso.')
        return super().delete(request, *args, **kwargs)
