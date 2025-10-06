# Cisco PnP Automation Lab - Instructor Guide

## Lab Overview
**Duration**: 3-4 hours  
**Class Size**: 8-12 students (2 per team recommended)  
**Skill Level**: Intermediate to Advanced

## Pre-Lab Instructor Setup

### Infrastructure Requirements

1. **Ubuntu Administrator Workstations**
   - **Ubuntu Version**: 20.04 LTS or 22.04 LTS
   - **Specifications**: 4GB RAM minimum (8GB recommended), 10GB free storage
   - **Network Access**: Internet connectivity + lab network access
   - **User Setup**: Standard user accounts with sudo privileges
   - **Pre-installed**: SSH client, web browser, terminal access

2. **Catalyst Center VM/Appliance**
   - Minimum: 32GB RAM, 8 vCPU, 500GB storage
   - IP: 172.16.1.10/24 (adjust as needed)
   - Admin credentials: admin/Cisco123!

3. **DHCP Server Configuration**
   - Cisco IOS-XE Router OR Linux with ISC-DHCP
   - IP: 10.10.10.1/24
   - Option 43: `5A1D;B2;K4;I172.16.1.10;J80`
   - Option 43 Hex: `35413144423242334b344937322e31362e312e31304a3830`

### Ubuntu Workstation Preparation Script

Create this script for automated Ubuntu setup across multiple student workstations:

```bash
#!/bin/bash
# ubuntu-lab-prep.sh - Automated Ubuntu setup for Cisco PnP Lab

echo "=== Cisco PnP Lab Ubuntu Preparation ==="

# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y build-essential software-properties-common apt-transport-https \
    ca-certificates curl gnupg lsb-release python3 python3-pip python3-dev \
    python3-venv python3-setuptools python3-wheel net-tools iputils-ping \
    traceroute nmap tcpdump openssh-client wget git nano vim tree

# Install Python packages globally for all users
sudo pip3 install --upgrade pip setuptools wheel

# Create standard project structure
sudo mkdir -p /opt/network-automation
sudo chown $USER:$USER /opt/network-automation

# Set up student environment
cd /home/$USER
mkdir -p network-automation
cd network-automation

# Create virtual environment
python3 -m venv cisco-pnp-env
source cisco-pnp-env/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install requests PyYAML Jinja2 urllib3 certifi colorlog python-dotenv
pip install netmiko napalm paramiko jsonschema ruamel.yaml pytest

echo "✓ Ubuntu setup completed for user: $USER"
echo "Next steps:"
echo "1. Activate virtual environment: source ~/network-automation/cisco-pnp-env/bin/activate"
echo "2. Clone project: git clone https://github.com/ters-golemi/Cisco-CCC-PNP.git"
```

3. **Network Devices** (per team)
   - ISR 8000v (or physical ISR 4000 series)
   - CSR1000v (or physical ASR 1000 series)
   - Catalyst 9800-L (or physical WLC)
   - 3x Catalyst 9130AXE (or similar APs)

### Student Account Preparation

Create student accounts with following access:
- Catalyst Center: Read/Write PnP permissions
- Device console access (SSH/Telnet)
- Lab server access for Python environment

## Answer Key

### Lab Exercise Configuration Values

**DHCP Option 43 Calculation:**
- String: `5A1D;B2;K4;I172.16.1.10;J80`
- Hex: `35413144423242334b344937322e31362e312e31304a3830`

**Complete Cisco IOS-XE DHCP Configuration:**
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
```

**Student Analysis Questions (Exercise 3):**
- Management IP: `10.10.10.10` (branch router)
- Guest VLAN: `VLAN 40`
- OSPF Area: `Area 0`

**Device Serial Numbers** (Lab Environment):
```
branch-router-01: FCH2147A1B2
gateway-router-01: FCH2147A1B3
wireless-controller-01: FCH2147A1B4
access-point-01: FCH2147A1B5
access-point-02: FCH2147A1B6
access-point-03: FCH2147A1B7
```

### Verification Checklist (Completed)

| Device | Management IP | Hostname | OSPF Process | Status |
|--------|---------------|----------|--------------|---------|
| Branch Router | 10.10.10.10 | branch-router-01 | 1 | ✓ |
| Gateway Router | 10.10.10.11 | gateway-router-01 | 1 | ✓ |
| Wireless Controller | 10.10.10.12 | wireless-controller-01 | N/A | ✓ |
| Access Point 1 | 10.10.70.21 | access-point-01 | N/A | ✓ |
| Access Point 2 | 10.10.70.22 | access-point-02 | N/A | ✓ |
| Access Point 3 | 10.10.70.23 | access-point-03 | N/A | ✓ |

## Common Student Issues and Solutions

### Issue 1: Python Environment Problems
**Symptoms**: Import errors, package not found
**Solution**: 
```bash
# Verify Python version
python3 --version  # Must be 3.8+

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Issue 2: Authentication Failures
**Symptoms**: "Authentication failed" messages
**Common Causes**:
- Incorrect Catalyst Center IP
- Wrong username/password
- SSL certificate issues

