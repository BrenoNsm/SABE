import pytest
from django.test import Client
from django.urls import reverse
from sabe.apps.findings.models import Finding
from sabe.apps.documents.models import Document
from sabe.apps.legal.models import LegalFramework, FindingLegalFramework


class TestFindingViews:
    def test_finding_create_view(self, client, sample_audit, auditor_user):
        client.force_login(auditor_user)
        response = client.get(
            reverse('findings:create', kwargs={'audit_id': sample_audit.pk})
        )
        assert response.status_code == 200

        response = client.post(
            reverse('findings:create', kwargs={'audit_id': sample_audit.pk}),
            {
                'title': 'Novo Achado Teste',
                'description': 'Descrição do achado de teste',
                'classificacao': 'medium',
            }
        )
        assert response.status_code == 302
        assert Finding.objects.filter(title='Novo Achado Teste').exists()

    def test_finding_detail_view(self, client, sample_audit, auditor_user):
        finding = Finding.objects.create(
            audit=sample_audit, title='Detalhe Achado',
            description='Detalhe', created_by=auditor_user,
        )
        client.force_login(auditor_user)
        response = client.get(
            reverse('findings:detail', kwargs={'pk': finding.pk})
        )
        assert response.status_code == 200
        assert response.context['finding'] == finding

    def test_finding_update_view(self, client, sample_audit, auditor_user):
        finding = Finding.objects.create(
            audit=sample_audit, title='Original',
            description='Original', created_by=auditor_user,
        )
        client.force_login(auditor_user)
        response = client.post(
            reverse('findings:update', kwargs={'pk': finding.pk}),
            {
                'title': 'Atualizado',
                'description': 'Descrição atualizada',
                'classificacao': 'high',
            }
        )
        assert response.status_code == 302
        finding.refresh_from_db()
        assert finding.title == 'Atualizado'
        assert finding.classificacao == 'high'

    def test_finding_delete_view(self, client, sample_audit, auditor_user):
        finding = Finding.objects.create(
            audit=sample_audit, title='Para Excluir',
            description='Excluir', created_by=auditor_user,
        )
        client.force_login(auditor_user)
        response = client.post(
            reverse('findings:delete', kwargs={'pk': finding.pk})
        )
        assert response.status_code == 302
        assert not Finding.objects.filter(pk=finding.pk).exists()

    def test_evidence_create(self, client, sample_audit, auditor_user):
        finding = Finding.objects.create(
            audit=sample_audit, title='Evidência Teste',
            description='Teste', created_by=auditor_user,
        )
        doc = Document.objects.create(
            audit=sample_audit, filename='ev.pdf',
            original_filename='ev.pdf', file_size=100,
            sha256_hash='d' * 64, uploaded_by=auditor_user,
        )
        client.force_login(auditor_user)
        response = client.post(
            reverse('findings:evidence_create'),
            {
                'document_id': doc.pk,
                'finding_id': finding.pk,
                'page_number': 1,
                'captured_text': 'Texto de evidência de teste',
                'coordinates': '{"x": 10, "y": 20}',
            }
        )
        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert data['id'] is not None
        assert data['page_number'] == 1


class TestLegalViews:
    def test_legal_list_view(self, client, auditor_user):
        LegalFramework.objects.create(
            tipo='lei', numero='TESTE/2026', ementa='Lei de teste',
        )
        client.force_login(auditor_user)
        response = client.get(reverse('legal:list'))
        assert response.status_code == 200
        assert 'frameworks' in response.context

    def test_legal_create_view(self, client, auditor_user):
        client.force_login(auditor_user)
        response = client.get(reverse('legal:create'))
        assert response.status_code == 200

        response = client.post(reverse('legal:create'), {
            'tipo': 'lei',
            'numero': 'NOVA/2026',
            'ementa': 'Nova lei de teste',
        })
        assert response.status_code == 302
        assert LegalFramework.objects.filter(numero='NOVA/2026').exists()

    def test_legal_update_view(self, client, auditor_user):
        lf = LegalFramework.objects.create(
            tipo='decreto', numero='DEC/2026', ementa='Decreto original',
        )
        client.force_login(auditor_user)
        response = client.post(
            reverse('legal:update', kwargs={'pk': lf.pk}),
            {
                'tipo': 'decreto',
                'numero': 'DEC/2026',
                'ementa': 'Decreto atualizado',
            }
        )
        assert response.status_code == 302
        lf.refresh_from_db()
        assert lf.ementa == 'Decreto atualizado'
