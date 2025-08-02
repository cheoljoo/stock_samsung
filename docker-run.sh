#!/bin/bash

# Docker build and run script for stock analysis
# This script builds the Docker image with current user's UID/GID and runs it

set -e

# Get current user information
USER_ID=$(id -u)
GROUP_ID=$(id -g)
USER_NAME=$(whoami)

# Docker image name
IMAGE_NAME="stock-analysis"
CONTAINER_NAME="stock-analysis-container"

# Function to print usage
usage() {
    echo "Usage: $0 [build|run|exec] [directory]"
    echo ""
    echo "Commands:"
    echo "  build                    - Build the Docker image"
    echo "  run [directory]          - Run container with specified directory mounted"
    echo "  exec                     - Execute bash in running container"
    echo "  stop                     - Stop and remove container"
    echo "  clean                    - Remove image and container"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 run many_company_effective_years_with_window_size"
    echo "  $0 run ."
    echo "  $0 exec"
    echo ""
    exit 1
}

# Function to build Docker image
build_image() {
    echo "🐳 Building Docker image with user ${USER_NAME} (UID: ${USER_ID}, GID: ${GROUP_ID})"
    
    docker build \
        --build-arg USER_ID=${USER_ID} \
        --build-arg GROUP_ID=${GROUP_ID} \
        --build-arg USER_NAME=${USER_NAME} \
        -t ${IMAGE_NAME} \
        .
    
    echo "✅ Docker image '${IMAGE_NAME}' built successfully!"
}

# Function to run container
run_container() {
    local mount_dir=${1:-.}
    local abs_mount_dir=$(realpath "$mount_dir")
    
    echo "🚀 Running container with directory: ${abs_mount_dir}"
    
    # Stop existing container if running
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
    
    # Run container with mounted directory
    docker run --rm -it \
        --name ${CONTAINER_NAME} \
        --user ${USER_ID}:${GROUP_ID} \
        -v "${abs_mount_dir}:/home/${USER_NAME}/workspace" \
        -e HOME="/home/${USER_NAME}" \
        --workdir "/home/${USER_NAME}/workspace" \
        ${IMAGE_NAME}
}

# Function to execute bash in running container
exec_container() {
    echo "🔧 Executing bash in running container..."
    docker exec -it \
        --user ${USER_ID}:${GROUP_ID} \
        -e HOME="/home/${USER_NAME}" \
        ${CONTAINER_NAME} \
        /bin/bash
}

# Function to stop container
stop_container() {
    echo "🛑 Stopping container..."
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
    echo "✅ Container stopped and removed"
}

# Function to clean up
clean_up() {
    echo "🧹 Cleaning up Docker image and container..."
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
    docker rmi ${IMAGE_NAME} 2>/dev/null || true
    echo "✅ Cleanup completed"
}

# Main script logic
case "${1:-}" in
    "build")
        build_image
        ;;
    "run")
        if ! docker image inspect ${IMAGE_NAME} >/dev/null 2>&1; then
            echo "❌ Docker image '${IMAGE_NAME}' not found. Building it first..."
            build_image
        fi
        run_container "$2"
        ;;
    "exec")
        exec_container
        ;;
    "stop")
        stop_container
        ;;
    "clean")
        clean_up
        ;;
    *)
        usage
        ;;
esac
