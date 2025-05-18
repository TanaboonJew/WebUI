from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('monitoring.urls')),
    path('accounts/', include('accounts.urls')),
    path('docker/', include('docker_manager.urls')),
    path('files/', include('file_manager.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)