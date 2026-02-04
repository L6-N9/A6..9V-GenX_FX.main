#!/bin/bash

# AMP System Docker Deployment Script
# This script deploys the AMP trading system using Docker Compose

set -e  # Exit on any error

echo "🐳 AMP System Docker Deployment"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
}

# Check if Docker Compose is installed
check_docker_compose() {
    print_status "Checking Docker Compose installation..."
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed"
}

# Pull the latest Docker image
pull_image() {
    print_status "Pulling latest AMP Docker image..."
    docker pull keamouyleng/genx-fx:latest
    print_success "Docker image pulled successfully"
}

# Check if .env file exists
check_env_file() {
    print_status "Checking environment configuration..."
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success ".env file created from template"
            print_warning "Please update .env file with your actual API keys before continuing"
        else
            print_error ".env.example not found. Please create .env file manually."
            exit 1
        fi
    else
        print_success ".env file found"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs data reports
    print_success "Directories created"
}

# Deploy with Docker Compose
deploy() {
    print_status "Deploying AMP system with Docker Compose..."
    docker-compose -f docker-compose.amp.yml up -d
    print_success "AMP system deployed successfully"
}

# Check deployment status
check_status() {
    print_status "Checking deployment status..."
    sleep 5  # Wait for containers to start
    docker-compose -f docker-compose.amp.yml ps
}

# Show access information
show_access_info() {
    echo ""
    echo "🎉 AMP System Deployment Complete!"
    echo "================================"
    echo ""
    echo "📊 Access Points:"
    echo "   - API Health: http://localhost:8000/health"
    echo "   - Grafana Dashboard: http://localhost:3000"
    echo "   - Grafana Credentials: admin / amp_admin"
    echo ""
    echo "🔧 Management Commands:"
    echo "   - Check status: docker-compose -f docker-compose.amp.yml ps"
    echo "   - View logs: docker logs amp-trading-system"
    echo "   - Stop system: docker-compose -f docker-compose.amp.yml down"
    echo "   - Restart system: docker-compose -f docker-compose.amp.yml restart"
    echo ""
    echo "⚡ AMP CLI Commands:"
    echo "   - System status: docker exec -it amp-trading-system amp status"
    echo "   - Authentication: docker exec -it amp-trading-system amp auth --status"
    echo "   - Start scheduler: docker exec -it amp-trading-system amp schedule --start"
    echo "   - Monitor dashboard: docker exec -it amp-trading-system amp monitor --dashboard"
    echo ""
    echo "📁 Data Directories:"
    echo "   - Logs: ./logs/"
    echo "   - Data: ./data/"
    echo "   - Reports: ./reports/"
    echo ""
}

# Main deployment function
main() {
    echo "Starting AMP system deployment..."
    echo ""
    
    # Run checks
    check_docker
    check_docker_compose
    check_env_file
    create_directories
    
    # Pull latest image
    pull_image
    
    # Deploy
    deploy
    
    # Check status
    check_status
    
    # Show access information
    show_access_info
}

# Handle script arguments
case "${1:-}" in
    "status")
        print_status "Checking AMP system status..."
        docker-compose -f docker-compose.amp.yml ps
        ;;
    "logs")
        print_status "Showing AMP system logs..."
        docker logs amp-trading-system
        ;;
    "stop")
        print_status "Stopping AMP system..."
        docker-compose -f docker-compose.amp.yml down
        print_success "AMP system stopped"
        ;;
    "restart")
        print_status "Restarting AMP system..."
        docker-compose -f docker-compose.amp.yml restart
        print_success "AMP system restarted"
        ;;
    "help"|"-h"|"--help")
        echo "AMP System Docker Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Deploy the AMP system"
        echo "  status     Check system status"
        echo "  logs       Show system logs"
        echo "  stop       Stop the system"
        echo "  restart    Restart the system"
        echo "  help       Show this help message"
        ;;
    *)
        main
        ;;
esac