from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_admin', 'cpu_limit', 'memory_limit', 'gpu_access')
    fieldsets = UserAdmin.fieldsets + (
        ('Resource Limits', {
            'fields': ('cpu_limit', 'memory_limit', 'storage_limit', 'gpu_access'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)