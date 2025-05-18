from django.db import models
from accounts.models import CustomUser

class FileSystem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    path = models.CharField(max_length=512)
    is_dir = models.BooleanField(default=False)
    size = models.BigIntegerField(default=0)
    last_modified = models.DateTimeField(auto_now=True)

class FileShare(models.Model):
    file = models.ForeignKey(FileSystem, on_delete=models.CASCADE)
    shared_by = models.ForeignKey(CustomUser, related_name='shared_files', on_delete=models.CASCADE)
    shared_with = models.ForeignKey(CustomUser, related_name='received_files', on_delete=models.CASCADE)
    permission = models.CharField(max_length=10, choices=[
        ('read', 'Read Only'),
        ('write', 'Read/Write'),
    ])
    shared_at = models.DateTimeField(auto_now_add=True)