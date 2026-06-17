import pytest
from datetime import date
from sabe.apps.audit.models import Audit
from sabe.apps.documents.models import Document
from sabe.apps.documents.services import (
    calculate_sha256, has_meaningful_text,
)


class TestDocumentModel:
    def test_create_document(self, sample_audit, auditor_user):
        doc = Document.objects.create(
            audit=sample_audit,
            filename='teste.pdf',
            original_filename='teste.pdf',
            file_size=1024,
            mime_type='application/pdf',
            sha256_hash='a' * 64,
            page_count=1,
            ocr_status='pending',
            uploaded_by=auditor_user,
        )
        assert doc.original_filename == 'teste.pdf'
        assert doc.ocr_status == 'pending'
        assert doc.file_size == 1024
        assert str(doc) == 'teste.pdf'
        assert doc.uploaded_by == auditor_user


class TestDocumentServices:
    def test_calculate_sha256(self, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('Conteúdo de teste para hash')
        hash_result = calculate_sha256(str(test_file))
        assert len(hash_result) == 64
        assert isinstance(hash_result, str)

    def test_calculate_sha256_empty_file(self, tmp_path):
        test_file = tmp_path / 'empty.txt'
        test_file.write_text('')
        hash_result = calculate_sha256(str(test_file))
        assert len(hash_result) == 64

    def test_has_meaningful_text_valid(self):
        text = 'Este é um texto com conteúdo significativo para testes de auditoria.'
        assert has_meaningful_text(text) is True

    def test_has_meaningful_text_empty(self):
        assert has_meaningful_text('') is False
        assert has_meaningful_text(None) is False

    def test_has_meaningful_text_short(self):
        assert has_meaningful_text('abc') is False

    def test_has_meaningful_text_no_alpha(self):
        assert has_meaningful_text('12345 67890 11111' * 20) is False
