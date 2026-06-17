import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User


class TestLoginFunctional:
    def test_login_page_loads(self, client):
        response = client.get(reverse('login'))
        assert response.status_code == 200
        assert 'SABE' in response.content.decode()

    def test_successful_login_redirects(self, client, auditor_user):
        response = client.post(reverse('login'), {
            'username': 'auditor_teste',
            'password': 'teste123',
        }, follow=True)
        assert response.status_code == 200
        # Deve ser redirecionado para a lista de auditorias
        assert 'Auditorias' in response.content.decode()

    def test_logout(self, client, auditor_user):
        client.force_login(auditor_user)
        response = client.get(reverse('audit:list'))
        assert response.status_code == 200

        response = client.post(reverse('logout'), follow=True)
        assert response.status_code == 200
        # Não deve mais acessar páginas protegidas
        response = client.get(reverse('audit:list'))
        assert response.status_code == 302


class TestNavigationFunctional:
    def test_nav_links_authenticated(self, client, auditor_user):
        client.force_login(auditor_user)
        response = client.get(reverse('audit:list'))
        content = response.content.decode()
        assert 'Auditorias' in content
        assert 'Fundamentação Legal' in content
        assert 'Pesquisa' in content
        assert 'Logs' in content

    def test_admin_link(self, client, auditor_user):
        auditor_user.is_staff = True
        auditor_user.is_superuser = True
        auditor_user.save()
        client.force_login(auditor_user)
        response = client.get(reverse('audit:list'))
        assert 'Admin' in response.content.decode()


class TestCRUDFunctional:
    def test_audit_crud_flow(self, client, auditor_user):
        client.force_login(auditor_user)

        # Create
        response = client.post(reverse('audit:create'), {
            'numero': 'CRUD/2026',
            'exercicio': 2026,
            'processo': 'CRUD/2026',
            'unidade_jurisdicionada': 'CRUD Teste',
            'responsavel': 'Teste',
            'objeto': 'Teste CRUD completo',
            'data_inicio': '2026-01-01',
        })
        assert response.status_code == 302

        from sabe.apps.audit.models import Audit
        audit = Audit.objects.get(numero='CRUD/2026')

        # Read
        response = client.get(reverse('audit:detail', kwargs={'pk': audit.pk}))
        assert response.status_code == 200

        # Update
        response = client.post(
            reverse('audit:update', kwargs={'pk': audit.pk}),
            {
                'numero': 'CRUD/2026',
                'exercicio': 2026,
                'unidade_jurisdicionada': 'CRUD Atualizado',
                'responsavel': 'Teste',
                'objeto': 'Atualizado',
                'data_inicio': '2026-01-01',
            }
        )
        assert response.status_code == 302
        audit.refresh_from_db()
        assert audit.unidade_jurisdicionada == 'CRUD Atualizado'

        # Duplicate
        response = client.post(
            reverse('audit:duplicate', kwargs={'pk': audit.pk})
        )
        assert response.status_code == 302
        assert Audit.objects.filter(numero='CRUD/2026-copia').exists()

        # Close
        response = client.post(
            reverse('audit:close', kwargs={'pk': audit.pk})
        )
        assert response.status_code == 302
        audit.refresh_from_db()
        assert audit.status == 'closed'

        # Delete
        response = client.post(
            reverse('audit:delete', kwargs={'pk': audit.pk})
        )
        assert response.status_code == 302
        assert not Audit.objects.filter(pk=audit.pk).exists()

    def test_finding_crud_flow(self, client, sample_audit, auditor_user):
        client.force_login(auditor_user)

        # Create
        response = client.post(
            reverse('findings:create', kwargs={'audit_id': sample_audit.pk}),
            {
                'title': 'Finding CRUD',
                'description': 'CRUD test finding',
                'classificacao': 'low',
            }
        )
        assert response.status_code == 302

        from sabe.apps.findings.models import Finding
        finding = Finding.objects.get(title='Finding CRUD')

        # Read
        response = client.get(
            reverse('findings:detail', kwargs={'pk': finding.pk})
        )
        assert response.status_code == 200

        # Update
        response = client.post(
            reverse('findings:update', kwargs={'pk': finding.pk}),
            {
                'title': 'Finding CRUD Updated',
                'description': 'Updated',
                'classificacao': 'high',
            }
        )
        assert response.status_code == 302
        finding.refresh_from_db()
        assert finding.title == 'Finding CRUD Updated'

        # Delete
        response = client.post(
            reverse('findings:delete', kwargs={'pk': finding.pk})
        )
        assert response.status_code == 302
        assert not Finding.objects.filter(pk=finding.pk).exists()
