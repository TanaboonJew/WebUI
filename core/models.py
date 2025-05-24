import os
from django.db import models
from users.models import CustomUser


def user_directory_path(instance, filename):
    """Returns: user_<ID>_(<USERNAME>)/<type>/<filename>"""
    return f'user_{instance.user.id}_({instance.user.username})/{instance._meta.model_name}s/{filename}'


def user_file_path(instance, filename):
    """Used by models that have a static file_type attribute"""
    return f"user_{instance.user.id}_({instance.user.username})/{instance.file_type}/{filename}"


class DockerContainer(models.Model):
    CONTAINER_TYPES = [
        ('regular', 'Regular Container'),
        ('jupyter', 'Jupyter Notebook'),
        ('ai', 'AI Model Service')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    container_id = models.CharField(max_length=64, default='default_container_id')
    container_type = models.CharField(max_length=20, choices=CONTAINER_TYPES, default='regular')
    image_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='stopped')
    port_bindings = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ('user', 'container_type')

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


class AIModel(models.Model):
    FRAMEWORKS = [
        ('tensorflow', 'TensorFlow'),
        ('pytorch', 'PyTorch'),
        ('onnx', 'ONNX'),
        ('keras', 'Keras')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ai_models')
    name = models.CharField(max_length=100)
    framework = models.CharField(max_length=20, choices=FRAMEWORKS)
    model_file = models.FileField(upload_to=user_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    file_type = 'models'  # Used in upload path

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_framework_display()})"

    def delete(self, *args, **kwargs):
        self.model_file.delete(save=False)
        super().delete(*args, **kwargs)
