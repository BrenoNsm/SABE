from django.urls import path
from . import views

app_name = 'logs'

urlpatterns = [
    path('', views.AuditLogListView.as_view(), name='list'),
]
