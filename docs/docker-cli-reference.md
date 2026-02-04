# Docker CLI Reference Guide

## Docker Installation Verification
```bash
docker --version
docker-compose --version
docker info
```

## Container Management

### Basic Container Operations
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Run a container
docker run [OPTIONS] IMAGE [COMMAND]

# Run container in detached mode
docker run -d nginx

# Run container with port mapping
docker run -p 8080:80 nginx

# Run container with environment variables
docker run -e ENV_VAR=value nginx

# Run container with volume mount
docker run -v /host/path:/container/path nginx

# Stop a container
docker stop CONTAINER_ID

# Start a stopped container
docker start CONTAINER_ID

# Restart a container
docker restart CONTAINER_ID

# Remove a container
docker rm CONTAINER_ID

# Remove all stopped containers
docker container prune
```

### Container Interaction
```bash
# Execute command in running container
docker exec -it CONTAINER_ID bash

# View container logs
docker logs CONTAINER_ID

# Follow logs in real-time
docker logs -f CONTAINER_ID

# Copy files between host and container
docker cp file.txt CONTAINER_ID:/path/to/destination
docker cp CONTAINER_ID:/path/to/file.txt ./local/path
```

## Image Management

### Basic Image Operations
```bash
# List images
docker images

# Pull an image from registry
docker pull IMAGE_NAME:TAG

# Build an image from Dockerfile
docker build -t IMAGE_NAME:TAG .

# Build with custom Dockerfile
docker build -f custom.dockerfile -t IMAGE_NAME .

# Remove an image
docker rmi IMAGE_ID

# Remove unused images
docker image prune

# Remove all unused images (including tagged)
docker image prune -a
```

### Image Information
```bash
# Inspect an image
docker inspect IMAGE_ID

# View image history
docker history IMAGE_ID

# Search for images on Docker Hub
docker search TERM
```

## Docker Compose Commands

### Basic Compose Operations
```bash
# Start services defined in docker-compose.yml
docker-compose up

# Start services in detached mode
docker-compose up -d

# Start specific service
docker-compose up SERVICE_NAME

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View running services
docker-compose ps

# View service logs
docker-compose logs SERVICE_NAME

# Follow logs
docker-compose logs -f SERVICE_NAME
```

### Compose Service Management
```bash
# Build services
docker-compose build

# Build specific service
docker-compose build SERVICE_NAME

# Restart services
docker-compose restart

# Scale a service
docker-compose up --scale SERVICE_NAME=3

# Execute command in service container
docker-compose exec SERVICE_NAME bash
```

## Your Trading Application Commands

Based on your `docker-compose.yml`, here are specific commands for your setup:

### Start All Services
```bash
# Start all trading services
docker-compose up -d

# View status of all services
docker-compose ps
```

### Individual Service Management
```bash
# Start only the API service
docker-compose up -d api

# Start Discord bot
docker-compose up -d discord_bot

# Start Telegram bot
docker-compose up -d telegram_bot

# Start notifier service
docker-compose up -d notifier

# Start scheduler service
docker-compose up -d scheduler

# Start WebSocket feed
docker-compose up -d websocket_feed
```

### Monitoring and Debugging
```bash
# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs api
docker-compose logs discord_bot
docker-compose logs telegram_bot

# Follow logs in real-time
docker-compose logs -f api

# Access service container shell
docker-compose exec api bash
docker-compose exec discord_bot bash
```

### Development Workflow
```bash
# Rebuild and restart services after code changes
docker-compose down && docker-compose up -d --build

# Rebuild specific service
docker-compose build api && docker-compose up -d api

# View service resource usage
docker stats
```

## Network Management

```bash
# List networks
docker network ls

# Create a network
docker network create NETWORK_NAME

# Connect container to network
docker network connect NETWORK_NAME CONTAINER_ID

# Inspect network
docker network inspect NETWORK_NAME

# Remove unused networks
docker network prune
```

## Volume Management

```bash
# List volumes
docker volume ls

# Create a volume
docker volume create VOLUME_NAME

# Inspect volume
docker volume inspect VOLUME_NAME

# Remove unused volumes
docker volume prune

# Remove specific volume
docker volume rm VOLUME_NAME
```

## System Management

```bash
# View system information
docker system df

# Clean up everything (containers, networks, images, build cache)
docker system prune -a

# View real-time resource usage
docker stats

# View system events
docker events
```

## Registry Operations

```bash
# Login to Docker registry
docker login

# Push image to registry
docker push IMAGE_NAME:TAG

# Tag an image
docker tag LOCAL_IMAGE:TAG REGISTRY/IMAGE:TAG
```

## Useful Flags and Options

### Common Run Options
- `-d, --detach`: Run container in background
- `-p, --publish`: Publish container port to host
- `-v, --volume`: Mount volume
- `-e, --env`: Set environment variables
- `--name`: Assign name to container
- `--rm`: Automatically remove container when it exits
- `-it`: Interactive terminal

### Common Build Options
- `-t, --tag`: Name and optionally tag the image
- `-f, --file`: Name of the Dockerfile
- `--no-cache`: Do not use cache when building

## Environment-Specific Commands

### Production Environment
```bash
# Use production compose file
docker-compose -f docker-compose.production.yml up -d

# View production logs
docker-compose -f docker-compose.production.yml logs -f
```

### Debug Environment
```bash
# Use debug compose file
docker-compose -f docker-compose.debug.yml up -d
```

## Troubleshooting Commands

```bash
# Check Docker daemon status
docker version

# View detailed system information
docker info

# Check container resource usage
docker stats CONTAINER_ID

# Inspect container configuration
docker inspect CONTAINER_ID

# View container processes
docker top CONTAINER_ID

# Check container health
docker exec CONTAINER_ID ps aux
```

## Quick Reference for Your Project

### Start Everything
```bash
docker-compose up -d
```

### Check Status
```bash
docker-compose ps
docker-compose logs --tail=50 -f
```

### Restart After Changes
```bash
docker-compose down && docker-compose up -d --build
```

### Clean Up
```bash
docker-compose down -v
docker system prune -a
```

### Access Service Logs
```bash
# API logs
docker-compose logs -f api

# Bot logs
docker-compose logs -f discord_bot
docker-compose logs -f telegram_bot
```