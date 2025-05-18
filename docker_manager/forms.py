
from django import forms
from .models import DockerImage

class DockerImageForm(forms.ModelForm):
    class Meta:
        model = DockerImage
        fields = ['name', 'tag', 'source', 'dockerfile', 'public']
        widgets = {
            'dockerfile': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
        }

class DockerContainerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        if self.user.gpu_access:
            self.fields['use_gpu'] = forms.BooleanField(
                required=False,
                label=f"Use H100 GPU (Shared with {settings.MAX_GPU_USERS} users max)",
                initial=True
            )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('use_gpu', False) and not self.user.gpu_access:
            raise forms.ValidationError("You don't have GPU access privileges")
        return cleaned_data