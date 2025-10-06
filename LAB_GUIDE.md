# Cisco Network Plug and Play (PnP) Automation Lab
## Student Lab Guide - Catalyst Center 3.1.x

**Course**: Advanced Network Automation  
**Lab Duration**: 3-4 hours  
**Difficulty Level**: Intermediate to Advanced  
**Prerequisites**: Basic Python, Cisco networking fundamentals, CLI experience, Catalyst Center 3.1.x familiarity

---

## Lab Objectives

By the end of this lab, you will be able to:

1. Configure and deploy Cisco Network Plug and Play (PnP) automation using Catalyst Center 3.1.x
2. Set up DHCP Option 43 for automatic device discovery with enhanced 3.1.x protocol support
3. Create and customize Jinja2 configuration templates with 3.1.x template versioning and commit features
4. Use Python scripts to interact with Catalyst Center 3.1.x Intent APIs with improved authentication
5. Leverage enhanced task management, real-time monitoring, and advanced site hierarchy features
6. Implement geographic site management with latitude/longitude support in 3.1.x
7. Provision multiple network devices using zero-touch deployment with enhanced workflow management
8. Monitor device provisioning status using 3.1.x enhanced task tracking and progress indicators
9. Troubleshoot common PnP deployment issues using 3.1.x diagnostic tools and improved logging

---

## Lab Topology

```
                    ┌─────────────────┐
                    │   Catalyst      │
                    │   Center        │
                    │ 172.16.1.10     │
                    └─────────────────┘
                             │
                    ┌─────────────────┐
                    │   DHCP Server   │
                    │   10.10.10.1    │
                    └─────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ Branch      │ │ Gateway     │ │ Wireless    │
    │ Router      │ │ Router      │ │ Controller  │
    │ 8000v       │ │ CSR1000v    │ │ 9800-L      │
    └─────────────┘ └─────────────┘ └─────────────┘
                             │
                    ┌─────────────────┐
                    │ Access Points   │
                    │ 9130AXE (x3)    │
                    └─────────────────┘
```

---

## Catalyst Center 3.1.x Enhanced Features

This lab leverages the advanced capabilities introduced in Cisco Catalyst Center 3.1.x:

### New API Enhancements
- **Enhanced Authentication**: Automatic token renewal and improved session management
- **Advanced Task Management**: Real-time progress tracking with detailed status reporting
- **Improved Error Handling**: Better exception management and retry logic for API calls
- **Enhanced Filtering**: Device state filtering and advanced query capabilities

### Site Management Improvements
- **Geographic Information**: Latitude/longitude support for site locations
- **Enhanced Site Hierarchy**: Multi-level site organization with area/building/floor structure
- **Automated Device Assignment**: Streamlined device-to-site assignment workflows

### Template Management Features
- **Template Versioning**: Automatic version control and commit functionality
- **Project Organization**: Template grouping and project-based management
- **Rollback Support**: Template rollback capabilities for configuration changes
- **Enhanced Validation**: Improved Jinja2 template syntax validation

### Monitoring and Diagnostics
- **Real-time Task Monitoring**: Live progress updates during device provisioning
- **Enhanced Device Status**: Detailed provisioning state information and workflow tracking
- **Improved Logging**: Comprehensive audit trails and diagnostic information
- **Advanced Troubleshooting**: Better error messages and resolution guidance

---

## Equipment Requirements

### Virtual Infrastructure
- **Catalyst Center**: Version 3.1.x required (3.1.0+ recommended for full feature support)
- **DHCP Server**: Windows Server, Linux ISC-DHCP, or Cisco router with Option 43 support
- **Python Environment**: Python 3.8+ with enhanced REST API libraries for 3.1.x compatibility
- **Network Connectivity**: Reliable connection to Catalyst Center for API operations

### Network Devices (Virtual or Physical)
- **ISR 8000v**: Branch router simulation
- **CSR1000v**: Gateway/core router
- **Catalyst 9800-L**: Wireless LAN Controller
- **Catalyst 9130AXE**: Access Points (3 units)

### Software Tools
- **Terminal/SSH Client**: PuTTY, Terminal, or VS Code
- **Text Editor**: VS Code, Notepad++, or vim
- **Git**: For project management
- **Web Browser**: For Catalyst Center GUI access

---

## Pre-Lab Setup

### Task 1: Ubuntu Administrator Workstation Preparation

This project must be deployed from an Ubuntu administrator device. Follow these steps to prepare your Ubuntu workstation.

#### System Requirements
- **Ubuntu Version**: 20.04 LTS or 22.04 LTS (recommended)
- **Memory**: Minimum 4GB RAM, 8GB recommended
- **Storage**: 10GB free space
- **Network**: Internet connectivity and access to lab network
- **User Privileges**: sudo access required

#### Step 1: Update Ubuntu System

1. **Update Package Lists and System**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Essential Build Tools**
   ```bash
   sudo apt install -y build-essential software-properties-common apt-transport-https ca-certificates curl gnupg lsb-release
   ```

#### Step 2: Install Python and Development Dependencies

1. **Install Python 3.8+ and Related Packages**
   ```bash
   # Install Python and development headers
   sudo apt install -y python3 python3-pip python3-dev python3-venv python3-setuptools
   
   # Install additional Python tools
   sudo apt install -y python3-wheel python3-distutils
   
   # Verify Python installation
   python3 --version
   # Expected output: Python 3.8.x or higher
   ```

2. **Install pip and Update to Latest Version**
   ```bash
   # Ensure pip is installed and updated
   python3 -m pip install --upgrade pip
   
   # Verify pip installation
   pip3 --version
   ```

#### Step 3: Install Network and System Dependencies

