#!/bin/bash
set -e

# TODO: Make these checks actually work...

# if [[ $(git diff --staged) ]]; then
#     echo "Repo checkout has staged changes - please comment them and try again."
#     exit 1
# fi

# if [[ ! $(git diff-files --quiet) ]]; then
#     echo "Repo checkout has uncommitted changes - please commit or .gitignore them and try again."
#     exit 1
# fi

# if [[ $(git ls-files --exclude-standard --others) ]]; then
#     echo "Repo checkout has untracked files - please commit or .gitignore them and try again."
#     exit 1
# fi

PACKAGE_REPO=ghcr.io/stackhpc/flux-image-model-inference
COMMIT_SHA=$(git rev-parse --short HEAD)
IMAGE_NAME=$PACKAGE_REPO:$COMMIT_SHA

echo
echo Building image $IMAGE_NAME
echo

docker build --platform linux/amd64 . -t $IMAGE_NAME
docker push $IMAGE_NAME
