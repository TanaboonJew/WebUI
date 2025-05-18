import docker
from django.conf import settings
from docker.errors import DockerException

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.gpu_available = GPU_AVAILABLE and self._check_gpu_availability()
        
    def _check_gpu_availability(self):
        if not GPU_AVAILABLE:
            return False
        try:
            gpus = GPUtil.getGPUs()
            return len(gpus) > 0
        except:
            return False
    
    def create_container(self, user, image_id, **kwargs):
        if user.containers.count() >= settings.DOCKER_CONFIG['MAX_CONTAINERS_PER_USER']:
            raise Exception("You have reached your container limit")
            
        cpu_limit = user.effective_cpu_limit
        memory_limit = user.effective_memory_limit
        
        container_config = {
            'image': image_id,
            'detach': True,
            'name': f"webui_{user.username}_{image_id.replace(':', '_')}",
            'cpu_period': 100000,
            'cpu_quota': int(cpu_limit * 100000),
            'mem_limit': memory_limit,
            'ports': kwargs.get('ports', {}),
            'volumes': kwargs.get('volumes', {}),
        }
        
        if kwargs.get('gpu_access', False) and self.gpu_available:
            container_config['device_requests'] = [
                docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])
            ]
        
        try:
            container = self.client.containers.run(**container_config)
            return DockerContainer.objects.create(
                user=user,
                image_id=image_id,
                container_id=container.id,
                name=container.name,
                status='running',
                cpu_limit=cpu_limit,
                memory_limit=memory_limit,
                gpu_access=kwargs.get('gpu_access', False),
                ports=kwargs.get('ports', {}),
                volumes=kwargs.get('volumes', {}),
            )
        except DockerException as e:
            raise Exception(f"Failed to create container: {str(e)}")
    
    def stop_container(self, container_id):
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            DockerContainer.objects.filter(container_id=container_id).update(status='stopped')
            return True
        except DockerException as e:
            raise Exception(f"Failed to stop container: {str(e)}")