from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('', views.public_dashboard, name='public_dashboard'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
]