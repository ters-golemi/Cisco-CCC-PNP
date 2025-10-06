#!/bin/bash
# Cisco PnP Automation - Quick Setup Script
# This script automates the initial setup and deployment process

set -e

# Configuration
TOPOLOGY_FILE="topology/pnp-topology.yaml"
TEMPLATES_DIR="templates"
OUTPUT_DIR="generated_configs"
CATALYST_CENTER_IP=""
USERNAME=""
PASSWORD=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log "Python version: $PYTHON_VERSION"
    else
        error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check required directories
    if [ ! -d "$TEMPLATES_DIR" ]; then
        error "Templates directory not found: $TEMPLATES_DIR"
        exit 1
    fi
    
    if [ ! -f "$TOPOLOGY_FILE" ]; then
        error "Topology file not found: $TOPOLOGY_FILE"
        exit 1
    fi
    
    success "Prerequisites check completed"
}

# Install Python dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        python3 -m pip install -r requirements.txt
        success "Dependencies installed successfully"
    else
        error "requirements.txt not found"
        exit 1
    fi
}

# Validate templates
validate_templates() {
    log "Validating Jinja2 templates..."
    
    python3 scripts/config_generator.py \
        --validate \
        --templates "$TEMPLATES_DIR" \
        --topology "$TOPOLOGY_FILE"
    
    if [ $? -eq 0 ]; then
        success "All templates validated successfully"
    else
        error "Template validation failed"
        exit 1
    fi
}

# Generate configurations
generate_configs() {
    log "Generating device configurations..."
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    python3 scripts/config_generator.py \
        --topology "$TOPOLOGY_FILE" \
        --templates "$TEMPLATES_DIR" \
        --output "$OUTPUT_DIR" \
        --summary
    
    if [ $? -eq 0 ]; then
        success "Configurations generated in $OUTPUT_DIR"
        
        # List generated files
        log "Generated files:"
        ls -la "$OUTPUT_DIR/"
    else
        error "Configuration generation failed"
        exit 1
    fi
}

# Interactive configuration
interactive_setup() {
    echo ""
    echo "=== Cisco PnP Automation Setup ==="
    echo ""
    
    # Get Catalyst Center details
    read -p "Catalyst Center IP Address: " CATALYST_CENTER_IP
    read -p "Username: " USERNAME
    read -s -p "Password: " PASSWORD
    echo ""
    
    # Validate connectivity (optional)
    if command -v ping &> /dev/null; then
        log "Testing connectivity to Catalyst Center..."
        if ping -c 3 "$CATALYST_CENTER_IP" > /dev/null 2>&1; then
            success "Catalyst Center is reachable"
        else
            warning "Cannot ping Catalyst Center (this may be normal if ICMP is blocked)"
        fi
    fi
}

# Deploy configurations
deploy_configs() {
    if [ -z "$CATALYST_CENTER_IP" ] || [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]; then
        warning "Catalyst Center credentials not provided. Skipping automated deployment."
        return 0
    fi
    
    log "Starting automated deployment to Catalyst Center..."
    
    python3 scripts/pnp_automation.py \
        --host "$CATALYST_CENTER_IP" \
        --username "$USERNAME" \
        --password "$PASSWORD" \
        --topology "$TOPOLOGY_FILE" \
        --templates "$TEMPLATES_DIR"
    
    if [ $? -eq 0 ]; then
        success "Deployment completed successfully"
    else
        error "Deployment failed. Check logs for details."
        exit 1
    fi
}

# Show DHCP configuration
show_dhcp_config() {
    log "Generating DHCP Option 43 configuration..."
    
    if [ -n "$CATALYST_CENTER_IP" ]; then
        # Calculate Option 43 hex value
        OPTION43_STRING="5A1D;B2;K4;I${CATALYST_CENTER_IP};J80"
        OPTION43_HEX=$(python3 -c "print('${OPTION43_STRING}'.encode('ascii').hex())")
        
        echo ""
        echo "=== DHCP SERVER CONFIGURATION ==="
        echo ""
        echo "Cisco DHCP Server:"
        echo "ip dhcp pool PNP_POOL"
        echo " network 10.10.10.0 255.255.255.0"
        echo " default-router 10.10.10.1"
        echo " dns-server 8.8.8.8 8.8.4.4"
        echo " option 43 hex $OPTION43_HEX"
        echo ""
        echo "ISC DHCP Server (Linux):"
        echo "option pnp-string code 43 = string;"
        echo "subnet 10.10.10.0 netmask 255.255.255.0 {"
        echo "    range 10.10.10.100 10.10.10.200;"
        echo "    option routers 10.10.10.1;"
        echo "    option domain-name-servers 8.8.8.8, 8.8.4.4;"
        echo "    option pnp-string \"$OPTION43_STRING\";"
        echo "}"
        echo ""
    fi
}

# Main menu
show_menu() {
    echo ""
    echo "=== Cisco PnP Automation Tool ==="
    echo ""
    echo "1. Full Setup (Interactive)"
    echo "2. Install Dependencies Only"
    echo "3. Validate Templates Only"
    echo "4. Generate Configurations Only"
    echo "5. Deploy to Catalyst Center"
    echo "6. Show DHCP Configuration"
    echo "7. Exit"
    echo ""
}

# Main execution
main() {
    # Check if running in non-interactive mode
    if [ "$1" == "--auto" ]; then
        log "Running in automatic mode..."
        check_prerequisites
        install_dependencies
        validate_templates
        generate_configs
        success "Automatic setup completed. Use option 5 to deploy."
        exit 0
    fi
    
    # Interactive mode
    while true; do
        show_menu
        read -p "Select an option (1-7): " choice
        
        case $choice in
            1)
                check_prerequisites
                install_dependencies
                validate_templates
                generate_configs
                interactive_setup
                deploy_configs
                show_dhcp_config
                success "Full setup completed!"
                ;;
            2)
                check_prerequisites
                install_dependencies
                ;;
            3)
                check_prerequisites
                validate_templates
                ;;
            4)
                check_prerequisites
                generate_configs
                ;;
            5)
                check_prerequisites
                interactive_setup
                deploy_configs
                ;;
            6)
                interactive_setup
                show_dhcp_config
                ;;
            7)
                log "Exiting..."
                exit 0
                ;;
            *)
                error "Invalid option. Please select 1-7."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Script entry point
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi