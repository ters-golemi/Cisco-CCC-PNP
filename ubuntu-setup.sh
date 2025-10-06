#!/bin/bash
# ubuntu-setup.sh - Ubuntu Environment Setup for Cisco PnP Automation Lab
# This script prepares an Ubuntu workstation for the Cisco PnP automation project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running on Ubuntu
check_ubuntu() {
    if ! grep -q "Ubuntu" /etc/os-release; then
        error "This script is designed for Ubuntu. Detected OS: $(lsb_release -d | cut -f2)"
        exit 1
    fi
    
    UBUNTU_VERSION=$(lsb_release -r | cut -f2)
    log "Detected Ubuntu version: $UBUNTU_VERSION"
    
    # Check for supported versions
    if [[ "$UBUNTU_VERSION" < "20.04" ]]; then
        warning "Ubuntu 20.04+ recommended. Current version: $UBUNTU_VERSION"
    fi
}

# Check for sudo privileges
check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        log "Checking sudo privileges..."
        sudo -v || {
            error "This script requires sudo privileges"
            exit 1
        }
    fi
    success "Sudo privileges confirmed"
}

# Update system packages
update_system() {
    log "Updating Ubuntu system packages..."
    sudo apt update
    sudo apt upgrade -y
    success "System packages updated"
}

# Install system dependencies
install_system_dependencies() {
    log "Installing system dependencies..."
    
    # Essential build tools
    sudo apt install -y \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Python development
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-dev \
        python3-venv \
        python3-setuptools \
        python3-wheel \
        python3-distutils
    
    # Network tools
    sudo apt install -y \
        net-tools \
        iputils-ping \
        traceroute \
        nmap \
        tcpdump \
        dnsutils \
        openssh-client \
        wget
    
    # Development tools
    sudo apt install -y \
        git \
        git-lfs \
        nano \
        vim \
        tree \
        htop
    
    success "System dependencies installed"
}

# Install Python dependencies
setup_python_environment() {
    log "Setting up Python environment..."
    
    # Upgrade pip
    python3 -m pip install --user --upgrade pip
    
    # Create project directory
    PROJECT_DIR="$HOME/network-automation"
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # Create virtual environment
    log "Creating Python virtual environment..."
    python3 -m venv cisco-pnp-env
    
    # Activate virtual environment
    source cisco-pnp-env/bin/activate
    
    # Upgrade pip in virtual environment
    pip install --upgrade pip setuptools wheel
    
    # Install core Python packages
    log "Installing Python packages..."
    pip install \
        requests \
        PyYAML \
        Jinja2 \
        urllib3 \
        certifi \
        colorlog \
        python-dotenv
    
    # Install optional packages for network automation
    pip install \
        netmiko \
        napalm \
        paramiko \
        jsonschema \
        ruamel.yaml
    
    # Install development tools
    pip install \
        pytest \
        pytest-mock \
        Sphinx \
        sphinx-rtd-theme
    
    success "Python environment configured at: $PROJECT_DIR/cisco-pnp-env"
    
    # Create activation script
    cat << EOF > "$PROJECT_DIR/activate-env.sh"
#!/bin/bash
# Activation script for Cisco PnP environment
source $PROJECT_DIR/cisco-pnp-env/bin/activate
cd $PROJECT_DIR/Cisco-CCC-PNP 2>/dev/null || cd $PROJECT_DIR
echo "Cisco PnP environment activated"
echo "Current directory: \$(pwd)"
echo "Python: \$(which python)"
EOF
    
    chmod +x "$PROJECT_DIR/activate-env.sh"
    
    return 0
}

# Clone the project repository
clone_project() {
    log "Cloning Cisco PnP project repository..."
    
    PROJECT_DIR="$HOME/network-automation"
    cd "$PROJECT_DIR"
    
    if [ -d "Cisco-CCC-PNP" ]; then
        warning "Project directory already exists. Updating..."
        cd Cisco-CCC-PNP
        git pull origin main
    else
        git clone https://github.com/ters-golemi/Cisco-CCC-PNP.git
        cd Cisco-CCC-PNP
    fi
    
    # Make scripts executable
    chmod +x setup.sh
    find scripts -name "*.py" -exec chmod +x {} \;
    
    success "Project repository cloned to: $PROJECT_DIR/Cisco-CCC-PNP"
}

