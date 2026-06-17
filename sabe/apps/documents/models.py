from django.db import models
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField


class Document(models.Model):
    OCR_STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
        ('not_needed', 'Não Necessário'),
    ]

    audit = models.ForeignKey(
        'audit.Audit', on_delete=models.CASCADE,
        related_name='documents', verbose_name='Auditoria'
    )
    filename = models.CharField('Nome do Arquivo', max_length=255)
    original_filename = models.CharField('Nome Original', max_length=255)
    file = models.FileField('Arquivo', upload_to='documents/%Y/%m/')
    file_size = models.BigIntegerField('Tamanho', default=0)
    mime_type = models.CharField('Tipo MIME', max_length=100, default='application/pdf')
    sha256_hash = models.CharField('Hash SHA-256', max_length=64, editable=False)
    page_count = models.IntegerField('Quantidade de Páginas', default=0)
    ocr_status = models.CharField(
        'Status OCR', max_length=15, choices=OCR_STATUS_CHOICES, default='pending'
    )
    extracted_text = models.TextField('Texto Extraído', blank=True, default='')
    search_vector = SearchVectorField(null=True, editable=False)
    uploaded_at = models.DateTimeField('Enviado em', auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='documents_uploaded', verbose_name='Enviado por'
    )

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['sha256_hash']),
            models.Index(fields=['ocr_status']),
            models.Index(fields=['audit', 'uploaded_at']),
            GinIndex(fields=['search_vector']),
        ]

    def __str__(self):
        return self.original_filename

    def delete(self, *args, **kwargs):
        if self.file:
            storage = self.file.storage
            if storage.exists(self.file.name):
                storage.delete(self.file.name)
        super().delete(*args, **kwargs)
