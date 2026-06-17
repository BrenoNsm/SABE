from django.contrib import admin
from .models import Audit


@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ['numero', 'exercicio', 'unidade_jurisdicionada', 'responsavel', 'status', 'data_inicio', 'created_by']
    list_filter = ['status', 'exercicio', 'unidade_jurisdicionada']
    search_fields = ['numero', 'unidade_jurisdicionada', 'objeto', 'processo']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    date_hierarchy = 'data_inicio'
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
