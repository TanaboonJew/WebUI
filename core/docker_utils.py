import docker
from docker.errors import DockerException
import os
import logging
from django.conf import settings
from .models import DockerContainer
from users.models import CustomUser
import secrets
import string

logger = logging.getLogger(__name__)

try:
    client = docker.from_env()
    client.ping()
except DockerException as e:
    logger.error(f"Docker connection failed: {e}")
    client = None

def generate_jupyter_token():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))

def get_user_workspace(user):
    """Returns path: user_data/user_<ID>_(<USERNAME>)"""
    user_dir = f"user_{user.id}_({user.username})"
    base_path = os.path.join(settings.MEDIA_ROOT, user_dir)
    
    # Create required subdirectories
    os.makedirs(os.path.join(base_path, 'jupyter'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'models'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'data'), exist_ok=True)
    
    return base_path

def create_container(user: CustomUser, image_name: str):
    if not client:
        return False
        
    try:
        workspace = get_user_workspace(user)
        container = client.containers.create(
            image=image_name,
            name=f"user_{user.id}_container",
            volumes={
                workspace: {'bind': '/workspace', 'mode': 'rw'},
                f"{workspace}/jupyter": {'bind': '/notebooks', 'mode': 'rw'},
                f"{workspace}/models": {'bind': '/models', 'mode': 'rw'},
                f"{workspace}/data": {'bind': '/data', 'mode': 'rw'}
            },
            ports={'8888/tcp': 8080 + user.id},
            environment={
                'JUPYTER_TOKEN': generate_jupyter_token(),
                'GRANT_SUDO': 'yes'
            },
            detach=True,
            runtime='nvidia' if user.gpu_access else None
        )
        
        DockerContainer.objects.update_or_create(
            user=user,
            defaults={
                'container_id': container.id,
                'image_name': image_name,
                'status': 'created',
                'port_bindings': {'8888_tcp': 8080 + user.id}
            }
        )
        return True
    except Exception as e:
        logger.error(f"Container creation failed: {e}")
        return False

def create_jupyter_container(user):
    if not client:
        return None
        
    try:
        workspace = get_user_workspace(user)
        token = generate_jupyter_token()
        
        container = client.containers.run(
            "jupyter/datascience-notebook",
            name=f"jupyter_{user.id}",
            volumes={
                f"{workspace}/jupyter": {'bind': '/home/jovyan/work', 'mode': 'rw'},
                f"{workspace}/models": {'bind': '/models', 'mode': 'rw'},
                f"{workspace}/data": {'bind': '/data', 'mode': 'rw'}
            },
            ports={'8888/tcp': 9000 + user.id},
            environment={
                'JUPYTER_TOKEN': token,
                'GRANT_SUDO': 'yes'
            },
            detach=True,
            remove=True,
            runtime='nvidia' if user.gpu_access else None
        )
        
        return f"http://localhost:{9000 + user.id}/?token={token}"
    except Exception as e:
        logger.error(f"Jupyter creation failed: {e}")
        return None