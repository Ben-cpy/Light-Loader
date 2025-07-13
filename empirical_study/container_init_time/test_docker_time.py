import docker
import time

def measure_container_start_time(image_name):
    # Initialize Docker client
    client = docker.from_env()

    print(f"Pulling image {image_name}...")
    start_time = time.time()

    # Pull image (if not cached)
    try:
        client.images.pull(image_name)
    except Exception as e:
        print(f"Error pulling image: {e}")

    pull_time = time.time() - start_time
    print(f"Image pull time: {pull_time:.2f} seconds")

    print(f"Creating and starting container from image {image_name}...")
    start_time = time.time()

    # Create and start container
    container = client.containers.run(image_name, detach=True)
    container_time = time.time() - start_time
    print(f"Container start time: {container_time:.2f} seconds")

    # Clean up container
    container.remove(force=True)
    print("Container removed.")

    return pull_time, container_time

if __name__ == "__main__":
    # Replace with your built image name
    image_name = "test-container"

    print("Testing Docker container creation time...")
    pull_time, container_time = measure_container_start_time(image_name)
    print(f"Total time: {pull_time + container_time:.2f} seconds")
