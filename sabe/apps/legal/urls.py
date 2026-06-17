from django.urls import path
from . import views

app_name = 'legal'

urlpatterns = [
    path('', views.LegalFrameworkListView.as_view(), name='list'),
    path('create/', views.LegalFrameworkCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.LegalFrameworkUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.LegalFrameworkDeleteView.as_view(), name='delete'),
]