# Install project dependencies
install_project_dependencies() {
    log "Installing project-specific dependencies..."
    
    PROJECT_DIR="$HOME/network-automation"
    cd "$PROJECT_DIR/Cisco-CCC-PNP"
    
    # Activate virtual environment
    source ../cisco-pnp-env/bin/activate
    
    # Install from requirements.txt if it exists
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    success "Project dependencies installed"
}

# Verify installation
verify_installation() {
    log "Verifying installation..."
    
    PROJECT_DIR="$HOME/network-automation"
    source "$PROJECT_DIR/cisco-pnp-env/bin/activate"
    cd "$PROJECT_DIR/Cisco-CCC-PNP"
    
    echo ""
    echo "=== Installation Verification ==="
    
    # Check Python version
    PYTHON_VERSION=$(python --version)
    echo "Python Version: $PYTHON_VERSION"
    
    # Check pip version
    PIP_VERSION=$(pip --version)
    echo "Pip Version: $PIP_VERSION"
    
    # Check virtual environment
    echo "Virtual Environment: $VIRTUAL_ENV"
    
    # Check essential imports
    python -c "
import requests, yaml, jinja2, urllib3, json, os, time, logging
from datetime import datetime
print('[OK] All core packages imported successfully')
" || {
        error "Python package import failed"
        return 1
    }
    
    # Check project scripts
    python -m py_compile scripts/pnp_automation.py
    python -m py_compile scripts/config_generator.py
    echo "[OK] Project scripts compiled successfully"
    
    # Check network connectivity
    if ping -c 3 8.8.8.8 >/dev/null 2>&1; then
        echo "[OK] Internet connectivity verified"
    else
        warning "No internet connectivity detected"
    fi
    
    # Check essential commands
    for cmd in git curl ssh; do
        if command -v $cmd >/dev/null 2>&1; then
            echo "[OK] $cmd command available"
        else
            error "$cmd command not found"
        fi
    done
    
    echo ""
    success "Installation verification completed"
    
    echo ""
    echo "=== Next Steps ==="
    echo "1. Activate environment: source $PROJECT_DIR/activate-env.sh"
    echo "2. Edit topology: nano $PROJECT_DIR/Cisco-CCC-PNP/topology/pnp-topology.yaml"
    echo "3. Run setup: cd $PROJECT_DIR/Cisco-CCC-PNP && ./setup.sh"
    echo ""
}

# Create desktop shortcut (optional)
create_shortcuts() {
    log "Creating desktop shortcuts..."
    
    DESKTOP_DIR="$HOME/Desktop"
    PROJECT_DIR="$HOME/network-automation"
    
    if [ -d "$DESKTOP_DIR" ]; then
        # Create terminal shortcut for Cisco PnP environment
        cat << EOF > "$DESKTOP_DIR/Cisco-PnP-Terminal.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Cisco PnP Terminal
Comment=Terminal with Cisco PnP environment activated
Icon=terminal
Exec=gnome-terminal --working-directory="$PROJECT_DIR/Cisco-CCC-PNP" --command="bash -c 'source ../cisco-pnp-env/bin/activate; echo Welcome to Cisco PnP Automation Lab; bash'"
Terminal=false
Categories=Development;
EOF
        
        chmod +x "$DESKTOP_DIR/Cisco-PnP-Terminal.desktop"
        success "Desktop shortcut created"
    fi
}

# Main installation function
main() {
    echo ""
    echo "=============================================="
    echo "  Cisco PnP Automation Lab - Ubuntu Setup"
    echo "=============================================="
    echo ""
    
    check_ubuntu
    check_sudo
    
    log "Starting Ubuntu environment setup..."
    
    # Install components
    update_system
    install_system_dependencies
    setup_python_environment
    clone_project
    install_project_dependencies
    
    # Verify and finalize
    verify_installation
    create_shortcuts
    
    echo ""
    echo "=============================================="
    success "Ubuntu setup completed successfully!"
    echo "=============================================="
    echo ""
    
    # Final instructions
    echo "To get started:"
    echo "  cd ~/network-automation"
    echo "  source activate-env.sh"
    echo "  cd Cisco-CCC-PNP"
    echo "  ./setup.sh"
    echo ""
}

# Script entry point
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi