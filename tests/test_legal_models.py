import pytest
from sabe.apps.legal.models import LegalFramework, FindingLegalFramework
from sabe.apps.findings.models import Finding


class TestLegalFrameworkModel:
    def test_create_legal_framework(self):
        lf = LegalFramework.objects.create(
            tipo='lei',
            numero='14.133/2021',
            ementa='Lei de Licitações',
            texto='Texto completo da lei',
        )
        assert lf.tipo == 'lei'
        assert lf.numero == '14.133/2021'
        assert str(lf) == 'Lei - 14.133/2021'

    def test_legal_framework_unique_together(self):
        LegalFramework.objects.create(
            tipo='lei', numero='TESTE/2026',
            ementa='Teste', texto='Teste',
        )
        with pytest.raises(Exception):
            LegalFramework.objects.create(
                tipo='lei', numero='TESTE/2026',
                ementa='Duplicado', texto='Teste',
            )

    def test_all_tipo_choices(self):
        for tipo, _ in LegalFramework.TIPO_CHOICES:
            lf = LegalFramework.objects.create(
                tipo=tipo, numero=f'{tipo}/TESTE',
                ementa=f'Teste {tipo}',
            )
            assert lf.tipo == tipo

    def test_legal_framework_ordering(self):
        LegalFramework.objects.create(tipo='lei', numero='B', ementa='B')
        LegalFramework.objects.create(tipo='lei', numero='A', ementa='A')
        lfs = list(LegalFramework.objects.all())
        assert lfs[0].numero == 'A'

    def test_finding_legal_framework_relationship(self, sample_audit, auditor_user):
        lf = LegalFramework.objects.create(
            tipo='lei', numero='REL/2026', ementa='Relacionamento',
        )
        finding = Finding.objects.create(
            audit=sample_audit, title='Achado Relacionado',
            description='Teste', created_by=auditor_user,
        )
        rel = FindingLegalFramework.objects.create(
            finding=finding, legal_framework=lf,
        )
        assert rel.finding == finding
        assert rel.legal_framework == lf
        assert str(rel) == f'Achado Relacionado -> Lei - REL/2026'
