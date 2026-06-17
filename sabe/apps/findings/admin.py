from django.contrib import admin
from .models import Finding, Evidence


class EvidenceInline(admin.TabularInline):
    model = Evidence
    extra = 0
    readonly_fields = ['hash', 'created_at', 'created_by']
    fields = ['document', 'page_number', 'captured_text', 'hash']


@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ['title', 'audit', 'classificacao', 'created_by', 'created_at']
    list_filter = ['classificacao', 'audit']
    search_fields = ['title', 'description', 'criterio', 'causa']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    inlines = [EvidenceInline]
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ['document', 'finding', 'page_number', 'hash', 'created_at', 'created_by']
    list_filter = ['document__audit', 'page_number']
    search_fields = ['captured_text', 'hash']
    readonly_fields = ['hash', 'created_at', 'created_by', 'coordinates']
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
