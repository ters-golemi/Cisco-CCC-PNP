# Quick Start Guide

## Prerequisites
- Python 3.8+
- Access to Cisco Catalyst Center
- DHCP server with Option 43 support

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ters-golemi/Cisco-CCC-PNP.git
   cd Cisco-CCC-PNP
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the setup script:**
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
   # Cisco DHCP Server
   option 43 hex 5A1D;B2;K4;I172.16.1.10;J80
   
   # Replace 172.16.1.10 with your Catalyst Center IP
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