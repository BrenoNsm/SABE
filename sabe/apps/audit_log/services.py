import logging

from django.utils import timezone
from django.conf import settings

from .models import AuditLog

logger = logging.getLogger(__name__)


def log_action(user, action, model_name='', object_id='', details='', request=None):
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id else '',
        details=details,
        ip_address=ip_address,
    )


def clean_old_logs():
    retention_days = settings.AUDIT_LOG_RETENTION_DAYS
    cutoff_date = timezone.now() - timezone.timedelta(days=retention_days)
    deleted_count, _ = AuditLog.objects.filter(created_at__lt=cutoff_date).delete()
    if deleted_count:
        logger.info(f'{deleted_count} logs de auditoria removidos (retenção: {retention_days} dias)')
    return deleted_count
