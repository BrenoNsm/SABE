from django.db import models
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField


class Finding(models.Model):
    CLASSIFICATION_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

    audit = models.ForeignKey(
        'audit.Audit', on_delete=models.CASCADE,
        related_name='findings', verbose_name='Auditoria'
    )
    title = models.CharField('Título', max_length=300)
    description = models.TextField('Descrição')
    criterio = models.TextField('Critério', blank=True, default='')
    condicao = models.TextField('Condição', blank=True, default='')
    causa = models.TextField('Causa', blank=True, default='')
    efeito = models.TextField('Efeito', blank=True, default='')
    recomendacao = models.TextField('Recomendação', blank=True, default='')
    classificacao = models.CharField(
        'Classificação', max_length=10, choices=CLASSIFICATION_CHOICES, default='medium'
    )
    search_vector = SearchVectorField(null=True, editable=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='findings_created', verbose_name='Criado por'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='findings_updated', verbose_name='Atualizado por',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Achado'
        verbose_name_plural = 'Achados'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['audit', 'classificacao']),
            GinIndex(fields=['search_vector']),
        ]

    def __str__(self):
        return self.title


class Evidence(models.Model):
    document = models.ForeignKey(
        'documents.Document', on_delete=models.CASCADE,
        related_name='evidences', verbose_name='Documento'
    )
    finding = models.ForeignKey(
        Finding, on_delete=models.CASCADE,
        related_name='evidences', verbose_name='Achado'
    )
    page_number = models.IntegerField('Página')
    captured_text = models.TextField('Texto Capturado')
    coordinates = models.JSONField('Coordenadas', default=dict)
    hash = models.CharField('Hash', max_length=64, editable=False)
    created_at = models.DateTimeField('Criada em', auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='evidences_created', verbose_name='Criada por'
    )

    class Meta:
        verbose_name = 'Evidência'
        verbose_name_plural = 'Evidências'
        ordering = ['document', 'page_number']
        indexes = [
            models.Index(fields=['document', 'finding']),
            models.Index(fields=['hash']),
            models.Index(fields=['page_number']),
        ]

    def __str__(self):
        return f'Evidência p.{self.page_number} - {self.document.original_filename}'
