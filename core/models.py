import os
from django.db import models
from django.conf import settings
from users.models import CustomUser

def user_directory_path(instance, filename):
    """Returns: user_<ID>_(<USERNAME>)/<type>/<filename>"""
    return f'user_{instance.user.id}_({instance.user.username})/{instance._meta.model_name}s/{filename}'

class DockerContainer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='container')
    container_id = models.CharField(max_length=64, blank=True, null=True)
    image_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='stopped')
    port_bindings = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username}'s {self.image_name} ({self.status})"


class UserFile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def filename(self):
        return os.path.basename(self.file.name)
    
    def __str__(self):
        return self.filename()
    
def user_model_path(instance, filename):
    """Returns: user_<ID>_(<USERNAME>)/models/<filename>"""
    return f'user_{instance.user.id}_({instance.user.username})/models/{filename}'

class AIModel(models.Model):
    FRAMEWORK_CHOICES = [
        ('tensorflow', 'TensorFlow'),
        ('pytorch', 'PyTorch'), 
        ('onnx', 'ONNX'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ai_models')
    name = models.CharField(max_length=100)
    model_file = models.FileField(upload_to=user_directory_path)
    framework = models.CharField(max_length=50, choices=FRAMEWORK_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_framework_display()})"

    def delete(self, *args, **kwargs):
        """Delete associated files when model is deleted"""
        self.model_file.delete()
        super().delete(*args, **kwargs)
    