1. **Install Network Tools**
   ```bash
   # Essential network utilities
   sudo apt install -y net-tools iputils-ping traceroute nmap tcpdump
   
   # SSH client and curl for API testing
   sudo apt install -y openssh-client curl wget
   
   # DNS utilities
   sudo apt install -y dnsutils
   ```

2. **Install Git and Version Control Tools**
   ```bash
   sudo apt install -y git git-lfs
   
   # Configure Git (replace with your information)
   git config --global user.name "Your Name"
   git config --global user.email "your.email@domain.com"
   
   # Verify Git installation
   git --version
   ```

3. **Install Text Editors and Development Tools**
   ```bash
   # Install nano, vim, and other editors
   sudo apt install -y nano vim tree
   
   # Optional: Install VS Code
   wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
   sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
   sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
   sudo apt update
   sudo apt install -y code
   ```

#### Step 4: Install SSL/TLS and Security Dependencies

1. **Install SSL Certificates and Security Tools**
   ```bash
   # SSL/TLS certificates and tools
   sudo apt install -y ca-certificates openssl
   
   # Install additional security tools
   sudo apt install -y gnupg2 software-properties-common
   ```

#### Step 5: Python Virtual Environment Setup

1. **Create Project Directory and Virtual Environment**
   ```bash
   # Create project directory
   mkdir -p ~/network-automation
   cd ~/network-automation
   
   # Create virtual environment
   python3 -m venv cisco-pnp-env
   
   # Activate virtual environment
   source cisco-pnp-env/bin/activate
   
   # Verify virtual environment
   which python
   # Should show path to virtual environment
   ```

2. **Install Python Package Dependencies**
   ```bash
   # Ensure virtual environment is activated
   source ~/network-automation/cisco-pnp-env/bin/activate
   
   # Upgrade pip in virtual environment
   pip install --upgrade pip setuptools wheel
   
   # Install core dependencies
   pip install requests PyYAML Jinja2 urllib3 certifi
   
   # Install development and testing dependencies
   pip install pytest pytest-mock colorlog python-dotenv
   
   # Install optional network automation libraries
   pip install netmiko napalm paramiko jsonschema ruamel.yaml
   
   # Install documentation tools
   pip install Sphinx sphinx-rtd-theme
   ```

#### Step 6: Verify Complete Installation

1. **System Verification Script**
   ```bash
   # Create verification script
   cat << 'EOF' > ~/verify-ubuntu-setup.sh
   #!/bin/bash
   
   echo "=== Ubuntu Setup Verification ==="
   echo ""
   
   # Check Python
   echo "Python Version:"
   python3 --version
   echo ""
   
   # Check pip
   echo "Pip Version:"
   pip3 --version
   echo ""
   
   # Check Git
   echo "Git Version:"
   git --version
   echo ""
   
   # Check network connectivity
   echo "Network Connectivity:"
   ping -c 3 8.8.8.8 > /dev/null && echo "[OK] Internet connectivity verified" || echo "[FAIL] No internet connectivity"
   echo ""
   
   # Check essential commands
   echo "Essential Tools:"
   command -v curl >/dev/null 2>&1 && echo "[OK] curl installed" || echo "[MISSING] curl not found"
   command -v wget >/dev/null 2>&1 && echo "[OK] wget installed" || echo "[MISSING] wget not found"
   command -v ssh >/dev/null 2>&1 && echo "[OK] ssh client installed" || echo "[MISSING] ssh client not found"
   command -v git >/dev/null 2>&1 && echo "[OK] git installed" || echo "[MISSING] git not found"
   echo ""
   
   # Check Python packages (if virtual env is active)
   if [[ "$VIRTUAL_ENV" != "" ]]; then
       echo "Virtual Environment Active: $VIRTUAL_ENV"
       echo "Python Packages:"
       python -c "import requests, yaml, jinja2; print('[OK] Core packages installed')" 2>/dev/null || echo "[FAIL] Core packages missing"
   else
       echo "[WARNING] Virtual environment not activated"
   fi
   echo ""
   
   echo "=== Verification Complete ==="
   EOF
   
   # Make script executable
   chmod +x ~/verify-ubuntu-setup.sh
   
   # Run verification
   ~/verify-ubuntu-setup.sh
   ```

### Task 2: Environment Verification

1. **Verify Python Installation**
   ```bash
   python3 --version
   # Expected output: Python 3.8.x or higher
   ```

2. **Check Network Connectivity**
   ```bash
   ping -c 3 172.16.1.10  # Catalyst Center
   ping -c 3 10.10.10.1   # DHCP Server
   
   # Test HTTPS connectivity to Catalyst Center
   curl -k -I https://172.16.1.10 2>/dev/null | head -1
   ```

3. **Verify Catalyst Center Access**
   - Open browser: `https://172.16.1.10`
   - Login with provided credentials
   - Navigate to System > Settings > External Services > PnP

4. **Test SSH Connectivity to Network Devices**
   ```bash
   # Test SSH access to sample device (replace IP as needed)
   ssh admin@10.10.10.10 "show version" 2>/dev/null || echo "SSH access test - configure as needed"
   ```

### Task 2: Download Lab Files

1. **Clone the Project Repository**
   ```bash
   cd ~/Desktop
   git clone https://github.com/ters-golemi/Cisco-CCC-PNP.git
   cd Cisco-CCC-PNP
   ```

2. **Verify Project Structure**
   ```bash
   ls -la
   # Verify all directories: topology/, templates/, scripts/
   ```

---

## Lab Exercise 1: Project Setup and Configuration

### Step 1: Project Installation on Ubuntu

1. **Activate Virtual Environment**
   ```bash
   # Navigate to project directory
   cd ~/network-automation
   
   # Activate virtual environment
   source cisco-pnp-env/bin/activate
   
   # Verify activation
   echo $VIRTUAL_ENV
   # Should show path to cisco-pnp-env
   ```

