from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.AuditListView.as_view(), name='list'),
    path('create/', views.AuditCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AuditDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.AuditUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.AuditDeleteView.as_view(), name='delete'),
    path('<int:pk>/duplicate/', views.AuditDuplicateView.as_view(), name='duplicate'),
    path('<int:pk>/close/', views.AuditCloseView.as_view(), name='close'),
]
