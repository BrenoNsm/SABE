import factory
from datetime import date
from django.contrib.auth.models import User
from sabe.apps.audit.models import Audit
from sabe.apps.documents.models import Document
from sabe.apps.findings.models import Finding, Evidence
from sabe.apps.legal.models import LegalFramework


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'auditor{n:03d}')
    password = factory.PostGenerationMethodCall('set_password', 'teste123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class AuditFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Audit

    numero = factory.Sequence(lambda n: f'{n:03d}/{date.today().year}')
    exercicio = date.today().year
    processo = factory.Sequence(lambda n: f'PROC/{n:04d}/{date.today().year}')
    unidade_jurisdicionada = factory.Faker('company')
    responsavel = factory.Faker('name')
    objeto = factory.Faker('text', max_nb_chars=200)
    data_inicio = date(date.today().year, 1, 1)
    status = 'active'
    created_by = factory.SubFactory(UserFactory)


class DocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Document

    audit = factory.SubFactory(AuditFactory)
    filename = factory.Sequence(lambda n: f'document_{n:04d}.pdf')
    original_filename = factory.Sequence(lambda n: f'document_{n:04d}.pdf')
    file_size = 10240
    mime_type = 'application/pdf'
    sha256_hash = factory.Faker('sha256')
    page_count = 5
    ocr_status = 'completed'
    extracted_text = factory.Faker('text', max_nb_chars=500)
    uploaded_by = factory.SubFactory(UserFactory)


class FindingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Finding

    audit = factory.SubFactory(AuditFactory)
    title = factory.Faker('sentence', nb_words=6)
    description = factory.Faker('text', max_nb_chars=300)
    criterio = factory.Faker('text', max_nb_chars=200)
    condicao = factory.Faker('text', max_nb_chars=200)
    causa = factory.Faker('text', max_nb_chars=200)
    efeito = factory.Faker('text', max_nb_chars=200)
    recomendacao = factory.Faker('text', max_nb_chars=200)
    classificacao = factory.Iterator(['low', 'medium', 'high', 'critical'])
    created_by = factory.SubFactory(UserFactory)


class EvidenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Evidence

    document = factory.SubFactory(DocumentFactory)
    finding = factory.SubFactory(FindingFactory)
    page_number = factory.Faker('random_int', min=1, max=100)
    captured_text = factory.Faker('text', max_nb_chars=200)
    coordinates = {'x': 10, 'y': 20, 'width': 100, 'height': 50}
    hash = factory.Faker('sha256')
    created_by = factory.SubFactory(UserFactory)


class LegalFrameworkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LegalFramework

    tipo = factory.Iterator(['lei', 'decreto', 'resolucao', 'in', 'acordao'])
    numero = factory.Sequence(lambda n: f'{n:04d}/{date.today().year}')
    ementa = factory.Faker('text', max_nb_chars=100)
    texto = factory.Faker('text', max_nb_chars=500)
