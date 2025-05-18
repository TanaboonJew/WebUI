from django.db import models
from django.utils import timezone
from accounts.models import CustomUser

class DockerImage(models.Model):
    name = models.CharField(max_length=255)
    tag = models.CharField(max_length=100, default='latest')
    source = models.CharField(max_length=10, choices=[
        ('hub', 'Docker Hub'),
        ('file', 'Dockerfile'),
    ])
    dockerfile = models.TextField(null=True, blank=True)
    public = models.BooleanField(default=False)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, default=timezone.now)
    
    def __str__(self):
        return f"{self.name}:{self.tag}"

class DockerContainer(models.Model):
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('paused', 'Paused'),
        ('exited', 'Exited'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='containers')
    image = models.ForeignKey(DockerImage, on_delete=models.CASCADE)
    container_id = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    cpu_limit = models.FloatField()
    memory_limit = models.CharField(max_length=20)
    gpu_access = models.BooleanField(default=False)
    ports = models.JSONField(default=dict)
    volumes = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.name} ({self.status})"