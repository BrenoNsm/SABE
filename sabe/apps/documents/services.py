import hashlib
import logging
import os

from django.conf import settings
from django.db import transaction
from django.contrib.postgres.search import SearchVector

import fitz

from .models import Document

logger = logging.getLogger(__name__)


class DocumentProcessingError(Exception):
    pass


def calculate_sha256(file_path):
    h = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def extract_text_pymupdf(file_path):
    text_parts = []
    try:
        doc = fitz.open(file_path)
        page_count = doc.page_count
        for page_num in range(page_count):
            page = doc.load_page(page_num)
            text = page.get_text()
            text_parts.append(text)
        doc.close()
        return '\n'.join(text_parts), page_count
    except Exception as e:
        raise DocumentProcessingError(f'Erro ao extrair texto com PyMuPDF: {e}')


def extract_text_pdfplumber(file_path):
    import pdfplumber
    text_parts = []
    page_count = 0
    try:
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text() or ''
                text_parts.append(text)
        return '\n'.join(text_parts), page_count
    except Exception as e:
        raise DocumentProcessingError(f'Erro ao extrair texto com pdfplumber: {e}')


def has_meaningful_text(text, min_chars=100):
    if not text:
        return False
    stripped = text.strip()
    if len(stripped) < min_chars:
        return False
    alpha_chars = sum(c.isalpha() for c in stripped)
    if alpha_chars < 20:
        return False
    return True


def run_ocr(file_path, language=None):
    import ocrmypdf
    if language is None:
        language = settings.OCR_LANGUAGE
    output_path = file_path.replace('.pdf', '_ocr.pdf')
    try:
        ocrmypdf.ocr(
            file_path,
            output_path,
            language=language,
            force_ocr=True,
            deskew=True,
            clean=True,
            optimize=1,
        )
        return output_path
    except Exception as e:
        logger.error(f'OCR falhou para {file_path}: {e}')
        raise DocumentProcessingError(f'Erro no OCR: {e}')


def update_search_vector(instance):
    if instance.extracted_text:
        instance.search_vector = SearchVector('extracted_text', config='portuguese')
    else:
        instance.search_vector = None


@transaction.atomic
def process_document(document_id):
    try:
        document = Document.objects.select_for_update().get(id=document_id)
    except Document.DoesNotExist:
        raise DocumentProcessingError(f'Documento {document_id} não encontrado')

    document.ocr_status = 'processing'
    document.save(update_fields=['ocr_status'])

    file_path = document.file.path

    if not os.path.exists(file_path):
        document.ocr_status = 'failed'
        document.save(update_fields=['ocr_status'])
        raise DocumentProcessingError(f'Arquivo não encontrado: {file_path}')

    try:
        extracted_text, page_count = extract_text_pymupdf(file_path)
        document.page_count = page_count

        if has_meaningful_text(extracted_text):
            document.extracted_text = extracted_text
            document.ocr_status = 'not_needed'
        else:
            try:
                ocr_path = run_ocr(file_path)
                ocr_text, ocr_pages = extract_text_pymupdf(ocr_path)
                if has_meaningful_text(ocr_text):
                    document.extracted_text = ocr_text
                    document.ocr_status = 'completed'
                    import shutil
                    shutil.move(ocr_path, file_path)
                else:
                    document.extracted_text = extracted_text or ''
                    document.ocr_status = 'completed'
                    if os.path.exists(ocr_path) and ocr_path != file_path:
                        os.remove(ocr_path)
            except DocumentProcessingError:
                document.extracted_text = extracted_text or ''
                document.ocr_status = 'failed'

        update_search_vector(document)
        document.save(update_fields=[
            'extracted_text', 'ocr_status', 'page_count', 'search_vector'
        ])

        logger.info(f'Documento {document_id} processado: OCR={document.ocr_status}, páginas={page_count}')
        return document

    except Exception as e:
        document.ocr_status = 'failed'
        document.save(update_fields=['ocr_status'])
        logger.error(f'Erro no processamento do documento {document_id}: {e}')
        raise DocumentProcessingError(str(e))
