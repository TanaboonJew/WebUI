from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Base fields (username, password, email, etc. are inherited)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    # Resource allocation fields
    ram_limit = models.PositiveIntegerField(default=15360)  # 15GB in MB
    storage_limit = models.PositiveIntegerField(default=51200)  # 50GB in MB
    cpu_limit = models.PositiveIntegerField(default=4)  # 4 cores
    gpu_access = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username