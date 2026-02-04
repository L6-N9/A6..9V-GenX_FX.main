# Docker CLI Cheat Sheet

## Essential Docker Commands

### Container Lifecycle
```bash
docker run -d -p 8080:80 --name myapp nginx    # Run container
docker ps                                       # List running containers
docker ps -a                                    # List all containers
docker stop myapp                               # Stop container
docker start myapp                              # Start stopped container
docker restart myapp                            # Restart container
docker rm myapp                                 # Remove container
```

### Images
```bash
docker images                                   # List images
docker pull nginx:latest                        # Pull image
docker build -t myapp .                        # Build image
docker rmi myapp                                # Remove image
docker tag myapp myregistry/myapp:v1.0         # Tag image
```

### Logs and Debugging
```bash
docker logs myapp                               # View logs
docker logs -f myapp                            # Follow logs
docker exec -it myapp bash                     # Access container shell
docker inspect myapp                           # Inspect container
docker stats                                   # Resource usage
```

### Docker Compose
```bash
docker-compose up -d                            # Start services
docker-compose down                             # Stop services
docker-compose ps                               # List services
docker-compose logs -f                          # Follow all logs
docker-compose logs -f service_name             # Follow specific service
docker-compose build                            # Build services
docker-compose restart service_name             # Restart service
```

### Cleanup
```bash
docker container prune                          # Remove stopped containers
docker image prune                              # Remove unused images
docker volume prune                             # Remove unused volumes
docker system prune -a                         # Remove everything unused
```

## Your Trading App Quick Commands

```bash
# Start all trading services
docker-compose up -d

# Check service status
docker-compose ps

# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f discord_bot

# Restart specific service
docker-compose restart api

# Stop all services
docker-compose down

# Rebuild and restart everything
docker-compose down && docker-compose up -d --build

# Access API container
docker-compose exec api bash
```

## Useful Flags
- `-d` : Detached mode (background)
- `-p` : Port mapping (host:container)
- `-v` : Volume mount
- `-e` : Environment variable
- `-it` : Interactive terminal
- `--name` : Container name
- `--rm` : Auto-remove when stopped
- `-f` : Follow/force