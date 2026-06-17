from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('upload/<int:audit_id>/', views.DocumentUploadView.as_view(), name='upload'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='delete'),
    path('<int:pk>/process/', views.DocumentProcessView.as_view(), name='process'),
    path('<int:pk>/viewer/', views.PDFViewerView.as_view(), name='viewer'),
]
