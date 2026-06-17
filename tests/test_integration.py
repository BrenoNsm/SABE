import pytest
from datetime import date
from django.test import Client
from django.urls import reverse
from io import BytesIO
from sabe.apps.audit.models import Audit
from sabe.apps.documents.models import Document
from sabe.apps.documents.services import calculate_sha256, has_meaningful_text


class TestIntegrationFullFlow:
    def test_complete_audit_flow(self, client, auditor_user):
        client.force_login(auditor_user)

        # 1. Criar auditoria
        response = client.post(reverse('audit:create'), {
            'numero': 'INTEGRACAO/2026',
            'exercicio': 2026,
            'processo': 'INT/2026',
            'unidade_jurisdicionada': 'Secretaria de Integração',
            'responsavel': 'Auditor Chefe',
            'objeto': 'Auditoria completa de integração',
            'data_inicio': '2026-01-01',
        })
        assert response.status_code == 302
        audit = Audit.objects.get(numero='INTEGRACAO/2026')

        # 2. Fazer upload de documento
        pdf_content = b'%PDF-1.4 fake pdf content for testing'
        response = client.post(
            reverse('documents:upload', kwargs={'audit_id': audit.pk}),
            {'file': BytesIO(pdf_content)}
        )
        # Deve redirecionar (302) mesmo sem arquivo real
        assert response.status_code == 302

        # 3. Criar achado
        response = client.post(
            reverse('findings:create', kwargs={'audit_id': audit.pk}),
            {
                'title': 'Achado Integração',
                'description': 'Descrição do achado de integração',
                'criterio': 'Critério de integração',
                'condicao': 'Condição encontrada',
                'causa': 'Causa identificada',
                'efeito': 'Efeito observado',
                'recomendacao': 'Recomendar correção',
                'classificacao': 'critical',
            }
        )
        assert response.status_code == 302

        # 4. Verificar achado criado
        from sabe.apps.findings.models import Finding
        finding = Finding.objects.get(title='Achado Integração')
        assert finding.causa == 'Causa identificada'

        # 5. Gerar relatório
        response = client.post(
            reverse('reports:generate', kwargs={'audit_id': audit.pk}),
            {'format': 'docx'}
        )
        assert response.status_code == 302

        # 6. Verificar logs
        from sabe.apps.audit_log.models import AuditLog
        assert AuditLog.objects.filter(
            model_name='Audit', object_id=str(audit.pk)
        ).exists()

        # 7. Encerrar auditoria
        response = client.post(
            reverse('audit:close', kwargs={'pk': audit.pk})
        )
        assert response.status_code == 302
        audit.refresh_from_db()
        assert audit.status == 'closed'


class TestServicesIntegration:
    def test_sha256_consistency(self, tmp_path):
        content = b'Conteudo consistente para hash SHA256'
        file1 = tmp_path / 'test1.txt'
        file2 = tmp_path / 'test2.txt'
        file1.write_bytes(content)
        file2.write_bytes(content)
        hash1 = calculate_sha256(str(file1))
        hash2 = calculate_sha256(str(file2))
        assert hash1 == hash2

    def test_has_meaningful_text_different_inputs(self):
        assert has_meaningful_text(' ' * 200) is False
        long_text = 'Texto com conteúdo significativo ' * 20
        assert has_meaningful_text(long_text) is True
