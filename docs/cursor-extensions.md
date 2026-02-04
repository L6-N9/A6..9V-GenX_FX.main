# 🚀 Essential Cursor Extensions for GenX FX

## 🎯 Core Development Extensions

### **Python Development**
- **Python** - Microsoft Python extension
- **Pylance** - Advanced Python language server
- **Python Debugger** - Enhanced debugging capabilities
- **autoDocstring** - Generate Python docstrings automatically

### **Web Development**
- **ES7+ React/Redux/React-Native snippets** - React development
- **TypeScript Importer** - Auto import TypeScript modules
- **Tailwind CSS IntelliSense** - Tailwind CSS support
- **Auto Rename Tag** - Rename paired HTML/XML tags

### **API & Backend**
- **REST Client** - Test APIs directly in Cursor
- **Thunder Client** - Lightweight REST API client
- **Docker** - Docker container management
- **YAML** - YAML language support

### **Database & Cloud**
- **PostgreSQL** - PostgreSQL syntax highlighting
- **MongoDB for VS Code** - MongoDB integration
- **Google Cloud Code** - GCP integration
- **Firebase** - Firebase project management

### **Trading & Finance**
- **MQL4/MQL5** - MetaTrader language support
- **CSV Rainbow** - Colorize CSV files
- **Excel Viewer** - View Excel files in editor

### **Git & Version Control**
- **GitLens** - Enhanced Git capabilities
- **Git Graph** - Visualize Git repository
- **GitHub Pull Requests** - GitHub integration

### **AI & Productivity**
- **GitHub Copilot** - AI code completion
- **Cursor AI** - Built-in AI assistant
- **Code Spell Checker** - Spell check in code
- **Todo Tree** - Highlight TODO comments

## 🛠️ Installation Commands

### **Quick Install (Copy to Cursor terminal):**
```bash
# Core Python
cursor --install-extension ms-python.python
cursor --install-extension ms-python.vscode-pylance
cursor --install-extension ms-python.debugpy

# Web Development
cursor --install-extension dsznajder.es7-react-js-snippets
cursor --install-extension bradlc.vscode-tailwindcss
cursor --install-extension formulahendry.auto-rename-tag

# API & Backend
cursor --install-extension humao.rest-client
cursor --install-extension rangav.vscode-thunder-client
cursor --install-extension ms-azuretools.vscode-docker

# Database & Cloud
cursor --install-extension ms-ossdata.vscode-postgresql
cursor --install-extension mongodb.mongodb-vscode
cursor --install-extension googlecloudtools.cloudcode

# Git & Productivity
cursor --install-extension eamodio.gitlens
cursor --install-extension mhutchie.git-graph
cursor --install-extension streetsidesoftware.code-spell-checker
```

## 🎯 GenX FX Specific Settings

### **Cursor Settings (settings.json):**
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.associations": {
    "*.mq4": "cpp",
    "*.mq5": "cpp",
    "*.env": "properties"
  },
  "emmet.includeLanguages": {
    "javascript": "javascriptreact"
  }
}
```

## 🚀 Recommended Workflow Extensions

### **For Trading Development:**
1. **MQL4/MQL5 Syntax** - MetaTrader language support
2. **CSV Rainbow** - Better CSV file visualization
3. **Excel Viewer** - View trading data files

### **For API Development:**
1. **REST Client** - Test GenX FX API endpoints
2. **OpenAPI (Swagger) Editor** - Edit API documentation
3. **JSON Tools** - Format and validate JSON

### **For Cloud Deployment:**
1. **Google Cloud Code** - GCP integration
2. **Firebase Tools** - Firebase management
3. **Docker** - Container management

## 📋 Installation Priority

### **High Priority (Install First):**
- Python + Pylance
- GitLens
- REST Client
- Docker

### **Medium Priority:**
- React/TypeScript extensions
- Tailwind CSS
- Thunder Client

### **Low Priority (Optional):**
- GitHub Copilot
- Advanced Git tools
- Specialized trading extensions

## 🎯 Quick Setup Command

```bash
# Install all essential extensions at once
cursor --install-extension ms-python.python ms-python.vscode-pylance eamodio.gitlens humao.rest-client ms-azuretools.vscode-docker dsznajder.es7-react-js-snippets bradlc.vscode-tailwindcss
```

**Copy and paste the quick setup command in Cursor terminal to install all essential extensions for GenX FX development!**