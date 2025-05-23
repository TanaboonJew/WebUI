# Generated by Django 5.2.1 on 2025-05-20 17:33

import core.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_aimodel'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aimodel',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='dockercontainer',
            options={'ordering': ['-updated_at']},
        ),
        migrations.RenameField(
            model_name='dockercontainer',
            old_name='last_updated',
            new_name='updated_at',
        ),
        migrations.AlterField(
            model_name='aimodel',
            name='model_file',
            field=models.FileField(upload_to=core.models.user_directory_path),
        ),
        migrations.AlterField(
            model_name='aimodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_models', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='dockercontainer',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='container', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='aimodel',
            unique_together={('user', 'name')},
        ),
    ]
