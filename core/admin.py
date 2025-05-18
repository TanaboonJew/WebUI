from django.contrib import admin
from .models import DockerContainer, UserFile

@admin.register(DockerContainer)
class DockerContainerAdmin(admin.ModelAdmin):
    list_display = ('user', 'image_name', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(UserFile)
class UserFileAdmin(admin.ModelAdmin):
    list_display = ('user', 'filename', 'uploaded_at')
    list_filter = ('user',)