import pytest
from datetime import date
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from sabe.apps.audit.models import Audit


class TestAuditViews:
    def test_login_required(self, client):
        response = client.get(reverse('audit:list'))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url

    def test_login_success(self, client, auditor_user):
        response = client.post(reverse('login'), {
            'username': 'auditor_teste',
            'password': 'teste123',
        })
        assert response.status_code == 302

    def test_login_failure(self, client):
        response = client.post(reverse('login'), {
            'username': 'invalido',
            'password': 'invalida',
        })
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    def test_audit_list_view(self, client, sample_audit):
        client.force_login(sample_audit.created_by)
        response = client.get(reverse('audit:list'))
        assert response.status_code == 200
        assert 'audits' in response.context
        assert sample_audit in response.context['audits']

    def test_audit_create_view(self, client, auditor_user):
        client.force_login(auditor_user)
        response = client.get(reverse('audit:create'))
        assert response.status_code == 200

        response = client.post(reverse('audit:create'), {
            'numero': 'NOVO/2026',
            'exercicio': 2026,
            'processo': 'NOVO/2026',
            'unidade_jurisdicionada': 'Nova Unidade',
            'responsavel': 'Novo Responsável',
            'objeto': 'Nova auditoria de teste',
            'data_inicio': '2026-01-01',
        })
        assert response.status_code == 302

    def test_audit_detail_view(self, client, sample_audit):
        client.force_login(sample_audit.created_by)
        response = client.get(reverse('audit:detail', kwargs={'pk': sample_audit.pk}))
        assert response.status_code == 200
        assert response.context['audit'] == sample_audit

    def test_audit_update_view(self, client, sample_audit):
        client.force_login(sample_audit.created_by)
        response = client.post(
            reverse('audit:update', kwargs={'pk': sample_audit.pk}),
            {
                'numero': sample_audit.numero,
                'exercicio': sample_audit.exercicio,
                'unidade_jurisdicionada': 'Unidade Atualizada',
                'responsavel': 'Responsável Atualizado',
                'objeto': 'Objeto atualizado',
                'data_inicio': '2026-01-01',
            }
        )
        assert response.status_code == 302
        sample_audit.refresh_from_db()
        assert sample_audit.unidade_jurisdicionada == 'Unidade Atualizada'

    def test_audit_delete_view(self, client, sample_audit):
        client.force_login(sample_audit.created_by)
        response = client.post(
            reverse('audit:delete', kwargs={'pk': sample_audit.pk})
        )
        assert response.status_code == 302
        assert not Audit.objects.filter(pk=sample_audit.pk).exists()

    def test_audit_duplicate_view(self, client, sample_audit):
        client.force_login(sample_audit.created_by)
        response = client.post(
            reverse('audit:duplicate', kwargs={'pk': sample_audit.pk})
        )
        assert response.status_code == 302
        assert Audit.objects.filter(numero=f'{sample_audit.numero}-copia').exists()

    def test_audit_close_view(self, client, sample_audit):
        client.force_login(sample_audit.created_by)
        response = client.post(
            reverse('audit:close', kwargs={'pk': sample_audit.pk})
        )
        assert response.status_code == 302
        sample_audit.refresh_from_db()
        assert sample_audit.status == 'closed'