2. **Clone Project Repository**
   ```bash
   # Ensure we're in the right directory
   cd ~/network-automation
   
   # Clone the Cisco PnP project
   git clone https://github.com/ters-golemi/Cisco-CCC-PNP.git
   cd Cisco-CCC-PNP
   
   # Verify project structure
   ls -la
   tree . -L 2  # Optional: if tree is installed
   ```

3. **Install Project Dependencies**
   ```bash
   # Install from requirements.txt
   pip install -r requirements.txt
   
   # Alternative: Install dependencies manually if requirements.txt fails
   pip install requests PyYAML Jinja2 urllib3 certifi colorlog python-dotenv
   pip install netmiko napalm paramiko jsonschema ruamel.yaml
   ```

4. **Verify Complete Installation**
   ```bash
   # Test all required imports
   python3 -c "
   try:
       import requests, yaml, jinja2, urllib3, json, os, time, logging
       from datetime import datetime
       print('[OK] All core packages imported successfully')
   except ImportError as e:
       print(f'[FAIL] Import error: {e}')
   "
   
   # Test project scripts syntax
   python3 -m py_compile scripts/pnp_automation.py
   python3 -m py_compile scripts/config_generator.py
   echo "[OK] Scripts compiled successfully"
   ```

5. **Set Up Project Permissions**
   ```bash
   # Make scripts executable
   chmod +x setup.sh
   chmod +x scripts/*.py
   
   # Verify permissions
   ls -la setup.sh scripts/
   ```

### Step 2: Customize Network Topology

1. **Edit Topology File**
   ```bash
   nano topology/pnp-topology.yaml
   # OR use your preferred editor
   ```

2. **Update Device Information**
   
   **IMPORTANT**: Replace the following values with your lab environment:
   
   ```yaml
   catalyst_center:
     ip_address: "172.16.1.10"        # Your Catalyst Center IP
     settings:
       username: "admin"               # Your admin username
       password: "Cisco123!"           # Your admin password
       domain: "lab.local"             # Your lab domain
   ```

3. **Update Device Serial Numbers**
   
   Find each device section and update with actual serial numbers:
   ```yaml
   devices:
     branch-router-01:
       serial_number: "YOUR_ACTUAL_SERIAL"  # Replace with device serial
   ```

   **How to Find Serial Numbers:**
   - Physical devices: Check device label
   - Virtual devices: Use `show version` command
   - Simulator: Use assigned lab serials

### Step 3: Validate Configuration

1. **Run Template Validation**
   ```bash
   python scripts/config_generator.py \
     --validate \
     --templates templates \
     --topology topology/pnp-topology.yaml
   ```

2. **Expected Output:**
   ```
   Template validation: 5/5 templates valid
   ```

---

## Lab Exercise 2: DHCP Option 43 Configuration (3.1.x Enhanced)

### Step 1: Calculate Option 43 Value (3.1.x Format)

1. **Generate Basic Option 43 String (HTTP)**
   ```bash
   python3 -c "
   catalyst_ip = '172.16.1.10'  # Replace with your Catalyst Center IP
   option43 = f'5A1N;B2;K4;I{catalyst_ip};J80;'
   hex_value = option43.encode('ascii').hex()
   print(f'Basic Option 43 String: {option43}')
   print(f'Basic Option 43 Hex: {hex_value}')
   "
   ```

2. **Generate Enhanced Option 43 String (HTTPS with NTP) - 3.1.x Recommended**
   ```bash
   python3 -c "
   catalyst_ip = '172.16.1.10'  # Replace with your Catalyst Center IP
   ntp_server = '172.16.1.1'    # Replace with your NTP server IP
   option43 = f'5A1D;B2;K5;I{catalyst_ip};J443;Z{ntp_server};'
   hex_value = option43.encode('ascii').hex()
   print(f'Enhanced 3.1.x Option 43 String: {option43}')
   print(f'Enhanced 3.1.x Option 43 Hex: {hex_value}')
   "
   ```

3. **Generate FQDN-Based Option 43 (3.1.x FQDN Support)**
   ```bash
   python3 -c "
   catalyst_fqdn = 'catalyst.lab.local'  # Replace with your FQDN
   ntp_server = '172.16.1.1'            # Replace with your NTP server
   option43 = f'5A1D;B1;K5;I{catalyst_fqdn};J443;Z{ntp_server};'
   hex_value = option43.encode('ascii').hex()
   print(f'FQDN-based 3.1.x Option 43 String: {option43}')
   print(f'FQDN-based 3.1.x Option 43 Hex: {hex_value}')
   "
   ```

4. **Record Your Values:**
   - Basic Option 43 String: `________________`
   - Enhanced 3.1.x Option 43 String: `________________`
   - FQDN-based Option 43 String: `________________`

### Step 2: Configure DHCP Server

Choose your DHCP server type and follow the appropriate section:

#### Option A: Cisco IOS-XE Router DHCP

1. **Access Router Console**
   ```
   Router> enable
   Router# configure terminal
   ```

2. **Basic DHCP Configuration**
   ```
   ! Enable DHCP service
   service dhcp
   
   ! Exclude static IP addresses from DHCP pool
   ip dhcp excluded-address 10.10.10.1 10.10.10.20
   ip dhcp excluded-address 10.10.10.250 10.10.10.255
   ```

3. **Configure PnP DHCP Pool**
   ```
   ! Create DHCP pool for PnP devices
   ip dhcp pool PNP_POOL
    network 10.10.10.0 255.255.255.0
    default-router 10.10.10.1
    dns-server 8.8.8.8 8.8.4.4
    domain-name lab.local
    lease 0 12 0
    option 43 hex 35413144423242334b344937322e31362e312e31304a3830
   exit
   ```

