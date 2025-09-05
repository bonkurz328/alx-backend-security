from django.urls import path
from . import views

urlpatterns = [
    path('sensitive/', views.sensitive_view, name='sensitive-view'),
    path('auth-sensitive/', views.authenticated_sensitive_view, name='auth-sensitive-view'),
]
