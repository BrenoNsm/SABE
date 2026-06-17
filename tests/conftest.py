import pytest
from django.contrib.auth.models import User
from django.test import TestCase


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username='admin', password='admin123', email='admin@tce.rr.gov.br'
    )


@pytest.fixture
def auditor_user(db):
    return User.objects.create_user(
        username='auditor_teste',
        password='teste123',
        first_name='Auditor',
        last_name='Teste',
    )


@pytest.fixture
def sample_audit(db, auditor_user):
    from sabe.apps.audit.models import Audit
    from datetime import date
    return Audit.objects.create(
        numero='001/2026',
        exercicio=2026,
        processo='001/2026',
        unidade_jurisdicionada='Secretaria Teste',
        responsavel='Responsável Teste',
        objeto='Objeto de teste',
        data_inicio=date(2026, 1, 1),
        created_by=auditor_user,
    )
