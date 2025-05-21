from django.db import models
from django.conf import settings
from users.models import CustomUser
import os

def user_file_path(instance, filename):
    return f"user_{instance.user.id}_({instance.user.username})/{instance.file_type}/{filename}"

class DockerContainer(models.Model):
    CONTAINER_TYPES = [
        ('regular', 'Regular Container'),
        ('jupyter', 'Jupyter Notebook'),
        ('ai', 'AI Model Service')
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    container_id = models.CharField(max_length=64)
    container_type = models.CharField(max_length=20, choices=CONTAINER_TYPES)
    image_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='stopped')
    port_bindings = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'container_type')

class AIModel(models.Model):
    FRAMEWORKS = [
        ('tensorflow', 'TensorFlow'),
        ('pytorch', 'PyTorch'),
        ('onnx', 'ONNX'),
        ('keras', 'Keras')
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    framework = models.CharField(max_length=20, choices=FRAMEWORKS)
    model_file = models.FileField(upload_to=user_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    file_type = 'models'
    
    def __str__(self):
        return f"{self.name} ({self.get_framework_display()})"