import pytest
from datetime import date
from django.contrib.auth.models import User
from django.db import transaction
from sabe.apps.audit.models import Audit


class TestAuditModel:
    def test_create_audit(self, auditor_user):
        audit = Audit.objects.create(
            numero='TEST/2026',
            exercicio=2026,
            processo='TEST/2026',
            unidade_jurisdicionada='Unidade Teste',
            responsavel='Responsável Teste',
            objeto='Auditoria de teste',
            data_inicio=date(2026, 1, 1),
            created_by=auditor_user,
        )
        assert audit.numero == 'TEST/2026'
        assert audit.exercicio == 2026
        assert audit.status == 'active'
        assert str(audit) == 'TEST/2026 - Unidade Teste'
        assert audit.created_by == auditor_user

    def test_audit_default_status(self, auditor_user):
        audit = Audit.objects.create(
            numero='DEFAULT/2026',
            exercicio=2026,
            unidade_jurisdicionada='Teste',
            responsavel='Teste',
            objeto='Teste',
            data_inicio=date(2026, 1, 1),
            created_by=auditor_user,
        )
        assert audit.status == 'active'

    def test_audit_unique_numero(self, auditor_user):
        Audit.objects.create(
            numero='UNIQUE/2026',
            exercicio=2026,
            unidade_jurisdicionada='Teste',
            responsavel='Teste',
            objeto='Teste',
            data_inicio=date(2026, 1, 1),
            created_by=auditor_user,
        )
        with pytest.raises(Exception):
            Audit.objects.create(
                numero='UNIQUE/2026',
                exercicio=2026,
                unidade_jurisdicionada='Outra',
                responsavel='Outro',
                objeto='Teste',
                data_inicio=date(2026, 1, 1),
                created_by=auditor_user,
            )

    def test_audit_exercicio_validators(self, auditor_user):
        with pytest.raises(Exception):
            Audit.objects.create(
                numero='INVALID/1899',
                exercicio=1899,
                unidade_jurisdicionada='Teste',
                responsavel='Teste',
                objeto='Teste',
                data_inicio=date(1899, 1, 1),
                created_by=auditor_user,
            )

    def test_audit_str(self, auditor_user):
        audit = Audit.objects.create(
            numero='STR/2026',
            exercicio=2026,
            unidade_jurisdicionada='Unidade para String',
            responsavel='Teste',
            objeto='Teste',
            data_inicio=date(2026, 1, 1),
            created_by=auditor_user,
        )
        expected = 'STR/2026 - Unidade para String'
        assert str(audit) == expected

    def test_audit_ordering(self, auditor_user):
        Audit.objects.create(
            numero='B/2026', exercicio=2026,
            unidade_jurisdicionada='A', responsavel='A', objeto='A',
            data_inicio=date(2026, 1, 1), created_by=auditor_user,
        )
        Audit.objects.create(
            numero='A/2026', exercicio=2026,
            unidade_jurisdicionada='B', responsavel='B', objeto='B',
            data_inicio=date(2026, 1, 1), created_by=auditor_user,
        )
        audits = list(Audit.objects.all())
        assert audits[0].numero == 'A/2026'
        assert audits[1].numero == 'B/2026'
