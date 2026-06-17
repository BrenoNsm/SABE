from django.urls import path
from . import views

app_name = 'findings'

urlpatterns = [
    path('create/<int:audit_id>/', views.FindingCreateView.as_view(), name='create'),
    path('<int:pk>/', views.FindingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.FindingUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.FindingDeleteView.as_view(), name='delete'),
    path('evidence/create/', views.EvidenceCreateView.as_view(), name='evidence_create'),
    path('evidence/<int:pk>/delete/', views.EvidenceDeleteView.as_view(), name='evidence_delete'),
]
