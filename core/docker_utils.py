import docker
from docker.errors import DockerException
import os
import logging
import random
import string
from django.conf import settings
from .models import DockerContainer, AIModel
from users.models import CustomUser

logger = logging.getLogger(__name__)

try:
    client = docker.from_env()
    client.ping()
except DockerException as e:
    logger.error(f"Docker connection failed: {e}")
    client = None

def generate_jupyter_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def get_user_workspace(user):
    """Returns absolute path to user's workspace"""
    path = os.path.join(settings.MEDIA_ROOT, f'user_{user.id}_({user.username})')
    os.makedirs(path, exist_ok=True)
    return path

def create_container(user: CustomUser, image_name: str, container_type='default'):
    if not client:
        return None
        
    try:
        # Create user-specific directories
        user_dir = get_user_workspace(user)
        os.makedirs(os.path.join(user_dir, 'jupyter'), exist_ok=True)
        os.makedirs(os.path.join(user_dir, 'models'), exist_ok=True)
        os.makedirs(os.path.join(user_dir, 'data'), exist_ok=True)
        
        # Special handling for Jupyter containers
        if container_type == 'jupyter':
            port = 8888
            token = generate_jupyter_token()
            container = client.containers.run(
                image="jupyter/tensorflow-notebook:latest",
                name=f"jupyter_{user.id}_{user.username}",
                volumes={
                    os.path.join(user_dir, 'jupyter'): {'bind': '/home/jovyan/work', 'mode': 'rw'},
                    os.path.join(user_dir, 'models'): {'bind': '/home/jovyan/models', 'mode': 'ro'},
                    os.path.join(user_dir, 'data'): {'bind': '/home/jovyan/data', 'mode': 'ro'}
                },
                ports={f'{port}/tcp': (8080 + user.id)},
                environment={
                    'JUPYTER_TOKEN': token,
                    'GRANT_SUDO': 'yes'
                },
                detach=True,
                mem_limit=f"{user.ram_limit}m",
                cpu_shares=int(user.cpu_limit * 1024),
                runtime='nvidia' if user.gpu_access else None
            )
            return f"http://localhost:{8080 + user.id}/?token={token}"
        
        # Default container creation
        client.images.pull(image_name)
        container = client.containers.create(
            image=image_name,
            name=f"app_{user.id}_{user.username}",
            volumes={
                user_dir: {'bind': '/workspace', 'mode': 'rw'}
            },
            ports={'80/tcp': (8080 + user.id)},
            detach=True,
            mem_limit=f"{user.ram_limit}m",
            cpu_shares=int(user.cpu_limit * 1024),
            runtime='nvidia' if user.gpu_access else None
        )
        
        DockerContainer.objects.update_or_create(
            user=user,
            defaults={
                'container_id': container.id,
                'image_name': image_name,
                'status': 'created',
                'port_bindings': {'80_tcp': 8080 + user.id}
            }
        )
        return container.id
        
    except Exception as e:
        logger.error(f"Container creation failed: {e}")
        return None

def manage_container(user, action, container_type='default'):
    if not client:
        return False
        
    try:
        if container_type == 'jupyter':
            container_name = f"jupyter_{user.id}_{user.username}"
        else:
            container_name = f"app_{user.id}_{user.username}"
            
        container = client.containers.get(container_name)
        
        if action == 'start':
            container.start()
            status = 'running'
        elif action == 'stop':
            container.stop()
            status = 'stopped'
        elif action == 'delete':
            container.remove(force=True)
            return True
            
        if container_type != 'jupyter':
            DockerContainer.objects.filter(user=user).update(status=status)
        return True
        
    except Exception as e:
        logger.error(f"Container {action} failed: {e}")
        return False

def start_container(user): return manage_container(user, 'start')
def stop_container(user): return manage_container(user, 'stop')
def delete_container(user): return manage_container(user, 'delete')

def get_container_stats(container_id):
    if not client:
        return None
        
    try:
        container = client.containers.get(container_id)
        stats = container.stats(stream=False)
        
        # CPU calculation
        cpu_stats = stats['cpu_stats']
        cpu_delta = cpu_stats['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = cpu_stats['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
        cpu_percent = (cpu_delta / system_delta) * 100 if system_delta > 0 else 0

        # Memory calculation
        memory = stats['memory_stats']
        mem_usage = memory.get('usage', 0)
        mem_limit = memory.get('limit', 1)
        
        return {
            'cpu': round(cpu_percent, 2),
            'memory': mem_usage / (1024 * 1024),  # MB
            'memory_percent': (mem_usage / mem_limit) * 100,
            'network': {
                'rx': stats['networks']['eth0']['rx_bytes'] / (1024 * 1024),
                'tx': stats['networks']['eth0']['tx_bytes'] / (1024 * 1024)
            }
        }
    except Exception as e:
        logger.error(f"Stats collection failed: {e}")
        return None
    
def create_jupyter_container(user: CustomUser):
    if not client:
        return None
        
    try:
        user_dir = get_user_workspace(user)
        os.makedirs(os.path.join(user_dir, 'jupyter'), exist_ok=True)
        os.makedirs(os.path.join(user_dir, 'models'), exist_ok=True)
        os.makedirs(os.path.join(user_dir, 'data'), exist_ok=True)

        port = 8888
        token = generate_jupyter_token()

        container = client.containers.run(
            image="jupyter/tensorflow-notebook:latest",
            name=f"jupyter_{user.id}_{user.username}",
            volumes={
                os.path.join(user_dir, 'jupyter'): {'bind': '/home/jovyan/work', 'mode': 'rw'},
                os.path.join(user_dir, 'models'): {'bind': '/home/jovyan/models', 'mode': 'ro'},
                os.path.join(user_dir, 'data'): {'bind': '/home/jovyan/data', 'mode': 'ro'}
            },
            ports={f'{port}/tcp': (8080 + user.id)},
            environment={
                'JUPYTER_TOKEN': token,
                'GRANT_SUDO': 'yes'
            },
            detach=True,
            mem_limit=f"{user.ram_limit}m",
            cpu_shares=int(user.cpu_limit * 1024),
            runtime='nvidia' if user.gpu_access else None
        )

        return f"http://localhost:{8080 + user.id}/?token={token}"
    
    except Exception as e:
        logger.error(f"Failed to start Jupyter container: {e}")
        return None
