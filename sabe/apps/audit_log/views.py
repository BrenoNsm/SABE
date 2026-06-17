import logging

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.utils import timezone

from .models import AuditLog

logger = logging.getLogger(__name__)


class AuditLogListView(LoginRequiredMixin, ListView):
    model = AuditLog
    template_name = 'audit_log/list.html'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        action = self.request.GET.get('action', '')
        user_id = self.request.GET.get('user', '')
        if action:
            qs = qs.filter(action=action)
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs
