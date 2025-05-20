import docker
from docker.errors import DockerException
import os
import logging
from django.conf import settings
from .models import DockerContainer
from users.models import CustomUser

# Initialize logger
logger = logging.getLogger(__name__)

# Docker client with error handling
try:
    client = docker.from_env()
    client.ping()  # Test connection
except DockerException as e:
    logger.error(f"Docker connection failed: {e}")
    client = None

def get_user_dir(user):
    """Returns path in format: user_<ID>_(<USERNAME>)"""
    return f'user_{user.id}_({user.username})'

def get_user_workspace(user):
    """Get absolute path to user's workspace directory"""
    user_dir = os.path.join(settings.USER_DATA_ROOT, get_user_dir(user))
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def create_container(user: CustomUser, image_name: str):
    if not client:
        logger.error("Docker service unavailable")
        return False
        
    try:
        # Pull image with progress tracking
        logger.info(f"Pulling image {image_name}")
        client.images.pull(image_name)
        
        # Create container configuration
        container_config = {
            'image': image_name,
            'name': f"webui_{get_user_dir(user)}",
            'mem_limit': f"{user.ram_limit}m",
            'cpu_shares': int(user.cpu_limit * 1024),
            'volumes': {
                get_user_workspace(user): {
                    'bind': '/workspace',
                    'mode': 'rw'
                }
            },
            'ports': {'80/tcp': ('0.0.0.0', 8080 + user.id)},
            'detach': True,
            'restart_policy': {'Name': 'unless-stopped'}
        }
        
        # Add GPU support if enabled
        if user.gpu_access:
            container_config['runtime'] = 'nvidia'
            container_config['device_requests'] = [
                docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])
            ]

        # Create container
        container = client.containers.create(**container_config)
        
        # Save to database
        DockerContainer.objects.update_or_create(
            user=user,
            defaults={
                'container_id': container.id,
                'image_name': image_name,
                'status': 'created',
                'port_bindings': {'80_tcp': 8080 + user.id}
            }
        )
        logger.info(f"Created container {container.id} for user {get_user_dir(user)}")
        return True
        
    except Exception as e:
        logger.error(f"Container creation failed: {e}")
        return False

def manage_container(user, action):
    """Generic container management function"""
    if not client:
        return False
        
    try:
        container = DockerContainer.objects.get(user=user)
        docker_container = client.containers.get(container.container_id)
        
        if action == 'start':
            docker_container.start()
            container.status = 'running'
        elif action == 'stop':
            docker_container.stop()
            container.status = 'stopped'
        elif action == 'delete':
            docker_container.remove(force=True)
            container.delete()
            return True
            
        container.save()
        return True
    except Exception as e:
        logger.error(f"Container {action} failed: {e}")
        return False

def start_container(user): return manage_container(user, 'start')
def stop_container(user): return manage_container(user, 'stop')
def delete_container(user): return manage_container(user, 'delete')

def get_user_container_stats(user):
    """Get detailed container statistics"""
    if not client:
        return None
        
    try:
        container = DockerContainer.objects.get(user=user)
        docker_container = client.containers.get(container.container_id)
        stats = docker_container.stats(stream=False)
        
        # CPU calculation
        cpu_stats = stats['cpu_stats']
        cpu_percent = 0.0
        if 'system_cpu_usage' in cpu_stats:
            cpu_delta = cpu_stats['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = cpu_stats['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100 if system_delta > 0 else 0

        # Memory calculation
        memory = stats['memory_stats']
        mem_usage = memory.get('usage', 0)
        mem_limit = memory.get('limit', 1)  # Avoid division by zero
        
        return {
            'cpu_percent': round(cpu_percent, 2),
            'memory_usage': mem_usage,
            'memory_limit': mem_limit,
            'memory_percent': (mem_usage / mem_limit) * 100,
            'network': stats.get('networks', {}),
            'status': container.status,
            'ports': container.port_bindings
        }
    except Exception as e:
        logger.error(f"Stats collection failed: {e}")
        return None

def create_jupyter_container(user):
    if not client:
        logger.error("Docker service unavailable - client is None")
        return None

    try:
        user_dir = os.path.join(settings.USER_DATA_ROOT, f'user_{user.id}_({user.username})')
        jupyter_dir = os.path.join(user_dir, 'jupyter')
        
        logger.info(f"Creating directories: {user_dir} and {jupyter_dir}")
        os.makedirs(jupyter_dir, exist_ok=True)
        
        logger.info(f"Attempting to create container for {user.username}")
        container = client.containers.run(
            image="jupyter/tensorflow-notebook",
            name=f"jupyter_{user.id}_{user.username}",
            volumes={
                jupyter_dir: {'bind': '/home/jovyan/work', 'mode': 'rw'}
            },
            ports={'8888/tcp': (8080 + user.id)},
            environment={
                'JUPYTER_TOKEN': str(user.id)[:8]
            },
            detach=True
        )
        logger.info(f"Container created: {container.id}")
        return f"http://localhost:{8080 + user.id}/?token={str(user.id)[:8]}"
    except Exception as e:
        logger.error(f"Jupyter creation failed: {str(e)}")
        return None