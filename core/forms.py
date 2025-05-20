from django import forms
from .models import UserFile, AIModel

class DockerImageForm(forms.Form):
    image_name = forms.CharField(
        label='Docker Image',
        help_text='e.g., nginx:latest or python:3.9-slim'
    )

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UserFile
        fields = ['file']
        
class AIModelForm(forms.ModelForm):
    class Meta:
        model = AIModel
        fields = ['name', 'model_file', 'framework']
        widgets = {
            'framework': forms.Select(attrs={'class': 'form-control'}),
        }