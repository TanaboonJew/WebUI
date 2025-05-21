from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from .docker_utils import (  # Update this import line
    create_container,
    start_container,
    stop_container,
    delete_container,
    create_jupyter_container
)
from .file_utils import ensure_workspace_exists
from .models import DockerContainer, UserFile, AIModel
from .forms import DockerImageForm, FileUploadForm, AIModelForm
from .monitoring import get_system_stats, get_user_container_stats
from django.contrib import messages
import os

def home(request):
    """Home page view that shows different content based on authentication status"""
    return render(request, 'core/home.html')

@login_required
def docker_management(request):
    user_container = DockerContainer.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        form = DockerImageForm(request.POST)
        if form.is_valid():
            image_name = form.cleaned_data['image_name']
            if create_container(request.user, image_name):
                return redirect('docker-management')
    else:
        form = DockerImageForm()
    
    return render(request, 'core/docker_management.html', {
        'form': form,
        'container': user_container
    })

@login_required
def file_manager(request):
    ensure_workspace_exists(request.user)
    files = UserFile.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save(commit=False)
            new_file.user = request.user
            new_file.save()
            return redirect('file-manager')
    else:
        form = FileUploadForm()
    
    return render(request, 'core/file_manager.html', {
        'form': form,
        'files': files
    })

@login_required
def start_container_view(request):
    """View to start a user's container"""
    if request.method == 'POST':  # Add this check for security
        if start_container(request.user):
            messages.success(request, "Container started successfully")
        else:
            messages.error(request, "Failed to start container")
    return redirect('docker-management')

@login_required
def stop_container_view(request):
    """View to stop a user's container"""
    if request.method == 'POST':
        if stop_container(request.user):
            messages.success(request, "Container stopped successfully")
        else:
            messages.error(request, "Failed to stop container")
    return redirect('docker-management')

@login_required
def delete_container_view(request):
    """View to delete a user's container"""
    if request.method == 'POST':
        if delete_container(request.user):
            messages.success(request, "Container deleted successfully")
        else:
            messages.error(request, "Failed to delete container")
    return redirect('docker-management')

@login_required
def download_file(request, file_id):
    try:
        file_obj = UserFile.objects.get(id=file_id, user=request.user)
        response = FileResponse(file_obj.file)
        response['Content-Disposition'] = f'attachment; filename="{file_obj.filename()}"'
        return response
    except UserFile.DoesNotExist:
        messages.error(request, "File not found")
        return redirect('file-manager')

@login_required
def delete_file(request, file_id):
    try:
        file_obj = UserFile.objects.get(id=file_id, user=request.user)
        file_path = file_obj.file.path
        if os.path.exists(file_path):
            os.remove(file_path)
        file_obj.delete()
        messages.success(request, "File deleted successfully")
    except UserFile.DoesNotExist:
        messages.error(request, "File not found")
    return redirect('file-manager')

def public_dashboard(request):
    """Public system monitoring dashboard"""
    stats = get_system_stats()
    return render(request, 'core/public_dashboard.html', {
        'stats': stats
    })

@login_required
def private_dashboard(request):
    """Private user-specific monitoring dashboard"""
    system_stats = get_system_stats()
    container_stats = get_user_container_stats(request.user)
    
    return render(request, 'core/private_dashboard.html', {
        'system_stats': system_stats,
        'container_stats': container_stats,
        'user': request.user
    })
    
@login_required
def ai_dashboard(request):
    models = AIModel.objects.filter(user=request.user)
    jupyter_url = None
    jupyter_running = False
    
    if request.method == 'POST':
        if 'start_jupyter' in request.POST:
            jupyter_url = create_jupyter_container(request.user)
            messages.success(request, "Jupyter Notebook started successfully")
        elif 'stop_jupyter' in request.POST:
            if manage_container(request.user, 'stop', container_type='jupyter'):
                messages.success(request, "Jupyter Notebook stopped successfully")
            else:
                messages.error(request, "Failed to stop Jupyter Notebook")
        elif 'upload_model' in request.POST:
            form = AIModelForm(request.POST, request.FILES)
            if form.is_valid():
                model = form.save(commit=False)
                model.user = request.user
                model.save()
                messages.success(request, "Model uploaded successfully")
                return redirect('ai-dashboard')
    
    # Check if Jupyter is running
    try:
        if client:
            client.containers.get(f"jupyter_{request.user.id}_{request.user.username}")
            jupyter_running = True
    except:
        pass
    
    return render(request, 'core/ai_dashboard.html', {
        'models': models,
        'jupyter_url': jupyter_url,
        'jupyter_running': jupyter_running,
        'form': AIModelForm()
    })

@login_required
def delete_model(reques, model_id):
    try:
        model = AIModel.objects.get(id=model_id, user=request.user)
        model.delete()
        messages.success(request, "Model deleted successfully")
    except AIModel.DoesNotExist:
        messages.error(request, "Model not found")
    return redirect('ai-dashboard')