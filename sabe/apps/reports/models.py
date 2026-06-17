from django.db import models
from django.conf import settings


class Report(models.Model):
    FORMAT_CHOICES = [
        ('docx', 'DOCX'),
        ('pdf', 'PDF'),
    ]

    audit = models.ForeignKey(
        'audit.Audit', on_delete=models.CASCADE,
        related_name='reports', verbose_name='Auditoria'
    )
    title = models.CharField('Título', max_length=300)
    format = models.CharField(
        'Formato', max_length=4, choices=FORMAT_CHOICES
    )
    file = models.FileField('Arquivo', upload_to='reports/%Y/%m/', blank=True, null=True)
    generated_at = models.DateTimeField('Gerado em', auto_now_add=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='reports_generated', verbose_name='Gerado por'
    )

    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['audit', 'generated_at']),
        ]

    def __str__(self):
        return f'{self.title} ({self.get_format_display()})'
