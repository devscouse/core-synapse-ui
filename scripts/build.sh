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

echo "Building UI docker image..."
tag_name=core-synapse-ui-$SHORT_SHA
docker build -t $tag_name -f Dockerfile .
echo "$tag_name built..."

echo "Pushing $tag_name..."
docker tag $tag_name $DOCKER_REPO:$tag_name
docker push $DOCKER_REPO:$tag_name
echo "$tag_name pushed to $DOCKER_REPO"
