from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
import psutil
import docker
from docker_manager.models import DockerContainer

@cache_page(60 * 5)
def public_dashboard(request):
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    try:
        docker_client = docker.from_env()
        containers = docker_client.containers.list(all=True)
        gpu_containers = len([c for c in containers if 'gpu' in str(c.attrs.get('HostConfig', {}).get('DeviceRequests', []))])
    except:
        containers = []
        gpu_containers = 0
    
    return render(request, 'monitoring/public_dashboard.html', {
        'cpu_usage': cpu_usage,
        'memory_usage': memory.percent,
        'memory_total': round(memory.total / (1024**3)),
        'disk_usage': disk.percent,
        'disk_total': round(disk.total / (1024**3)),
        'running_containers': len([c for c in containers if c.status == 'running']),
        'total_containers': len(containers),
        'gpu_containers': gpu_containers,
    })

@login_required
def user_dashboard(request):
    user_container = DockerContainer.objects.filter(user=request.user).first()
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    container_stats = None
    if user_container:
        try:
            docker_client = docker.from_env()
            container = docker_client.containers.get(user_container.container_id)
            stats = container.stats(stream=False)
            container_stats = {
                'cpu_usage': (stats['cpu_stats']['cpu_usage']['total_usage'] / 
                             stats['cpu_stats']['system_cpu_usage']) * 100,
                'memory_usage': stats['memory_stats']['usage'] / (1024**2),
                'memory_limit': int(user_container.memory_limit[:-1]) * 1024,
            }
        except:
            pass
    
    return render(request, 'monitoring/user_dashboard.html', {
        'user_container': user_container,
        'container_stats': container_stats,
        'system_usage': {
            'cpu': cpu_usage,
            'memory': memory.percent,
        },
        'user_limits': {
            'cpu': request.user.effective_cpu_limit,
            'memory': request.user.effective_memory_limit,
            'gpu': request.user.gpu_access,
        }
    })