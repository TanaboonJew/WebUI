from django import forms
from .models import UserFile

class DockerImageForm(forms.Form):
    image_name = forms.CharField(
        label='Docker Image',
        help_text='e.g., nginx:latest or python:3.9-slim'
    )

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UserFile
        fields = ['file']