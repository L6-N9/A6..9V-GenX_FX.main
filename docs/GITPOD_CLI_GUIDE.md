# 🚀 Gitpod CLI Guide for AMP Trading System

## 📋 Overview

The Gitpod CLI wrapper (`gp`) provides a comprehensive interface for managing your AMP Trading System workspace. It combines Gitpod-like functionality with AMP-specific commands for seamless development and deployment.

## 🛠️ Installation

The Gitpod CLI wrapper is already included in your workspace:

```bash
# Make sure it's executable
chmod +x gp

# Test the installation
./gp --help
```

## 📚 Available Commands

### 🔍 **Information Commands**

#### `./gp info`
Shows comprehensive workspace information:
```bash
./gp info
```
**Output:**
- Workspace root directory
- AMP environment configuration
- Python version
- Docker version
- Git branch
- Gitpod workspace ID

#### `./gp status`
Shows AMP system status and health:
```bash
./gp status
```
**Output:**
- AMP CLI availability and functionality
- Environment configuration status
- Docker installation and status
- Port status for AMP services

### 🌐 **Port Management**

#### `./gp ports`
Lists and manages AMP system ports:
```bash
./gp ports
```
**Shows:**
- AMP API (port 8000)
- Grafana Dashboard (port 3000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Currently open ports

### 📋 **Task Management**

#### `./gp tasks`
Lists available AMP tasks:
```bash
./gp tasks
```
**Available Tasks:**
1. Setup Environment
2. Install Dependencies
3. Initialize AMP System
4. Start Scheduler
5. Run Monitoring
6. Build Docker Image

### 🔧 **Environment Management**

#### `./gp env`
Manages environment variables:
```bash
./gp env
```
**Features:**
- Shows current environment variables
- Validates .env file configuration
- Provides setup guidance

### 📖 **Documentation**

#### `./gp docs`
Opens AMP system documentation:
```bash
./gp docs
```
**Opens:**
- README.md (main documentation)
- AMP_CLI_INSTALLATION.md
- DOCKER_DEPLOYMENT_SUMMARY.md
- setup_docker_secrets.md

### 🚀 **System Initialization**

#### `./gp init`
Initializes the AMP system:
```bash
./gp init
```
**Performs:**
- Creates necessary directories (logs, reports, data)
- Copies .env.example to .env
- Installs Python dependencies
- Installs AMP-specific dependencies
- Makes scripts executable

### ⚡ **AMP CLI Integration**

#### `./gp run`
Runs AMP CLI commands:
```bash
# Show AMP CLI help
./gp run --help

# Check authentication status
./gp run auth --status

# Run a job
./gp run run

# Start scheduler
./gp run schedule --start

# Show monitoring dashboard
./gp run monitor --dashboard
```

### 🐳 **Docker Operations**

#### `./gp docker`
Manages Docker operations:
```bash
# Build Docker image
./gp docker build

# Run Docker container
./gp docker run

# Run with Docker Compose
./gp docker compose

# View Docker logs
./gp docker logs
```

### 📊 **Monitoring**

#### `./gp monitor`
Starts the AMP monitoring dashboard:
```bash
./gp monitor
```
**Features:**
- Real-time system monitoring
- Performance metrics
- Alert management
- Job execution status

## 🎯 **Quick Start Workflow**

### 1. **Initialize the System**
```bash
./gp init
```

### 2. **Check System Status**
```bash
./gp status
```

### 3. **Configure Environment**
```bash
# Edit .env file with your API keys
nano .env

# Verify configuration
./gp env
```

### 4. **Run AMP System**
```bash
# Authenticate
./gp run auth --token "your_token_here"

# Start scheduler
./gp run schedule --start

# Monitor system
./gp monitor
```

## 🔧 **Advanced Usage**

### **Custom AMP Commands**
```bash
# Run specific AMP commands
./gp run plugin install gemini
./gp run config set trading_enabled true
./gp run service enable scheduler
```

### **Docker Development**
```bash
# Build and test locally
./gp docker build
./gp docker run

# Deploy with compose
./gp docker compose
```

### **Environment Management**
```bash
# Check current environment
./gp env

# Update environment variables
export AMP_ENV=production
./gp status
```

## 🐛 **Troubleshooting**

### **Common Issues**

#### **AMP CLI Not Found**
```bash
# Check if files exist
ls -la amp_*.py

# Reinstall dependencies
./gp init
```

#### **Environment Not Configured**
```bash
# Initialize system
./gp init

# Check .env file
./gp env
```

#### **Docker Not Available**
```bash
# Check Docker installation
./gp status

# Install Docker if needed
sudo apt-get update && sudo apt-get install docker.io
```

### **Debug Mode**
```bash
# Run with verbose output
bash -x ./gp status
```

## 📊 **Integration with Gitpod**

### **Gitpod Workspace Features**
- **Automatic Port Management**: Ports are automatically exposed and managed
- **Environment Variables**: Seamless integration with Gitpod environment
- **Task Automation**: Pre-configured tasks for development
- **VS Code Integration**: Full IDE support with extensions

### **Gitpod-Specific Commands**
```bash
# Check if in Gitpod environment
echo $GITPOD_WORKSPACE_ID

# Access Gitpod features
./gp info
```

## 🎨 **Customization**

### **Adding Custom Commands**
You can extend the Gitpod CLI by adding new functions to the `gp` script:

```bash
# Add to gp script
custom_command() {
    echo "Your custom command here"
}

# Add to main case statement
"custom")
    custom_command
    ;;
```

### **Environment-Specific Configurations**
```bash
# Development environment
export AMP_ENV=development
./gp status

# Production environment
export AMP_ENV=production
./gp status
```

## 📈 **Performance Monitoring**

### **System Health Checks**
```bash
# Quick health check
./gp status

# Detailed monitoring
./gp monitor
```

### **Resource Usage**
```bash
# Check port usage
./gp ports

# Monitor system resources
htop
```

## 🔐 **Security Features**

### **Environment Variable Protection**
- Sensitive data stored in .env file
- .env file excluded from version control
- Secure credential management

### **Access Control**
- Token-based authentication
- Session management
- Secure API communication

## 🚀 **Deployment Integration**

### **CI/CD Pipeline**
```bash
# Build for deployment
./gp docker build

# Deploy to production
./gp docker compose
```

### **Cloud Deployment**
```bash
# Prepare for cloud deployment
./gp status
./gp docker build

# Deploy to cloud platform
# (Platform-specific commands)
```

---

## 📞 **Support**

For issues or questions:
1. Check the troubleshooting section
2. Review the AMP system documentation
3. Check system status with `./gp status`
4. Verify environment configuration with `./gp env`

---

**🎯 The Gitpod CLI wrapper provides a unified interface for managing your AMP Trading System!**