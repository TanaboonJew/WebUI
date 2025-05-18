import os
from django.db import models
from django.conf import settings
from users.models import CustomUser

def user_directory_path(instance, filename):
    # Files will be uploaded to MEDIA_ROOT/User_<id>_(<username>)/<filename>
    return f'User_{instance.user.id}_({instance.user.username})/{filename}'

class DockerContainer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    container_id = models.CharField(max_length=64, blank=True, null=True)
    image_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='stopped')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    port_bindings = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.user.username}'s {self.image_name}"

class UserFile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def filename(self):
        return os.path.basename(self.file.name)
    
    def __str__(self):
        return self.filename()