4. **Alternative Option 43 Configuration Methods**
   ```
   ! Method 1: Using hex string directly
   ip dhcp pool PNP_POOL
    option 43 hex 35413144423242334b344937322e31362e312e31304a3830
   
   ! Method 2: Using ASCII string (if supported)
   ip dhcp pool PNP_POOL
    option 43 ascii "5A1D;B2;K4;I172.16.1.10;J80"
   
   ! Method 3: Step-by-step hex calculation
   ! String: 5A1D;B2;K4;I172.16.1.10;J80
   ! Each character to hex: 35413144423242334b344937322e31362e312e31304a3830
   ```

5. **Verification Commands**
   ```
   ! Verify DHCP pool configuration
   show ip dhcp pool PNP_POOL
   
   ! Monitor DHCP bindings
   show ip dhcp binding
   
   ! Check DHCP conflicts
   show ip dhcp conflict
   
   ! Debug DHCP operations
   debug ip dhcp server events
   debug ip dhcp server packet
   ```

6. **Advanced DHCP Configuration**
   ```
   ! Multiple VLAN support
   ip dhcp pool VLAN10_POOL
    network 10.10.10.0 255.255.255.0
    default-router 10.10.10.1
    option 43 hex 35413144423242334b344937322e31362e312e31304a3830
   
   ip dhcp pool VLAN20_POOL
    network 10.10.20.0 255.255.255.0
    default-router 10.10.20.1
    option 43 hex 35413144423242334b344937322e31362e312e31304a3830
   
   ! DHCP relay configuration for remote subnets
   interface vlan 30
    ip helper-address 10.10.10.1
   ```

#### Option B: Linux ISC-DHCP

1. **Edit DHCP Configuration**
   ```bash
   sudo nano /etc/dhcp/dhcpd.conf
   ```

2. **Add Configuration Block**
   ```
   option pnp-string code 43 = string;
   
   subnet 10.10.10.0 netmask 255.255.255.0 {
     range 10.10.10.100 10.10.10.200;
     option routers 10.10.10.1;
     option domain-name-servers 8.8.8.8, 8.8.4.4;
     option domain-name "lab.local";
     default-lease-time 43200;
     max-lease-time 86400;
     option pnp-string "5A1D;B2;K4;I172.16.1.10;J80";
   }
   ```

3. **Restart DHCP Service**
   ```bash
   sudo systemctl restart isc-dhcp-server
   sudo systemctl status isc-dhcp-server
   ```

4. **Verify DHCP Operation**
   ```bash
   # Check DHCP leases
   sudo cat /var/lib/dhcp/dhcpd.leases
   
   # Monitor DHCP logs
   sudo tail -f /var/log/syslog | grep dhcp
   ```

### Step 3: Verify DHCP Configuration

1. **Test DHCP Lease**
   ```bash
   # From a test client
   sudo dhclient -r  # Release current lease
   sudo dhclient    # Request new lease
   ```

2. **Verify Option 43**
   ```bash
   # Check DHCP lease file for Option 43
   cat /var/lib/dhcp/dhclient.leases | grep option-43
   ```

---

## Lab Exercise 3: Configuration Generation

### Step 1: Generate Device Configurations

1. **Run Configuration Generator**
   ```bash
   python scripts/config_generator.py \
     --topology topology/pnp-topology.yaml \
     --templates templates \
     --output generated_configs \
     --summary
   ```

2. **Review Generated Files**
   ```bash
   ls -la generated_configs/
   cat generated_configs/deployment_summary.txt
   ```

### Step 2: Examine Configuration Templates

1. **Review Branch Router Template**
   ```bash
   cat generated_configs/branch-router-01.cfg
   ```

2. **Key Elements to Verify:**
   - Hostname configuration
   - Management IP address
   - DHCP Option 43 in configuration
   - Interface configurations
   - Default routes

### Step 3: Test Catalyst Center 3.1.x Template Management

1. **Create Template with 3.1.x Features**
   ```bash
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   client.authenticate()
   
   # Read sample template
   with open('templates/8000v-branch-router.j2', 'r') as f:
       template_content = f.read()
   
   # Create template with 3.1.x enhanced features
   template_id = client.create_configuration_template(
       template_name='Lab_Branch_Router_3.1x',
       device_type='Routers',
       template_content=template_content,
       project_name='PnP_Automation_Lab'
   )
   
   if template_id:
       print(f'Template created successfully with ID: {template_id}')
       
       # List templates in project (3.1.x feature)
       templates = client.get_templates(project_name='PnP_Automation_Lab')
       print(f'Templates in project: {len(templates)}')
   else:
       print('Template creation failed')
   "
   ```

2. **Expected Output (3.1.x Enhanced):**
   ```
   Template created successfully with ID: abc123-def456-ghi789
   Template committed successfully
   Templates in project: 1
   ```

3. **Student Exercise: Configuration Analysis**
   
   **Question 1:** What is the management IP address of your branch router?
   **Answer:** `________________`
   
   **Question 2:** Which VLAN is configured for guest access?
   **Answer:** `________________`
   
   **Question 3:** What is the OSPF area configured for internal routing?
   **Answer:** `________________`

---

## Lab Exercise 4: Catalyst Center Preparation

### Step 1: Access Catalyst Center

1. **Login to Web Interface**
   - URL: `https://172.16.1.10`
   - Username: `admin`
   - Password: `Cisco123!`

2. **Navigate to PnP Dashboard**
   - Menu: Provision → Plug and Play
   - Verify PnP service is running

### Step 2: Verify Catalyst Center 3.1.x API Connectivity

