from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    cpu_limit = models.FloatField(null=True, blank=True)
    memory_limit = models.CharField(max_length=20, null=True, blank=True)
    storage_limit = models.CharField(max_length=20, null=True, blank=True)
    gpu_access = models.BooleanField(default=False)
    
    @property
    def effective_cpu_limit(self):
        return self.cpu_limit or settings.DOCKER_CONFIG['DEFAULT_CPU_LIMIT']
    
    @property
    def effective_memory_limit(self):
        return self.memory_limit or settings.DOCKER_CONFIG['DEFAULT_MEMORY_LIMIT']
    
    @property
    def effective_storage_limit(self):
        return self.storage_limit or settings.DOCKER_CONFIG['DEFAULT_STORAGE_LIMIT']