from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('upload', 'Upload'),
        ('create', 'Criação'),
        ('update', 'Alteração'),
        ('delete', 'Exclusão'),
        ('report', 'Geração de Relatório'),
        ('ocr', 'Processamento OCR'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='audit_logs',
        verbose_name='Usuário'
    )
    action = models.CharField('Ação', max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField('Modelo', max_length=100, blank=True, default='')
    object_id = models.CharField('ID do Objeto', max_length=50, blank=True, default='')
    details = models.TextField('Detalhes', blank=True, default='')
    ip_address = models.GenericIPAddressField('Endereço IP', blank=True, null=True)
    created_at = models.DateTimeField('Data/Hora', auto_now_add=True)

    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['created_at']),
            models.Index(fields=['model_name']),
        ]

    def __str__(self):
        user_str = str(self.user) if self.user else 'Sistema'
        return f'{self.get_action_display()} - {user_str} - {self.created_at}'
