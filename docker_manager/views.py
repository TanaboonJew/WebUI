from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import DockerManager
from .models import DockerImage, DockerContainer

@login_required
def container_list(request):
    containers = DockerContainer.objects.filter(user=request.user)
    return render(request, 'docker_manager/container_list.html', {
        'containers': containers,
    })

@login_required
def container_create(request):
    docker_manager = DockerManager()
    
    if request.method == 'POST':
        image_id = request.POST.get('image')
        try:
            docker_manager.create_container(
                request.user,
                image_id,
                gpu_access=request.POST.get('gpu_access') == 'on'
            )
            messages.success(request, 'Container created successfully!')
            return redirect('docker_manager:container_list')
        except Exception as e:
            messages.error(request, str(e))
    
    images = DockerImage.objects.filter(public=True) | DockerImage.objects.filter(created_by=request.user)
    return render(request, 'docker_manager/container_create.html', {
        'images': images,
        'gpu_available': docker_manager.gpu_available,
        'user_limits': {
            'cpu': request.user.effective_cpu_limit,
            'memory': request.user.effective_memory_limit,
            'gpu': request.user.gpu_access,
        }
    })

@login_required
def container_control(request, container_id, action):
    docker_manager = DockerManager()
    try:
        if action == 'stop':
            docker_manager.stop_container(container_id)
            messages.success(request, 'Container stopped successfully!')
        elif action == 'start':
            # Implement start functionality
            messages.success(request, 'Container started successfully!')
        elif action == 'remove':
            # Implement remove functionality
            messages.success(request, 'Container removed successfully!')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('docker_manager:container_list')