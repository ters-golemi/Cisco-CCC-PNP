# Quick Start Guide

## Prerequisites
- **Ubuntu 20.04+ Administrator Workstation** (Required)
- Python 3.8+ (installed via Ubuntu setup)
- Access to Cisco Catalyst Center
- DHCP server with Option 43 support
- Sudo privileges on Ubuntu system

## Ubuntu Environment Setup

1. **Automated Ubuntu setup (Recommended):**
   ```bash
   # Download and run Ubuntu setup script
   wget https://raw.githubusercontent.com/ters-golemi/Cisco-CCC-PNP/main/ubuntu-setup.sh
   chmod +x ubuntu-setup.sh
   ./ubuntu-setup.sh
   ```

2. **Activate the environment:**
   ```bash
   source ~/network-automation/activate-env.sh
   ```

## Project Configuration

1. **Navigate to project directory:**
   ```bash
   cd ~/network-automation/Cisco-CCC-PNP
   ```

2. **Run the setup script:**
   ```bash
   ./setup.sh
   ```
   Select option 1 for full interactive setup.

## Configuration

1. **Edit the topology file:**
   - Modify `topology/pnp-topology.yaml` 
   - Update IP addresses, device names, and serial numbers

2. **Configure DHCP Option 43:**
   ```
   # Cisco IOS-XE Router DHCP Configuration
   service dhcp
   ip dhcp excluded-address 10.10.10.1 10.10.10.20
   ip dhcp pool PNP_POOL
    network 10.10.10.0 255.255.255.0
    default-router 10.10.10.1
    dns-server 8.8.8.8 8.8.4.4
    option 43 hex 35413144423242334b344937322e31362e312e31304a3830
   exit
   
   # Replace the hex value with your calculated Option 43 for your Catalyst Center IP
   ```

3. **Generate configurations:**
   ```bash
   python scripts/config_generator.py \
     --topology topology/pnp-topology.yaml \
     --templates templates \
     --output generated_configs \
     --summary
   ```

4. **Deploy to devices:**
   ```bash
   python scripts/pnp_automation.py \
     --host <catalyst-center-ip> \
     --username <username> \
     --password <password> \
     --topology topology/pnp-topology.yaml \
     --templates templates
   ```

## Support

For detailed documentation, see [README.md](README.md)

For issues and questions, please create a GitHub issue.