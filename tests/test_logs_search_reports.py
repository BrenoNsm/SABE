import pytest
from datetime import date
from django.test import Client
from django.urls import reverse
from sabe.apps.audit_log.models import AuditLog
from sabe.apps.audit_log.services import log_action


class TestAuditLogModel:
    def test_create_log(self, auditor_user):
        log = AuditLog.objects.create(
            user=auditor_user,
            action='login',
            model_name='User',
            object_id=str(auditor_user.id),
            details='Login de teste',
            ip_address='127.0.0.1',
        )
        assert log.action == 'login'
        assert log.user == auditor_user
        assert str(log) is not None

    def test_log_str_without_user(self):
        log = AuditLog.objects.create(
            action='login',
            model_name='User',
            details='Login do sistema',
        )
        assert 'Sistema' in str(log)

    def test_last_login_log(self, auditor_user):
        AuditLog.objects.create(
            user=auditor_user,
            action='login',
            model_name='User',
            object_id=str(auditor_user.id),
            details=f'Usuário {auditor_user.username} realizou login',
            ip_address='127.0.0.1',
        )
        assert AuditLog.objects.count() == 1


class TestAuditLogServices:
    def test_log_action_with_request(self, auditor_user, rf):
        request = rf.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        log_action(auditor_user, 'login', 'User', '1', 'Teste', request)
        assert AuditLog.objects.count() == 1
        log_entry = AuditLog.objects.first()
        assert log_entry.ip_address == '192.168.1.1'

    def test_log_action_without_request(self, auditor_user):
        log_action(auditor_user, 'logout', 'User', '1', 'Logout')
        assert AuditLog.objects.count() == 1
        log_entry = AuditLog.objects.first()
        assert log_entry.ip_address is None

    def test_all_action_types(self, auditor_user):
        for action, _ in AuditLog.ACTION_CHOICES:
            AuditLog.objects.create(
                user=auditor_user,
                action=action,
                details=f'Ação {action}',
            )
        assert AuditLog.objects.count() == len(AuditLog.ACTION_CHOICES)


class TestSearchViews:
    def test_search_view(self, client, sample_audit, auditor_user):
        client.force_login(auditor_user)
        response = client.get(reverse('search:search'))
        assert response.status_code == 200

    def test_search_with_query(self, client, sample_audit, auditor_user):
        client.force_login(auditor_user)
        response = client.get(
            reverse('search:search'),
            {'q': sample_audit.unidade_jurisdicionada}
        )
        assert response.status_code == 200
        assert 'results' in response.context
        assert response.context['query'] == sample_audit.unidade_jurisdicionada


class TestAuditLogViews:
    def test_log_list_view(self, client, auditor_user):
        AuditLog.objects.create(
            user=auditor_user,
            action='login',
            details='Teste de log',
        )
        client.force_login(auditor_user)
        response = client.get(reverse('logs:list'))
        assert response.status_code == 200
        assert 'logs' in response.context


class TestReportViews:
    def test_report_generate(self, client, sample_audit, auditor_user):
        client.force_login(auditor_user)
        response = client.post(
            reverse('reports:generate', kwargs={'audit_id': sample_audit.pk}),
            {'format': 'docx'}
        )
        assert response.status_code == 302
