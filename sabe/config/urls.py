from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('sabe.apps.accounts.urls')),
    path('audit/', include('sabe.apps.audit.urls')),
    path('documents/', include('sabe.apps.documents.urls')),
    path('findings/', include('sabe.apps.findings.urls')),
    path('legal/', include('sabe.apps.legal.urls')),
    path('reports/', include('sabe.apps.reports.urls')),
    path('search/', include('sabe.apps.search.urls')),
    path('logs/', include('sabe.apps.audit_log.urls')),
    path('', RedirectView.as_view(pattern_name='audit:list', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