1. **Test Enhanced Authentication (3.1.x Features)**
   ```bash
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   success = client.authenticate()
   print('Authentication: Success' if success else 'Failed')
   
   # Test 3.1.x specific features
   if success:
       print(f'Token expires in: {client.token_expires} seconds')
       print(f'Token valid: {client.is_token_valid()}')
   "
   ```

2. **Expected Output (3.1.x Enhanced):**
   ```
   Authentication: Success
   Token expires in: 3600 seconds
   Token valid: True
   ```

### Step 3: Check Existing PnP Devices with 3.1.x Filtering

1. **List Current PnP Devices (Enhanced 3.1.x API)**
   ```bash
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   client.authenticate()
   
   # Get all devices
   all_devices = client.get_pnp_devices()
   print(f'Found {len(all_devices)} total PnP devices')
   
   # Use 3.1.x filtering capabilities
   unclaimed_devices = client.get_pnp_devices(device_state='Unclaimed')
   print(f'Unclaimed devices: {len(unclaimed_devices)}')
   
   provisioned_devices = client.get_pnp_devices(device_state='Provisioned')
   print(f'Provisioned devices: {len(provisioned_devices)}')
   
   for device in all_devices:
       serial = device.get('deviceInfo', {}).get('serialNumber', 'Unknown')
       state = device.get('deviceInfo', {}).get('state', 'Unknown')
       print(f'- {serial} (State: {state})')
   "
   ```

---

## Lab Exercise 5: Catalyst Center 3.1.x Site Management

### Step 1: Create Enhanced Site Hierarchy

1. **Create Site with Geographic Information (3.1.x Feature)**
   ```bash
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   client.authenticate()
   
   # Create area site with geographic information
   area_id = client.create_site_hierarchy(
       site_name='Lab_Campus_Area',
       site_type='area',
       parent_name='Global',
       address='123 Technology Drive, San Jose, CA 95134',
       country='United States',
       latitude=37.4419,
       longitude=-121.9438
   )
   
   if area_id:
       print(f'Area site created: {area_id}')
       
       # Create building under area
       building_id = client.create_site_hierarchy(
           site_name='Lab_Main_Building',
           site_type='building', 
           parent_name='Lab_Campus_Area',
           address='123 Technology Drive, Building A'
       )
       
       if building_id:
           print(f'Building site created: {building_id}')
   "
   ```

### Step 2: Verify Site Creation

1. **List Sites with 3.1.x Filtering**
   ```bash
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   client.authenticate()
   
   # Get all sites
   sites = client.get_sites()
   print(f'Total sites: {len(sites)}')
   
   # Filter by site type
   areas = client.get_sites(site_type='area')
   buildings = client.get_sites(site_type='building')
   
   print(f'Area sites: {len(areas)}')
   print(f'Building sites: {len(buildings)}')
   "
   ```

---

## Lab Exercise 6: 3.1.x Device Provisioning Workflows

### Step 1: Validate PnP Prerequisites (3.1.x)

1. **Run 3.1.x Prerequisites Validation**
   ```bash
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   
   # Validate all prerequisites according to 3.1.x documentation
   results = client.validate_pnp_prerequisites()
   
   print('=== PnP Prerequisites Validation (3.1.x) ===')
   for check, passed in results.items():
       status = 'PASS' if passed else 'FAIL'
       print(f'{check:<20}: {status}')
   
   all_passed = all(results.values())
   print(f'\\nOverall Status: {\"READY\" if all_passed else \"NOT READY\"} for PnP deployment')
   "
   ```

### Step 2: Generate DHCP Option 43 Strings

1. **Generate Multiple Option 43 Formats for 3.1.x**
   ```bash
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   
   # Generate various Option 43 strings for different scenarios
   print('=== DHCP Option 43 Generator (3.1.x) ===\\n')
   
   # Basic HTTP Option 43
   basic = client.generate_dhcp_option43_string(
       catalyst_center_ip='172.16.1.10',
       port=80,
       protocol='HTTP'
   )
   print(f'Basic HTTP: {basic}')
   
   # Enhanced HTTPS with NTP (recommended for 3.1.x)
   enhanced = client.generate_dhcp_option43_string(
       catalyst_center_ip='172.16.1.10',
       port=443,
       protocol='HTTPS',
       ntp_server='172.16.1.1'
   )
   print(f'Enhanced HTTPS: {enhanced}')
   
   # FQDN-based with security features
   fqdn = client.generate_dhcp_option43_string(
       catalyst_center_ip='catalyst.lab.local',
       port=443,
       protocol='HTTPS',
       ntp_server='ntp.lab.local',
       trusted_cert_url='tftp://172.16.1.100/ios.p7b'
   )
   print(f'FQDN with Security: {fqdn}')
   "
   ```

### Step 3: Physical Device Preparation (3.1.x Guidelines)

1. **Prepare Devices According to 3.1.x Best Practices**
   - Ensure devices are in factory default state (critical for 3.1.x)
   - Connect to management network with DHCP Option 43 configured
   - Verify NTP connectivity for certificate validation (3.1.x requirement)
   - Power on devices following recommended bring-up order

2. **Monitor Enhanced Console Output (3.1.x)**
   ```
   # Expected 3.1.x PnP discovery messages:
   %PNPA-5-DISCOVERY: PnP Discovery started
   %PNPA-5-PNP_DHCP_INSTALLED_SUCCESSFULLY: PnP DHCP client installed successfully
   %PNPA-5-CERTIFICATE_VALIDATION: Certificate validation in progress (3.1.x)
   %PNPA-5-PNP_DISCOVERY_DONE: PnP Discovery done successfully
   %PNPA-5-CONTROLLER_CONTACT: Successfully contacted Catalyst Center 3.1.x
   ```

### Step 2: Ubuntu Script Execution and Configuration Setup

