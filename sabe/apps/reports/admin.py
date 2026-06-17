from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'audit', 'format', 'generated_at', 'generated_by']
    list_filter = ['format', 'audit']
    search_fields = ['title']
    readonly_fields = ['generated_at', 'generated_by']
    list_per_page = 25
