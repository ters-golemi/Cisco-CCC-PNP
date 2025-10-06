# Cisco Network Plug and Play (PnP) Automation Lab
## Student Lab Guide

**Course**: Advanced Network Automation  
**Lab Duration**: 3-4 hours  
**Difficulty Level**: Intermediate to Advanced  
**Prerequisites**: Basic Python, Cisco networking fundamentals, CLI experience

---

## Lab Objectives

By the end of this lab, you will be able to:

1. Configure and deploy Cisco Network Plug and Play (PnP) automation
2. Set up DHCP Option 43 for automatic device discovery
3. Create and customize Jinja2 configuration templates
4. Use Python scripts to interact with Cisco Catalyst Center APIs
5. Provision multiple network devices using zero-touch deployment
6. Troubleshoot common PnP deployment issues

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

## Equipment Requirements

### Virtual Infrastructure
- **Catalyst Center**: Version 2.3.5+ (VM or physical appliance)
- **DHCP Server**: Windows Server, Linux ISC-DHCP, or Cisco router
- **Python Environment**: Python 3.8+ with internet access

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

### Task 1: Environment Verification

1. **Verify Python Installation**
   ```bash
   python3 --version
   # Expected output: Python 3.8.x or higher
   ```

2. **Check Network Connectivity**
   ```bash
   ping 172.16.1.10  # Catalyst Center
   ping 10.10.10.1   # DHCP Server
   ```

3. **Verify Catalyst Center Access**
   - Open browser: `https://172.16.1.10`
   - Login with provided credentials
   - Navigate to System > Settings > External Services > PnP

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

### Step 1: Install Dependencies

1. **Create Virtual Environment (Recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate     # Windows
   ```

2. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Installation**
   ```bash
   python -c "import requests, yaml, jinja2; print('All packages installed successfully')"
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

## Lab Exercise 2: DHCP Option 43 Configuration

### Step 1: Calculate Option 43 Value

1. **Generate Option 43 String**
   ```bash
   python3 -c "
   catalyst_ip = '172.16.1.10'  # Replace with your Catalyst Center IP
   option43 = f'5A1D;B2;K4;I{catalyst_ip};J80'
   hex_value = option43.encode('ascii').hex()
   print(f'Option 43 String: {option43}')
   print(f'Option 43 Hex: {hex_value}')
   "
   ```

2. **Record Your Values:**
   - Option 43 String: `________________`
   - Option 43 Hex: `________________`

### Step 2: Configure DHCP Server

Choose your DHCP server type and follow the appropriate section:

#### Option A: Cisco Router DHCP

1. **Access Router Console**
   ```
   Router> enable
   Router# configure terminal
   ```

2. **Configure DHCP Pool**
   ```
   ip dhcp excluded-address 10.10.10.1 10.10.10.10
   ip dhcp pool PNP_POOL
    network 10.10.10.0 255.255.255.0
    default-router 10.10.10.1
    dns-server 8.8.8.8 8.8.4.4
    option 43 hex [YOUR_HEX_VALUE_HERE]
   exit
   service dhcp
   ```

#### Option B: Windows DHCP Server

1. **Open DHCP Console**
   - Start → Administrative Tools → DHCP

2. **Configure Scope Options**
   - Right-click scope → Scope Options
   - Add Option 43 (Vendor Specific Info)
   - Data type: Binary
   - Value: `[YOUR_HEX_VALUE_HERE]`

#### Option C: Linux ISC-DHCP

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
     option pnp-string "5A1D;B2;K4;I172.16.1.10;J80";
   }
   ```

3. **Restart DHCP Service**
   ```bash
   sudo systemctl restart isc-dhcp-server
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

### Step 2: Verify API Connectivity

1. **Test Authentication**
   ```bash
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   success = client.authenticate()
   print('Authentication: Success' if success else 'Failed')
   "
   ```

2. **Expected Output:**
   ```
   Authentication: Success
   ```

### Step 3: Check Existing PnP Devices

1. **List Current PnP Devices**
   ```bash
   python3 -c "
   from scripts.pnp_automation import CatalystCenterPnP
   client = CatalystCenterPnP('172.16.1.10', 'admin', 'Cisco123!')
   client.authenticate()
   devices = client.get_pnp_devices()
   print(f'Found {len(devices)} PnP devices')
   for device in devices:
       print(f'- {device.get(\"deviceInfo\", {}).get(\"serialNumber\", \"Unknown\")}')
   "
   ```

---

## Lab Exercise 5: Device Deployment

### Step 1: Physical Device Preparation

1. **Power Cycle Devices**
   - Ensure devices have factory default configuration
   - Connect to management network (DHCP-enabled segment)
   - Power on devices one by one

2. **Monitor Console Output**
   ```
   # Expected PnP discovery messages:
   %PNPA-5-DISCOVERY: PnP Discovery started
   %PNPA-5-PNP_DHCP_INSTALLED_SUCCESSFULLY: PnP DHCP client installed successfully
   %PNPA-5-PNP_DISCOVERY_DONE: PnP Discovery done successfully
   ```

### Step 2: Automated Deployment

1. **Run PnP Automation Script**
   ```bash
   python scripts/pnp_automation.py \
     --host 172.16.1.10 \
     --username admin \
     --password Cisco123! \
     --topology topology/pnp-topology.yaml \
     --templates templates
   ```

2. **Monitor Deployment Progress**
   - Watch console output for status messages
   - Check Catalyst Center PnP dashboard
   - Monitor device console for configuration application

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
   | Branch Router | | | | ☐ |
   | Gateway Router | | | | ☐ |
   | Wireless Controller | | | | ☐ |
   | Access Point 1 | | | | ☐ |
   | Access Point 2 | | | | ☐ |
   | Access Point 3 | | | | ☐ |

---

## Lab Exercise 7: Troubleshooting Scenarios

### Scenario 1: Device Not Discovered

**Problem**: Device not appearing in PnP inventory

**Troubleshooting Steps:**

1. **Verify DHCP Configuration**
   ```bash
   # On device console
   show ip dhcp binding
   show ip route
   ```

2. **Check Option 43**
   ```bash
   show dhcp lease
   debug dhcp detail
   ```

3. **Verify Network Connectivity**
   ```bash
   ping 172.16.1.10  # Catalyst Center
   telnet 172.16.1.10 80  # HTTP connectivity
   ```

**Student Exercise:** Document your troubleshooting process:
- Issue observed: `________________`
- Steps taken: `________________`
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