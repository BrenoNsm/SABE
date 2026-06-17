from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'audit', 'file_size', 'page_count', 'ocr_status', 'uploaded_at', 'uploaded_by']
    list_filter = ['ocr_status', 'uploaded_at', 'audit']
    search_fields = ['original_filename', 'sha256_hash', 'extracted_text']
    readonly_fields = ['sha256_hash', 'file_size', 'page_count', 'extracted_text', 'search_vector', 'uploaded_at', 'uploaded_by']
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