1. **Pre-Deployment Environment Check**
   ```bash
   # Ensure virtual environment is active
   source ~/network-automation/cisco-pnp-env/bin/activate
   cd ~/network-automation/Cisco-CCC-PNP
   
   # Run the built-in setup verification
   ./setup.sh
   # Select option 2: "Install Dependencies Only" first
   
   # Alternative manual verification
   python3 scripts/config_generator.py --validate --templates templates --topology topology/pnp-topology.yaml
   ```

2. **Configure Network Connectivity Testing**
   ```bash
   # Test connectivity to Catalyst Center
   curl -k -X GET https://172.16.1.10/dna/system/api/v1/auth/token \
     -H "Content-Type: application/json" \
     -u admin:Cisco123! \
     --connect-timeout 10
   
   # Test DHCP server connectivity
   ping -c 3 10.10.10.1
   
   # Test SSH access to network segment
   nmap -p 22 10.10.10.0/24 | grep -E "(open|22)"
   ```

3. **Generate Device Configurations**
   ```bash
   # Create output directory
   mkdir -p generated_configs
   
   # Generate configurations for all devices
   python3 scripts/config_generator.py \
     --topology topology/pnp-topology.yaml \
     --templates templates \
     --output generated_configs \
     --summary
   
   # Verify generated configurations
   ls -la generated_configs/
   cat generated_configs/deployment_summary.txt
   
   # Review individual device configurations
   echo "=== Branch Router Configuration Preview ==="
   head -30 generated_configs/branch-router-01.cfg
   ```

4. **Test Catalyst Center API Authentication**
   ```bash
   # Test authentication with Python script
   python3 -c "
   import sys
   sys.path.append('./scripts')
   from pnp_automation import CatalystCenterPnP
   
   print('Testing Catalyst Center authentication...')
   try:
       client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
       success = client.authenticate()
       if success:
           print('[OK] Authentication successful')
           
           # Test getting PnP devices
           devices = client.get_pnp_devices()
           print(f'[OK] Found {len(devices)} PnP devices in inventory')
       else:
           print('[FAIL] Authentication failed')
   except Exception as e:
       print(f'[ERROR] Connection error: {e}')
   "
   ```

5. **Automated Deployment with Logging**
   ```bash
   # Create logs directory
   mkdir -p logs
   
   # Run PnP automation with detailed logging
   python3 scripts/pnp_automation.py \
     --host 172.16.1.10 \
     --username admin \
     --password Cisco123! \
     --topology topology/pnp-topology.yaml \
     --templates templates 2>&1 | tee logs/pnp_deployment_$(date +%Y%m%d_%H%M%S).log
   ```

6. **Alternative: Step-by-Step Deployment**
   ```bash
   # Step 1: Validate templates
   echo "=== Step 1: Template Validation ==="
   python3 scripts/config_generator.py --validate --templates templates --topology topology/pnp-topology.yaml
   
   # Step 2: Generate configurations
   echo "=== Step 2: Configuration Generation ==="
   python3 scripts/config_generator.py \
     --topology topology/pnp-topology.yaml \
     --templates templates \
     --output generated_configs \
     --summary
   
   # Step 3: Test API connectivity
   echo "=== Step 3: API Connectivity Test ==="
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   success = client.authenticate()
   print('Authentication:', 'SUCCESS' if success else 'FAILED')
   "
   
   # Step 4: Deploy configurations with 3.1.x task monitoring
   echo "=== Step 4: Enhanced Device Deployment (3.1.x) ==="
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   import time
   
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   client.authenticate()
   
   # Get unclaimed devices
   devices = client.get_pnp_devices(device_state='Unclaimed')
   print(f'Found {len(devices)} unclaimed devices')
   
   for device in devices[:1]:  # Process first device as example
       device_id = device.get('id')
       serial = device.get('deviceInfo', {}).get('serialNumber', 'Unknown')
       print(f'Processing device: {serial}')
       
       # Claim device with enhanced 3.1.x API
       task_id = client.claim_pnp_device(
           device_id=device_id,
           site_id='Lab_Main_Building'  # Use site created earlier
       )
       
       if task_id:
           print(f'Device claim initiated. Task ID: {task_id}')
           
           # Monitor task progress (3.1.x feature)
           result = client.wait_for_task_completion(task_id, max_wait_time=300)
           if result:
               print(f'Device {serial} provisioned successfully')
           else:
               print(f'Device {serial} provisioning failed or timed out')
       else:
           print(f'Failed to claim device {serial}')
   "
   ```

7. **Monitor Deployment Progress**
   ```bash
   # Monitor deployment in separate terminal
   # Terminal 1: Watch PnP automation log
   tail -f logs/pnp_deployment_*.log
   
   # Terminal 2: Monitor Catalyst Center (if GUI access available)
   # Open browser: https://172.16.1.10
   # Navigate: Provision > Plug and Play
   
   # Terminal 3: Monitor network device console (if console access available)
   # Watch for PnP discovery messages and configuration application
   ```

8. **Ubuntu System Monitoring During Deployment**
   ```bash
   # Monitor system resources during deployment
   # Terminal 4: System monitoring
   watch -n 2 "echo '=== System Resources ==='; free -h; echo; echo '=== Network Connections ==='; netstat -an | grep :443 | head -5"
   
   # Check active Python processes
   ps aux | grep python | grep pnp
   
   # Monitor network traffic to Catalyst Center
   sudo tcpdump -i any host 172.16.1.10 -c 10 2>/dev/null || echo "Run with sudo for packet capture"
   ```

### Step 3: Verify Device Status

1. **Check PnP Device Status**
   ```bash
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   client.authenticate()
   devices = client.get_pnp_devices()
   for device in devices:
       status = client.get_device_provisioning_status(device['id'])
       print(f'Device: {device.get(\"deviceInfo\", {}).get(\"serialNumber\")}')
       print(f'Status: {status.get(\"runSummaryList\", [{}])[0].get(\"details\", \"Unknown\")}')
   "
   ```

