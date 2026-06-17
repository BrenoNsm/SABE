from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ValidationError


def validate_tipo(value):
    valid_tipos = {
        'CF': 'Constituição Federal',
        'CE': 'Constituição Estadual',
        'lei': 'Lei',
        'decreto': 'Decreto',
        'resolucao': 'Resolução',
        'in': 'Instrução Normativa',
        'acordao': 'Acórdão',
        'sumula': 'Súmula',
        'jurisprudencia': 'Jurisprudência',
    }
    if value not in valid_tipos:
        raise ValidationError(f'{value} não é um tipo válido.')
    return value


class LegalFramework(models.Model):
    TIPO_CHOICES = [
        ('CF', 'Constituição Federal'),
        ('CE', 'Constituição Estadual'),
        ('lei', 'Lei'),
        ('decreto', 'Decreto'),
        ('resolucao', 'Resolução'),
        ('in', 'Instrução Normativa'),
        ('acordao', 'Acórdão'),
        ('sumula', 'Súmula'),
        ('jurisprudencia', 'Jurisprudência'),
    ]

    tipo = models.CharField('Tipo', max_length=20, validators=[validate_tipo])
    numero = models.CharField('Número', max_length=100)
    ementa = models.TextField('Ementa', blank=True, default='')
    texto = models.TextField('Texto', blank=True, default='')
    search_vector = SearchVectorField(null=True, editable=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Fundamentação Legal'
        verbose_name_plural = 'Fundamentações Legais'
        ordering = ['tipo', 'numero']
        indexes = [
            models.Index(fields=['tipo']),
            GinIndex(fields=['search_vector']),
        ]
        unique_together = ['tipo', 'numero']

    def tipo_display(self):
        labels = dict(self.TIPO_CHOICES)
        return labels.get(self.tipo, self.tipo)

    def __str__(self):
        return f'{self.tipo_display()} - {self.numero}'


class FindingLegalFramework(models.Model):
    finding = models.ForeignKey(
        'findings.Finding', on_delete=models.CASCADE,
        related_name='legal_frameworks', verbose_name='Achado'
    )
    legal_framework = models.ForeignKey(
        LegalFramework, on_delete=models.CASCADE,
        related_name='findings', verbose_name='Fundamentação Legal'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Vinculação Achado-Fundamentação'
        verbose_name_plural = 'Vinculações Achado-Fundamentação'
        unique_together = ['finding', 'legal_framework']

    def __str__(self):
        return f'{self.finding} -> {self.legal_framework}'
