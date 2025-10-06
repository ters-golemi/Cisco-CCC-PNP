# Cisco Network Plug and Play (PnP) Automation Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Deployment Process](#deployment-process)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)
8. [API Reference](#api-reference)

## Overview

This project provides comprehensive automation for Cisco Network Plug and Play (PnP) deployments using Cisco Catalyst Center 3.1.x (formerly DNA Center). The solution follows official Cisco 3.1.x PnP deployment guidelines and includes:

- **Enhanced 3.1.x PnP workflows** with improved task monitoring and site management
- **Advanced DHCP Option 43 generation** supporting HTTPS, NTP, and certificate validation
- **3.1.x-compatible configuration templates** with NETCONF and enhanced security features
- **Geographic site hierarchy management** with latitude/longitude support
- **Comprehensive prerequisites validation** according to 3.1.x documentation
- **Enhanced device provisioning workflows** with real-time status monitoring
- Python automation scripts for 3.1.x Intent APIs with token management
- Day-zero configuration deployment following 3.1.x best practices

### Supported Devices
- Cisco ISR 8000v Routers (Branch/WAN)
- Cisco CSR1000v Gateway Routers
- Cisco Catalyst 9800-L Wireless LAN Controllers
- Cisco Catalyst 9130AXE Access Points

## Prerequisites

### Infrastructure Requirements (3.1.x Specific)
- **Cisco Catalyst Center** (version 3.1.x required, 3.1.0+ recommended)
- **DHCP Server** with enhanced Option 43 support (IPv4/IPv6, FQDN, NTP integration)
- **NTP Server** for certificate validation (3.1.x requirement for secure deployments)
- **Network connectivity** between devices and Catalyst Center with HTTPS support
- **DNS resolution** for device discovery (enhanced FQDN support in 3.1.x)
- **Certificate management** infrastructure for SUDI validation (3.1.x security enhancement)
- **Enhanced API support** for 3.1.x features:
  - Geographic site management with coordinates
  - Real-time task monitoring and progress tracking
  - Advanced device filtering and state management
  - Enhanced template versioning and rollback capabilities

### Software Requirements
- Python 3.8 or higher
- Required Python packages (see requirements.txt)
- Network access to Catalyst Center APIs

### Credentials and Access (3.1.x Enhanced)
- **Catalyst Center administrator credentials** with API access
- **Network device credentials** (CLI and SNMPv2c/SNMPv3 - both read and write required for 3.1.x)
- **Cisco.com credentials** configured in System > Settings (3.1.x requirement)
- **Smart Account credentials** for device synchronization (optional but recommended)
- **Global device credentials** configured for site-level management

## New in Catalyst Center 3.1.x

### Enhanced PnP Features
- **Improved Task Management**: Real-time task monitoring with detailed progress tracking
- **Geographic Site Management**: Create sites with latitude/longitude coordinates for better visualization
- **Enhanced Security**: SUDI certificate validation and trusted certificate bundle support
- **Advanced Filtering**: Filter PnP devices by state, serial number, and other criteria
- **FQDN Support**: Enhanced DHCP Option 43 with full FQDN support
- **Template Versioning**: Better template management with version control and rollback capabilities

### API Enhancements
- **Enhanced Authentication**: Improved token management with expiration tracking
- **Better Error Handling**: More detailed error responses and troubleshooting information
- **Expanded Device Support**: Support for latest Catalyst device families
- **Performance Improvements**: Faster API responses and reduced latency

### Security Improvements
- **HTTPS by Default**: Enhanced security with mandatory HTTPS for production deployments
- **NTP Integration**: Certificate validation requires NTP synchronization
- **Enhanced SNMP**: Support for SNMPv3 with advanced authentication
- **Device Controllability**: Automatic NETCONF enablement for supported devices

## Installation

### Ubuntu Administrator Workstation Required
This project must be deployed from an Ubuntu administrator device (Ubuntu 20.04+ recommended).

### 1. Automated Ubuntu Setup
```bash
# Download and run the Ubuntu setup script
wget https://raw.githubusercontent.com/ters-golemi/Cisco-CCC-PNP/main/ubuntu-setup.sh
chmod +x ubuntu-setup.sh
./ubuntu-setup.sh
```

### 2. Manual Installation (Alternative)
```bash
# Update Ubuntu system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv git curl openssh-client

# Create project environment
mkdir -p ~/network-automation
cd ~/network-automation
python3 -m venv cisco-pnp-env
source cisco-pnp-env/bin/activate

# Clone repository
git clone https://github.com/ters-golemi/Cisco-CCC-PNP.git
cd Cisco-CCC-PNP

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
# Activate environment
source ~/network-automation/cisco-pnp-env/bin/activate
cd ~/network-automation/Cisco-CCC-PNP

# Validate installation
python scripts/config_generator.py --validate --templates templates --topology topology/pnp-topology.yaml
```

## Configuration

### 1. Topology Configuration
Edit `topology/pnp-topology.yaml` to match your network:

```yaml
# Example device configuration
devices:
  branch-router-01:
    type: "ISR8000v"
    role: "branch_router"
    mgmt_ip: "10.10.10.10"
    serial_number: "FCH2147A1B2"  # Device serial number for PnP matching
    template: "8000v-branch-router.j2"
```

### 2. DHCP Option 43 Configuration
Configure your DHCP server with Option 43 for PnP discovery:

**Cisco IOS-XE Router DHCP Server:**
```
service dhcp
ip dhcp excluded-address 10.10.10.1 10.10.10.20
ip dhcp pool PNP_POOL
 network 10.10.10.0 255.255.255.0
 default-router 10.10.10.1
 dns-server 8.8.8.8 8.8.4.4
 domain-name lab.local
 lease 0 12 0
 option 43 hex 35413144423242334b344937322e31362e312e31304a3830
exit

! Verification commands
show ip dhcp pool
show ip dhcp binding
```

**ISC DHCP Server (Linux):**
```
subnet 10.10.10.0 netmask 255.255.255.0 {
    range 10.10.10.100 10.10.10.200;
    option routers 10.10.10.1;
    option domain-name-servers 8.8.8.8, 8.8.4.4;
    option pnp-string "5A1D;B2;K4;I172.16.1.10;J80";
}
```

**Windows DHCP Server:**
1. Open DHCP Console
2. Navigate to Scope Options
3. Add Option 43 (Vendor Specific Info)
4. Enter hex string: `5A1D;B2;K4;I172.16.1.10;J80`

### 3. Catalyst Center Configuration
Ensure Catalyst Center is properly configured:

- **PnP Settings**: Enable PnP service
- **Network Discovery**: Configure discovery protocols
- **Templates**: Import or create device templates
- **Sites**: Define site hierarchy

## 3.1.x Enhanced Deployment Process

### Phase 1: Prerequisites Validation (3.1.x)

#### 1. Validate PnP Prerequisites
```bash
python3 -c "
from scripts.pnp_automation import CatalystCenterPnP
client = CatalystCenterPnP('172.16.1.10', 'admin', 'password')
results = client.validate_pnp_prerequisites()
for check, passed in results.items():
    print(f'{check}: {\"PASS\" if passed else \"FAIL\"}')
"
```

#### 2. Generate Enhanced DHCP Option 43 Strings
```bash
python3 -c "
from scripts.pnp_automation import CatalystCenterPnP
client = CatalystCenterPnP('172.16.1.10', 'admin', 'password')

# Generate HTTPS Option 43 with NTP (recommended for 3.1.x)
option43 = client.generate_dhcp_option43_string(
    catalyst_center_ip='172.16.1.10',
    port=443,
    protocol='HTTPS',
    ntp_server='172.16.1.1'
)
print(f'Enhanced 3.1.x Option 43: {option43}')
"
```

### Phase 2: Site Preparation (3.1.x Geographic Features)

#### 1. Create Geographic Site Hierarchy
```bash
python3 -c "
from scripts.pnp_automation import CatalystCenterPnP
client = CatalystCenterPnP('172.16.1.10', 'admin', 'password')
client.authenticate()

# Create area with geographic coordinates
area_id = client.create_site_hierarchy(
    site_name='Lab_Campus',
    site_type='area',
    address='123 Technology Drive, San Jose, CA',
    latitude=37.4419,
    longitude=-121.9438
)
print(f'Created area site: {area_id}')
"
```

### Phase 3: Device Provisioning (3.1.x Enhanced)

#### 1. Generate Device Configurations
```bash
python scripts/config_generator.py \
  --topology topology/pnp-topology.yaml \
  --templates templates \
  --output generated_configs \
  --3.1.x-mode \
  --summary
```

#### 2. Monitor Device States with 3.1.x Filtering
```bash
python3 -c "
from scripts.pnp_automation import CatalystCenterPnP
client = CatalystCenterPnP('172.16.1.10', 'admin', 'password')
client.authenticate()

# Get devices by state using enhanced 3.1.x filtering
for state in ['Unclaimed', 'Planned', 'Onboarding', 'Provisioned']:
    devices = client.get_pnp_devices(device_state=state)
    print(f'{state}: {len(devices)} devices')
"
```

#### 3. Validate Templates
```bash
python scripts/config_generator.py \
  --validate \
  --templates templates \
  --topology topology/pnp-topology.yaml
```

#### 3. Review Generated Configurations
Check the `generated_configs/` directory for device-specific configurations and review the deployment summary.

### Phase 2: Infrastructure Setup

#### 1. Configure DHCP Server
- Deploy DHCP Option 43 configuration
- Verify DHCP pool settings
- Test DHCP lease assignment

#### 2. Network Connectivity
- Ensure Layer 2 connectivity between devices and DHCP server
- Verify routing to Catalyst Center
- Test DNS resolution

#### 3. Catalyst Center Preparation
- Verify PnP service status
- Create site hierarchy
- Import device templates (if needed)

### Phase 3: Device Provisioning

#### 1. Physical Device Setup
- Connect devices to network
- Power on devices
- Verify console access (optional)

#### 2. Monitor PnP Discovery
```bash
# Check for discovered devices
python scripts/pnp_automation.py \
  --host 172.16.1.10 \
  --username admin \
  --password admin123 \
  --topology topology/pnp-topology.yaml \
  --templates templates
```

#### 3. Automated Provisioning
The script will:
- Authenticate with Catalyst Center
- Create configuration templates
- Claim PnP devices
- Apply configurations
- Monitor provisioning status

### Phase 4: Verification

#### 1. Device Status Verification
- Check device connectivity
- Verify configuration deployment
- Test network services

#### 2. Network Testing
- Ping tests between devices
- VLAN connectivity verification
- Wireless client connectivity (if applicable)

## Troubleshooting

### Common Issues and Solutions

#### 1. PnP Discovery Issues

**Problem**: Devices not appearing in PnP inventory
- **Check DHCP**: Verify Option 43 configuration
- **Network connectivity**: Ensure Layer 2/3 path to Catalyst Center
- **Firewall**: Verify ports 80/443 are open
- **DNS**: Check DNS resolution for device discovery

**Diagnostic Commands**:
```bash
# On device console (if accessible)
show pnp profile
show pnp discovery
show ip dhcp binding
show ip route
```

#### 2. Template Application Failures

**Problem**: Configuration templates not applying
- **Template syntax**: Validate Jinja2 template syntax
- **Variable substitution**: Check variable names and values
- **Device compatibility**: Verify template matches device type
- **Permissions**: Ensure sufficient privileges

**Debug Steps**:
```bash
# Validate template syntax
python scripts/config_generator.py --validate --templates templates --topology topology/pnp-topology.yaml

# Generate test configuration
python scripts/config_generator.py --topology topology/pnp-topology.yaml --templates templates --output test_configs
```

#### 3. API Authentication Issues

**Problem**: Authentication failures with Catalyst Center
- **Credentials**: Verify username/password
- **User permissions**: Check user has admin rights
- **SSL/TLS**: Verify certificate trust (use --verify-ssl for production)
- **Network access**: Test connectivity to Catalyst Center

**Test Authentication**:
```python
from scripts.pnp_automation import CatalystCenterPnP

client = CatalystCenterPnP("172.16.1.10", "admin", "admin123")
success = client.authenticate()
print(f"Authentication: {'Success' if success else 'Failed'}")
```

#### 4. Device Configuration Issues

**Problem**: Devices not accepting configuration
- **Syntax errors**: Check configuration syntax
- **Feature licensing**: Verify required licenses
- **Hardware compatibility**: Check feature support
- **Sequence**: Review configuration order

**Validation Steps**:
1. Test configuration on similar device
2. Check device logs for error messages
3. Validate feature availability
4. Review configuration dependencies

### Logging and Diagnostics

#### 1. Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. Catalyst Center Logs
- Navigate to System > Health > Audit Logs
- Filter for PnP-related events
- Check template deployment status

#### 3. Device Console Logs
```bash
# Monitor device logs
show logging
show pnp tech-support
show version
show running-config
```

#### 4. Network Packet Capture
- Capture DHCP Option 43 exchanges
- Monitor HTTP/HTTPS to Catalyst Center
- Verify DNS queries and responses

### Advanced Troubleshooting

#### 1. Manual PnP Reset
```bash
# On device console
pnp profile reset
reload
```

#### 2. Custom DHCP Option 43
```bash
# Calculate Option 43 hex string
python -c "
option43 = '5A1D;B2;K4;I172.16.1.10;J80'
hex_value = option43.encode('ascii').hex()
print(f'Option 43 Hex: {hex_value}')
"
```

#### 3. API Debugging
```bash
# Enable API request logging
export PYTHONHTTPSVERIFY=0
export REQUESTS_CA_BUNDLE=""
python -c "import requests; requests.get('https://172.16.1.10', verify=False)"
```

## Advanced Configuration

### 1. Custom Templates

Create custom Jinja2 templates for specific devices:

```jinja2
{# Custom device template #}
hostname {{ device.name }}
!
{% for interface in device.interfaces %}
interface {{ interface.name }}
 description {{ interface.description }}
 ip address {{ interface.ip }}
{% endfor %}
!
end
```

### 2. Multi-Site Deployment

Configure multiple sites in topology:

```yaml
sites:
  headquarters:
    devices: ["router-hq-01", "switch-hq-01"]
    catalyst_center: "172.16.1.10"
  
  branch_office:
    devices: ["router-branch-01"]  
    catalyst_center: "172.16.2.10"
```

### 3. Template Inheritance

Use template inheritance for common configurations:

```jinja2
{# base_device.j2 #}
hostname {{ device.name }}
service timestamps debug datetime msec
no ip http server
ip http secure-server
{% block device_specific %}{% endblock %}

{# router.j2 #}
{% extends "base_device.j2" %}
{% block device_specific %}
ip routing
router ospf 1
{% endblock %}
```

### 4. Configuration Validation

Add pre-deployment validation:

```python
def validate_config(config_text):
    """Validate configuration syntax"""
    # Add custom validation logic
    forbidden_commands = ['no service password-encryption']
    
    for line in config_text.split('\n'):
        if any(cmd in line for cmd in forbidden_commands):
            return False, f"Forbidden command: {line.strip()}"
    
    return True, "Configuration valid"
```

## API Reference

### CatalystCenterPnP Class Methods

#### Authentication
```python
authenticate() -> bool
```
Authenticate with Catalyst Center and obtain API token.

#### Device Management
```python
get_pnp_devices() -> List[Dict[str, Any]]
claim_pnp_device(device_id: str, template_id: str, config_parameters: Dict[str, Any]) -> bool
get_device_provisioning_status(device_id: str) -> Dict[str, Any]
```

#### Template Management
```python
create_configuration_template(template_name: str, device_type: str, template_content: str) -> Optional[str]
```

#### Site Management
```python
create_site_hierarchy(site_name: str, parent_id: str = None) -> Optional[str]
```

#### Bulk Operations
```python
provision_devices_from_topology(topology_file: str, template_dir: str) -> bool
```

### Configuration Generator Methods

#### Template Processing
```python
generate_device_config(device_name: str, device_config: Dict[str, Any], topology: Dict[str, Any]) -> str
generate_all_configs(topology_file: str) -> Dict[str, str]
validate_template_syntax(template_name: str) -> bool
```

#### Utility Functions
```python
generate_dhcp_option43_config(catalyst_center_ip: str, catalyst_center_port: int = 80) -> str
create_deployment_summary(topology: Dict[str, Any]) -> str
```

---

**Note**: This documentation assumes familiarity with Cisco networking concepts and basic Python programming. For additional support, refer to Cisco Catalyst Center documentation or contact your network administrator.