---

## Lab Exercise 6: Verification and Testing

### Step 1: Device Connectivity Verification

1. **Test Device Management Access**
   ```bash
   # Replace with your device management IPs
   ping 10.10.10.10  # Branch router
   ping 10.10.10.11  # Gateway router
   ping 10.10.10.12  # Wireless controller
   ```

2. **SSH Access Verification**
   ```bash
   ssh admin@10.10.10.10
   # Verify hostname and configuration
   show running-config | include hostname
   ```

### Step 2: Network Services Testing

1. **VLAN Connectivity**
   ```bash
   # From gateway router
   ping 10.10.10.1   # Management VLAN
   ping 10.10.30.1   # Corporate VLAN
   ping 10.10.40.1   # Guest VLAN
   ```

2. **Wireless Controller Testing**
   ```bash
   # SSH to WLC
   ssh admin@10.10.10.12
   
   # Check AP status
   show ap summary
   show wireless summary
   ```

### Step 3: Configuration Validation

1. **Verify Applied Templates**
   ```bash
   # On each device, verify key configurations
   show running-config | include ip route
   show running-config | include interface
   show running-config | include snmp
   ```

2. **Student Verification Checklist:**
   
   | Device | Management IP | Hostname | OSPF Process | Status |
   |--------|---------------|----------|--------------|---------|
   | Branch Router | | | | [ ] |
   | Gateway Router | | | | [ ] |
   | Wireless Controller | | | | [ ] |
   | Access Point 1 | | | | [ ] |
   | Access Point 2 | | | | [ ] |
   | Access Point 3 | | | | [ ] |

---

## Lab Exercise 7: Catalyst Center 3.1.x Troubleshooting and Diagnostics

### Scenario 1: Ubuntu Environment Issues

**Problem**: Python dependencies or environment problems

**Ubuntu-Specific Troubleshooting Steps:**

1. **Virtual Environment Issues**
   ```bash
   # Check if virtual environment is active
   echo $VIRTUAL_ENV
   
   # Reactivate if needed
   source ~/network-automation/cisco-pnp-env/bin/activate
   
   # Recreate virtual environment if corrupted
   cd ~/network-automation
   rm -rf cisco-pnp-env
   python3 -m venv cisco-pnp-env
   source cisco-pnp-env/bin/activate
   pip install --upgrade pip
   pip install -r Cisco-CCC-PNP/requirements.txt
   ```

2. **Package Installation Issues**
   ```bash
   # Check Ubuntu package dependencies
   sudo apt install -y python3-dev build-essential libssl-dev libffi-dev
   
   # Force reinstall Python packages
   pip install --force-reinstall requests PyYAML Jinja2
   
   # Check for conflicting system packages
   apt list --installed | grep python3
   ```

3. **Network Connectivity from Ubuntu**
   ```bash
   # Test DNS resolution
   nslookup 172.16.1.10
   
   # Test routing
   traceroute 172.16.1.10
   
   # Test firewall settings
   sudo ufw status
   
   # Test SSL/TLS connectivity
   openssl s_client -connect 172.16.1.10:443 -servername 172.16.1.10 < /dev/null
   ```

4. **File Permissions and Access**
   ```bash
   # Check file permissions
   ls -la ~/network-automation/Cisco-CCC-PNP/
   
   # Fix permissions if needed
   chmod +x ~/network-automation/Cisco-CCC-PNP/setup.sh
   chmod +x ~/network-automation/Cisco-CCC-PNP/scripts/*.py
   
   # Check directory ownership
   ls -ld ~/network-automation/
   ```

### Scenario 2: Device Not Discovered

**Problem**: Device not appearing in PnP inventory

**Ubuntu-Based Troubleshooting Steps:**

1. **Network Diagnostics from Ubuntu**
   ```bash
   # Test network path from Ubuntu to devices
   ping -c 3 10.10.10.0  # Network segment
   nmap -sn 10.10.10.0/24  # Network discovery
   
   # Check routing table
   ip route show
   
   # Test DHCP server from Ubuntu
   sudo nmap -sU -p 67 10.10.10.1  # DHCP port check
   ```

2. **DHCP Option 43 Verification from Ubuntu**
   ```bash
   # Install DHCP testing tools if needed
   sudo apt install -y dhcp-helper dhcpdump
   
   # Monitor DHCP traffic (requires sudo)
   sudo tcpdump -i any port 67 or port 68 -v
   
   # Test DHCP discovery
   sudo nmap --script dhcp-discover -e eth0
   ```

3. **Catalyst Center Connectivity from Ubuntu**
   ```bash
   # Detailed connectivity test
   curl -v -k https://172.16.1.10/dna/system/api/v1/auth/token 2>&1 | head -20
   
   # Test different connection methods
   telnet 172.16.1.10 80   # HTTP
   telnet 172.16.1.10 443  # HTTPS
   
   # Check SSL certificate
   echo | openssl s_client -servername 172.16.1.10 -connect 172.16.1.10:443 2>/dev/null | openssl x509 -inform pem -noout -text | grep -A2 "Subject:"
   ```

**Student Exercise:** Ubuntu troubleshooting documentation:
- Ubuntu version: `lsb_release -a`
- Virtual environment path: `echo $VIRTUAL_ENV`
- Python path: `which python3`
- Network interface: `ip addr show | grep -E "inet.*scope global"`
- Issue observed: `________________`
- Ubuntu-specific steps taken: `________________`
- Resolution: `________________`

### Scenario 2: Configuration Template Failure

**Problem**: Template application fails

**Troubleshooting Steps:**

