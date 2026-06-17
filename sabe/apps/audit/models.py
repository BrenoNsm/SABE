from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField


class Audit(models.Model):
    STATUS_CHOICES = [
        ('active', 'Ativa'),
        ('closed', 'Encerrada'),
    ]

    numero = models.CharField('Número', max_length=50, unique=True)
    exercicio = models.IntegerField(
        'Exercício',
        validators=[MinValueValidator(2000), MaxValueValidator(2099)]
    )
    processo = models.CharField('Processo', max_length=100, blank=True, default='')
    unidade_jurisdicionada = models.CharField('Unidade Jurisdicionada', max_length=300)
    responsavel = models.CharField('Responsável', max_length=200)
    objeto = models.TextField('Objeto')
    data_inicio = models.DateField('Data de Início')
    data_encerramento = models.DateField('Data de Encerramento', null=True, blank=True)
    observacoes = models.TextField('Observações', blank=True, default='')
    search_vector = SearchVectorField(null=True, editable=False)
    status = models.CharField(
        'Status', max_length=10, choices=STATUS_CHOICES, default='active'
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='audits_created', verbose_name='Criado por'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='audits_updated', verbose_name='Atualizado por',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Auditoria'
        verbose_name_plural = 'Auditorias'
        ordering = ['-exercicio', 'numero']
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['exercicio']),
            models.Index(fields=['status']),
            models.Index(fields=['unidade_jurisdicionada']),
            GinIndex(fields=['search_vector']),
        ]

    def __str__(self):
        return f'{self.numero}/{self.exercicio} - {self.unidade_jurisdicionada}'
