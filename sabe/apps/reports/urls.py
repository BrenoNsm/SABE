from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('generate/<int:audit_id>/', views.ReportGenerateView.as_view(), name='generate'),
    path('<int:pk>/download/', views.ReportDownloadView.as_view(), name='download'),
    path('<int:pk>/delete/', views.ReportDeleteView.as_view(), name='delete'),
]
