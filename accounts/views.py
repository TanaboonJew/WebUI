import docker

client = docker.from_env()

def create_container(image_name, user_id):
    container = client.containers.run(
        image=image_name,
        name=f"user_{user_id}_container",
        detach=True,
        tty=True,
        volumes={f"/home/h100_1/workspace/user_files/{user_id}": {'bind': '/data', 'mode': 'rw'}}
    )
    return container.id