1. **Check Template Syntax**
   ```bash
   python scripts/config_generator.py --validate --templates templates --topology topology/pnp-topology.yaml
   ```

2. **Verify Variable Values**
   ```bash
   # Generate test configuration
   python scripts/config_generator.py \
     --topology topology/pnp-topology.yaml \
     --templates templates \
     --output test_configs
   
   # Review generated configuration
   cat test_configs/branch-router-01.cfg
   ```

3. **Check Device Compatibility**
   - Verify device model matches template
   - Check software version compatibility
   - Review feature licensing

### Scenario 3: Network Connectivity Issues

**Problem**: Devices configured but not reachable

**Troubleshooting Steps:**

1. **Layer 3 Connectivity**
   ```bash
   traceroute 10.10.10.10
   show ip route
   show ip arp
   ```

2. **Layer 2 Verification**
   ```bash
   show vlan brief
   show interfaces trunk
   show spanning-tree
   ```

### Scenario 4: Catalyst Center 3.1.x Enhanced Diagnostics

**Use Case**: Leveraging 3.1.x diagnostic capabilities for troubleshooting

**Enhanced Diagnostic Steps:**

1. **Token and Authentication Diagnostics**
   ```bash
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   
   # Test authentication with detailed diagnostics
   success = client.authenticate()
   print(f'Authentication Success: {success}')
   
   if success:
       print(f'Token Valid: {client.is_token_valid()}')
       print(f'Token Expires: {client.token_expires} seconds')
       print(f'Automatic Renewal: Available')
   "
   ```

2. **Enhanced Task Status Monitoring**
   ```bash
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   client.authenticate()
   
   # Get recent tasks for monitoring
   devices = client.get_pnp_devices()
   for device in devices:
       status = client.get_device_provisioning_status(device.get('id'))
       
       print(f'Device: {status.get(\"serialNumber\", \"Unknown\")}')
       print(f'State: {status.get(\"state\", \"Unknown\")}')
       print(f'Onboard State: {status.get(\"onbState\", \"Unknown\")}')
       print(f'Last Contact: {status.get(\"lastContact\", \"Never\")}')
       print(f'Provision Details: {len(status.get(\"provisionDetails\", []))} entries')
       print('---')
   "
   ```

3. **Site and Device Assignment Verification**
   ```bash
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   client.authenticate()
   
   # Verify site hierarchy
   sites = client.get_sites()
   print(f'Total Sites: {len(sites)}')
   
   for site in sites:
       site_name = site.get('name', 'Unknown')
       site_type = site.get('type', 'Unknown')
       print(f'Site: {site_name} (Type: {site_type})')
   "
   ```

---

## Post-Lab Activities

### Lab Report Requirements

Complete the following sections in your lab report:

1. **Executive Summary**
   - Brief overview of lab objectives achieved
   - Key technologies implemented
   - Overall success rate

2. **Technical Implementation**
   - Network topology diagram with IP addressing
   - DHCP Option 43 configuration details
   - Device configuration summaries

3. **Testing Results**
   - Connectivity verification results
   - Performance metrics (if applicable)
   - Security validation

4. **Troubleshooting Experience**
   - Issues encountered and resolutions
   - Lessons learned
   - Recommendations for improvement

5. **Appendices**
   - Device configurations
   - Log files
   - Screenshots of key verification steps

### Knowledge Assessment

Answer the following questions:

1. **What is the purpose of DHCP Option 43 in PnP deployments?**

2. **Explain the difference between day-zero and day-one configurations.**

3. **What are the advantages of using Jinja2 templates for device configuration?**

4. **How does the Catalyst Center API facilitate network automation?**

5. **What security considerations should be implemented in PnP deployments?**

### Additional Challenges (Optional)

1. **Custom Template Creation**
   - Create a custom Jinja2 template for a different device type
   - Implement conditional configuration based on device role

2. **API Integration Enhancement**
   - Add error handling to the Python scripts
   - Implement configuration backup functionality

3. **Multi-Site Deployment**
   - Modify topology for multiple branch sites
   - Implement site-specific configurations

---

## Lab Cleanup

### Step 1: Document Current State

1. **Save Configurations**
   ```bash
   mkdir lab_backup
   cp generated_configs/* lab_backup/
   cp topology/pnp-topology.yaml lab_backup/
   ```

2. **Export Device Configurations**
   ```bash
   # SSH to each device and save config
   ssh admin@10.10.10.10 "show running-config" > lab_backup/branch-router-config.txt
   ```

### Step 2: Reset Lab Environment

1. **Reset Devices to Factory Default**
   ```bash
   # On each device console
   write erase
   reload
   ```

2. **Clear Catalyst Center PnP Inventory**
   - GUI: Provision → Plug and Play → Delete claimed devices
   - API: Use deletion scripts if provided

### Step 3: Lab Submission

Submit the following files:
- [ ] Completed lab report (PDF)
- [ ] Configuration files (generated_configs/)
- [ ] Modified topology file
- [ ] Screenshots of successful deployments
- [ ] Troubleshooting logs (if applicable)

---

## Additional Resources

### Documentation Links
- [Cisco Catalyst Center Documentation](https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/series.html)
- [PnP Configuration Guide](https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/dna-center/2-3-5/user_guide/b_cisco_dna_center_ug_2_3_5.html)
- [Jinja2 Template Documentation](https://jinja.palletsprojects.com/)

### Command Reference
- [Cisco IOS-XE Command Reference](https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xe-16/series.html)
- [Python Requests Library](https://docs.python-requests.org/)

### Support Contacts
- **Lab Instructor**: [instructor-email]
- **Technical Support**: [support-email]
- **Lab Resources**: [lab-portal-url]

---

**End of Lab Guide**

*This lab guide is designed for educational purposes. Always follow your institution's lab policies and procedures.*