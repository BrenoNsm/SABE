from django.contrib import admin
from .models import LegalFramework, FindingLegalFramework


class FindingLegalFrameworkInline(admin.TabularInline):
    model = FindingLegalFramework
    extra = 0
    autocomplete_fields = ['finding']


@admin.register(LegalFramework)
class LegalFrameworkAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'numero', 'ementa']
    list_filter = ['tipo']
    search_fields = ['numero', 'ementa', 'texto']
    inlines = [FindingLegalFrameworkInline]
    list_per_page = 25


@admin.register(FindingLegalFramework)
class FindingLegalFrameworkAdmin(admin.ModelAdmin):
    list_display = ['finding', 'legal_framework', 'created_at']
    list_filter = ['legal_framework__tipo']
    autocomplete_fields = ['finding', 'legal_framework']
