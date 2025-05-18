from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'is_staff', 'ram_limit', 'storage_limit', 'cpu_limit', 'gpu_access']
    fieldsets = UserAdmin.fieldsets + (
        ('Resource Limits', {'fields': ('ram_limit', 'storage_limit', 'cpu_limit', 'gpu_access')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)