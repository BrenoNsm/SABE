import pytest
from datetime import date
from sabe.apps.findings.models import Finding, Evidence
from sabe.apps.audit.models import Audit


class TestFindingModel:
    def test_create_finding(self, sample_audit, auditor_user):
        finding = Finding.objects.create(
            audit=sample_audit,
            title='Achado de Teste',
            description='Descrição do achado de teste',
            criterio='Critério de teste',
            classificacao='high',
            created_by=auditor_user,
        )
        assert finding.title == 'Achado de Teste'
        assert finding.classificacao == 'high'
        assert finding.get_classificacao_display() == 'Alta'
        assert str(finding) == 'Achado de Teste'
        assert finding.created_by == auditor_user

    def test_finding_classification_choices(self, sample_audit, auditor_user):
        for classificacao in ['low', 'medium', 'high', 'critical']:
            finding = Finding.objects.create(
                audit=sample_audit,
                title=f'Teste {classificacao}',
                description='Teste',
                classificacao=classificacao,
                created_by=auditor_user,
            )
            assert finding.classificacao == classificacao

    def test_finding_default_classification(self, sample_audit, auditor_user):
        finding = Finding.objects.create(
            audit=sample_audit,
            title='Classificação Padrão',
            description='Teste',
            created_by=auditor_user,
        )
        assert finding.classificacao == 'medium'

    def test_finding_all_fields(self, sample_audit, auditor_user):
        finding = Finding.objects.create(
            audit=sample_audit,
            title='Achado Completo',
            description='Descrição completa',
            criterio='Critério',
            condicao='Condição',
            causa='Causa',
            efeito='Efeito',
            recomendacao='Recomendação',
            classificacao='critical',
            created_by=auditor_user,
        )
        assert finding.criterio == 'Critério'
        assert finding.condicao == 'Condição'
        assert finding.causa == 'Causa'
        assert finding.efeito == 'Efeito'
        assert finding.recomendacao == 'Recomendação'


class TestEvidenceModel:
    def test_create_evidence(self, sample_audit, auditor_user):
        from sabe.apps.documents.models import Document
        finding = Finding.objects.create(
            audit=sample_audit, title='Achado Evidência',
            description='Teste', created_by=auditor_user,
        )
        doc = Document.objects.create(
            audit=sample_audit, filename='doc.pdf',
            original_filename='doc.pdf', file_size=100,
            sha256_hash='b' * 64, uploaded_by=auditor_user,
        )
        evidence = Evidence.objects.create(
            document=doc,
            finding=finding,
            page_number=1,
            captured_text='Texto capturado da evidência',
            coordinates={'x': 10, 'y': 20},
            hash='test_hash_123',
            created_by=auditor_user,
        )
        assert evidence.page_number == 1
        assert evidence.captured_text == 'Texto capturado da evidência'
        assert evidence.hash == 'test_hash_123'
        assert str(evidence) == f'Evidência p.1 - doc.pdf'

    def test_evidence_ordering(self, sample_audit, auditor_user):
        from sabe.apps.documents.models import Document
        finding = Finding.objects.create(
            audit=sample_audit, title='Achado',
            description='Teste', created_by=auditor_user,
        )
        doc = Document.objects.create(
            audit=sample_audit, filename='doc.pdf',
            original_filename='doc.pdf', file_size=100,
            sha256_hash='c' * 64, uploaded_by=auditor_user,
        )
        ev1 = Evidence.objects.create(
            document=doc, finding=finding, page_number=2,
            captured_text='Segunda página',
            hash='h1', created_by=auditor_user,
        )
        ev2 = Evidence.objects.create(
            document=doc, finding=finding, page_number=1,
            captured_text='Primeira página',
            hash='h2', created_by=auditor_user,
        )
        evidences = list(Evidence.objects.all())
        assert evidences[0].page_number == 1
        assert evidences[1].page_number == 2