**Solution**:
```python
# Test with verbose output
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Issue 3: DHCP Option 43 Issues
**Symptoms**: Devices not discovering PnP server
**Debugging**:
```bash
# On device console
debug dhcp detail
show dhcp lease
show ip dhcp binding
```

**Common Mistakes**:
- Incorrect hex encoding
- Missing semicolons in option string
- Wrong Catalyst Center IP/port

### Issue 4: Template Rendering Errors
**Symptoms**: Jinja2 template errors
**Common Issues**:
- Undefined variables
- Syntax errors in templates
- Missing template files

**Solution**:
```bash
# Validate templates individually
python -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('8000v-branch-router.j2')
print('Template loaded successfully')
"
```

## Grading Rubric

### Technical Implementation (70 points)

| Component | Excellent (A) | Good (B) | Satisfactory (C) | Needs Work (D/F) |
|-----------|---------------|----------|------------------|------------------|
| **Environment Setup** (10pts) | All dependencies installed, no issues | Minor installation issues resolved | Some setup problems | Major setup failures |
| **DHCP Configuration** (15pts) | Option 43 correctly configured and working | Option 43 configured with minor issues | DHCP working, Option 43 needs fixes | DHCP not working |
| **Template Customization** (15pts) | Templates modified correctly for environment | Minor template modifications | Basic template usage | Templates not working |
| **Device Deployment** (20pts) | All devices deployed successfully | Most devices deployed | Some devices deployed | Few/no devices deployed |
| **Verification Testing** (10pts) | All tests pass, comprehensive validation | Most tests pass | Basic testing completed | Minimal testing |

### Lab Report Quality (20 points)

| Component | Excellent (A) | Good (B) | Satisfactory (C) | Needs Work (D/F) |
|-----------|---------------|----------|------------------|------------------|
| **Technical Accuracy** | All technical details correct | Minor technical errors | Some technical inaccuracies | Major technical errors |
| **Documentation** | Comprehensive, well-organized | Good documentation | Adequate documentation | Poor documentation |
| **Troubleshooting** | Excellent problem-solving documentation | Good troubleshooting | Basic troubleshooting | Minimal troubleshooting |

### Knowledge Assessment (10 points)

**Answer Key:**

1. **DHCP Option 43 Purpose**: Provides PnP server discovery information to devices, including IP address and port of Catalyst Center.

2. **Day-zero vs Day-one**: Day-zero is initial bootstrap configuration for basic connectivity. Day-one adds operational configuration like routing protocols, security policies, etc.

3. **Jinja2 Template Advantages**: Reusable configurations, variable substitution, conditional logic, loops for repetitive configuration, version control friendly.

4. **Catalyst Center API Benefits**: Programmatic access, automation capabilities, standardized REST interface, bulk operations, integration with external systems.

5. **PnP Security Considerations**: Secure DHCP (DHCP snooping), encrypted communications (HTTPS), device authentication, network segmentation, access control lists.

## Lab Variations and Extensions

### Beginner Variation (2 hours)
- Pre-configured DHCP server
- Simplified topology (2-3 devices)
- Basic template customization only
- Guided troubleshooting

### Advanced Extension (5-6 hours)
- Multi-site deployment
- Custom Python script development
- Advanced Jinja2 template features
- Integration with external systems (IPAM, monitoring)

### Assessment Variations
- **Practical Exam**: Deploy devices with modified requirements
- **Group Project**: Design and implement custom PnP solution
- **Research Assignment**: Compare PnP with other automation tools

## Lab Environment Reset Procedures

### Automated Reset Script
```bash
#!/bin/bash
# reset_lab.sh

# Reset Catalyst Center PnP inventory
python3 scripts/reset_catalyst_center.py

# Factory reset all devices
ansible-playbook reset_devices.yml

# Clear DHCP leases
sudo dhcp_lease_cleanup.sh

# Reset student directories
for student in team{01..12}; do
    rm -rf /home/$student/Cisco-CCC-PNP/generated_configs/*
    git -C /home/$student/Cisco-CCC-PNP checkout -- topology/pnp-topology.yaml
done

echo "Lab environment reset complete"
```

### Manual Reset Checklist
- [ ] Clear Catalyst Center PnP device inventory
- [ ] Factory reset all network devices
- [ ] Clear DHCP server leases
- [ ] Reset student project directories
- [ ] Verify network connectivity
- [ ] Test DHCP Option 43 functionality

## Troubleshooting Support

### Common Student Help Requests

1. **"My device isn't being discovered"**
   - Check physical connections
   - Verify DHCP lease acquisition
   - Test Option 43 configuration
   - Check Catalyst Center PnP service status

2. **"The Python script isn't working"**
   - Verify Python environment
   - Check Catalyst Center connectivity
   - Review authentication credentials
   - Look for API rate limiting

3. **"My configuration template has errors"**
   - Validate Jinja2 syntax
   - Check variable definitions
   - Test template rendering offline
   - Review device compatibility

### Emergency Procedures

**Lab Network Issues:**
1. Check switch/router configurations
2. Verify VLAN assignments
3. Test inter-VLAN routing
4. Check DHCP server status

**Catalyst Center Issues:**
1. Restart DNA Center services
2. Check system resources (CPU, memory, disk)
3. Verify license status
4. Review system logs

**Mass Device Reset:**
```bash
# Emergency device reset (use with caution)
ansible all -i inventory -m raw -a "write erase; reload in 1"
```

## Additional Resources for Instructors

### Setup Scripts
- `setup_lab_environment.sh` - Automated lab setup
- `create_student_accounts.py` - Student account management
- `validate_lab_setup.py` - Environment validation

### Monitoring Tools
- `lab_monitor.py` - Real-time student progress monitoring
- `device_status_dashboard.html` - Web-based device status
- `generate_lab_report.py` - Automated progress reports

### Reference Configurations
- `reference_configs/` - Known working device configurations
- `topology_variations/` - Alternative lab topologies
- `troubleshooting_configs/` - Broken configs for practice

---

**Instructor Notes**: This guide assumes familiarity with Cisco networking technologies and Python programming. Adjust complexity based on student skill level and available lab time.