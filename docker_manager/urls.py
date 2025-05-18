from django.urls import path
from . import views

app_name = 'docker_manager'

urlpatterns = [
    path('', views.container_list, name='container_list'),
    path('create/', views.container_create, name='container_create'),
    path('<str:container_id>/<str:action>/', views.container_control, name='container_control'),
]