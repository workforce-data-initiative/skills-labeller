#!/bin/sh

# -----------------------------------------------------------------------------
# clean_docker.sh
#	Docker cleanup utility.
#
# -----------------------------------------------------------------------------

# Cleanup stopped containers
docker rm $(docker ps -qa --no-trunc --filter "status=exited")

# Removed ununsed networks
docker network rm $(docker network ls | awk '$3 == "bridge" && $2 != "bridge" { print $1 }')

# Remove dangling volumes
docker volume ls -qf dangling=true | xargs -r docker volume rm

# Delete docker images
docker rmi $(docker images | grep "none" | awk '/ / { print $3 }')


