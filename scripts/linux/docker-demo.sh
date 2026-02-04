#!/bin/bash

# Docker CLI Demonstration Script for Trading Application
# This script demonstrates various Docker CLI commands

echo "=== Docker CLI Demonstration ==="
echo ""

# Check Docker installation
echo "1. Checking Docker Installation:"
echo "Command: docker --version"
sudo docker --version
echo ""

echo "Command: docker-compose --version"
docker-compose --version
echo ""

# Show system information
echo "2. Docker System Information:"
echo "Command: docker info"
sudo docker info | head -20
echo ""

# List current containers and images
echo "3. Current State:"
echo "Command: docker ps -a"
sudo docker ps -a
echo ""

echo "Command: docker images"
sudo docker images
echo ""

# Build the application image
echo "4. Building Application Image:"
echo "Command: docker build -t trading-app ."
echo "This will build your trading application using the Dockerfile"
echo "Press Enter to continue or Ctrl+C to skip..."
read

sudo docker build -t trading-app .
echo ""

# Show the newly created image
echo "5. Checking Built Image:"
echo "Command: docker images"
sudo docker images
echo ""

# Start services with docker-compose
echo "6. Starting Services with Docker Compose:"
echo "Command: docker-compose up -d"
echo "This will start all your trading services in the background"
echo "Press Enter to continue or Ctrl+C to skip..."
read

docker-compose up -d
echo ""

# Check running containers
echo "7. Checking Running Services:"
echo "Command: docker-compose ps"
docker-compose ps
echo ""

echo "Command: docker ps"
sudo docker ps
echo ""

# Show logs
echo "8. Viewing Service Logs:"
echo "Command: docker-compose logs --tail=10"
docker-compose logs --tail=10
echo ""

# Demonstrate individual service management
echo "9. Individual Service Management Examples:"
echo ""

echo "Restart API service:"
echo "Command: docker-compose restart api"
docker-compose restart api
echo ""

echo "View API logs:"
echo "Command: docker-compose logs --tail=5 api"
docker-compose logs --tail=5 api
echo ""

# Show resource usage
echo "10. Resource Usage:"
echo "Command: docker stats --no-stream"
sudo docker stats --no-stream
echo ""

# Network information
echo "11. Network Information:"
echo "Command: docker network ls"
sudo docker network ls
echo ""

# Volume information
echo "12. Volume Information:"
echo "Command: docker volume ls"
sudo docker volume ls
echo ""

# Cleanup demonstration
echo "13. Cleanup Commands (not executed):"
echo "To stop all services:"
echo "  docker-compose down"
echo ""
echo "To stop and remove volumes:"
echo "  docker-compose down -v"
echo ""
echo "To clean up unused Docker resources:"
echo "  docker system prune -a"
echo ""

echo "=== Docker CLI Demonstration Complete ==="
echo ""
echo "Key commands for your trading application:"
echo "- Start all services: docker-compose up -d"
echo "- Check status: docker-compose ps"
echo "- View logs: docker-compose logs -f [service_name]"
echo "- Stop services: docker-compose down"
echo "- Rebuild and restart: docker-compose down && docker-compose up -d --build"
echo ""
echo "For more details, see docker-cli-reference.md"