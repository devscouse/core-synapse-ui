#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Default: don't load images into Minikube
LOAD_MINIKUBE=false

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --minikube) LOAD_MINIKUBE=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

SHORT_SHA=$(echo $GITHUB_SHA | cut -c1-7)

echo "Building API Docker image..."

if $LOAD_MINIKUBE; then
    echo "Activating Minikube Docker environment..."
    eval $(minikube docker-env)
fi

echo "Building UI docker image..."
ui_version=$(cat ui/VERSION)
tag_name=core-synapse-ui-$ui_version
docker build -t $tag_name -f ui/Dockerfile .
docker tag $tag_name $DOCKER_REPO:$tag_name
docker push $DOCKER_REPO:$tag_name
echo "$tag_name pushed to $DOCKER_REPO"
