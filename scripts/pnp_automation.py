#!/usr/bin/env python3
"""
Cisco Network Plug and Play Automation Script
Integrates with Cisco Catalyst Center (formerly DNA Center) for automated device provisioning
"""

import requests
import json
import yaml
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth
import argparse
import os

# Disable SSL warnings for lab environments
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class CatalystCenterPnP:
    """
    Cisco Catalyst Center PnP API Integration Class
    Handles device provisioning, template management, and network automation
    """
    
    def __init__(self, host: str, username: str, password: str, verify_ssl: bool = False):
        """
        Initialize Catalyst Center connection
        
        Args:
            host: Catalyst Center IP or FQDN
            username: Authentication username
            password: Authentication password  
            verify_ssl: SSL verification (default: False for lab)
        """
        self.host = host
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.base_url = f"https://{host}"
        self.token = None
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pnp_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def authenticate(self) -> bool:
        """
        Authenticate with Catalyst Center and get token
        
        Returns:
            bool: True if successful, False otherwise
        """
        auth_url = f"{self.base_url}/dna/system/api/v1/auth/token"
        
        try:
            response = requests.post(
                auth_url,
                auth=HTTPBasicAuth(self.username, self.password),
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                self.token = response.json()['Token']
                self.headers['X-Auth-Token'] = self.token
                self.logger.info("Successfully authenticated with Catalyst Center")
                return True
            else:
                self.logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return False

    def load_topology(self, topology_file: str) -> Dict[str, Any]:
        """
        Load network topology from YAML file
        
        Args:
            topology_file: Path to topology YAML file
            
        Returns:
            Dict containing topology configuration
        """
        try:
            with open(topology_file, 'r') as file:
                topology = yaml.safe_load(file)
            self.logger.info(f"Loaded topology from {topology_file}")
            return topology
        except Exception as e:
            self.logger.error(f"Failed to load topology: {str(e)}")
            return {}

    def create_configuration_template(self, template_name: str, device_type: str, 
                                    template_content: str, software_type: str = "IOS-XE") -> Optional[str]:
        """
        Create configuration template in Catalyst Center
        
        Args:
            template_name: Name of the template
            device_type: Device type (e.g., "Switches and Hubs")
            template_content: Jinja2 template content
            software_type: Software type (default: IOS-XE)
            
        Returns:
            Template ID if successful, None otherwise
        """
        url = f"{self.base_url}/dna/intent/api/v1/template-programmer/template"
        
        payload = {
            "name": template_name,
            "description": f"Auto-generated template for {device_type}",
            "deviceTypes": [{"productFamily": device_type}],
            "softwareType": software_type,
            "softwareVariant": "XE",
            "templateContent": template_content,
            "version": "1.0",
            "author": "PnP Automation Script"
        }
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                data=json.dumps(payload),
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                template_id = response.json()['response']['templateId']
                self.logger.info(f"Created template '{template_name}' with ID: {template_id}")
                return template_id
            else:
                self.logger.error(f"Template creation failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Template creation error: {str(e)}")
            return None

    def get_pnp_devices(self) -> List[Dict[str, Any]]:
        """
        Get all PnP devices from Catalyst Center
        
        Returns:
            List of PnP devices
        """
        url = f"{self.base_url}/dna/intent/api/v1/onboarding/pnp-device"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                devices = response.json().get('response', [])
                self.logger.info(f"Retrieved {len(devices)} PnP devices")
                return devices
            else:
                self.logger.error(f"Failed to get PnP devices: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting PnP devices: {str(e)}")
            return []

    def claim_pnp_device(self, device_id: str, template_id: str, 
                         config_parameters: Dict[str, Any], site_id: str = None) -> bool:
        """
        Claim and provision a PnP device
        
        Args:
            device_id: PnP device ID
            template_id: Configuration template ID
            config_parameters: Template parameters
            site_id: Site ID for device placement
            
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.base_url}/dna/intent/api/v1/onboarding/pnp-device/site-claim"
        
        payload = {
            "deviceId": device_id,
            "siteId": site_id,
            "type": "Default",
            "configInfo": {
                "configId": template_id,
                "configParameters": config_parameters
            }
        }
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                data=json.dumps(payload),
                verify=self.verify_ssl,
                timeout=60
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully claimed device {device_id}")
                return True
            else:
                self.logger.error(f"Device claim failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Device claim error: {str(e)}")
            return False

    def get_device_provisioning_status(self, device_id: str) -> Dict[str, Any]:
        """
        Get provisioning status of a PnP device
        
        Args:
            device_id: PnP device ID
            
        Returns:
            Dict containing device status information
        """
        url = f"{self.base_url}/dna/intent/api/v1/onboarding/pnp-device/{device_id}"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', {})
            else:
                self.logger.error(f"Failed to get device status: {response.status_code}")
                return {}
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting device status: {str(e)}")
            return {}

    def create_site_hierarchy(self, site_name: str, parent_id: str = None) -> Optional[str]:
        """
        Create site hierarchy in Catalyst Center
        
        Args:
            site_name: Name of the site
            parent_id: Parent site ID (optional)
            
        Returns:
            Site ID if successful, None otherwise
        """
        url = f"{self.base_url}/dna/intent/api/v1/site"
        
        payload = {
            "site": {
                "area": {
                    "name": site_name,
                    "parentName": parent_id or "Global"
                }
            }
        }
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                data=json.dumps(payload),
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 202:
                # Monitor task completion
                execution_id = response.json()['response']['executionId']
                site_id = self.wait_for_task_completion(execution_id)
                if site_id:
                    self.logger.info(f"Created site '{site_name}' with ID: {site_id}")
                return site_id
            else:
                self.logger.error(f"Site creation failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Site creation error: {str(e)}")
            return None

    def wait_for_task_completion(self, execution_id: str, timeout: int = 300) -> Optional[str]:
        """
        Wait for task completion and return result
        
        Args:
            execution_id: Task execution ID
            timeout: Maximum wait time in seconds
            
        Returns:
            Task result if successful, None otherwise
        """
        url = f"{self.base_url}/dna/intent/api/v1/task/{execution_id}"
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    verify=self.verify_ssl,
                    timeout=30
                )
                
                if response.status_code == 200:
                    task_data = response.json().get('response', {})
                    
                    if task_data.get('isError'):
                        self.logger.error(f"Task failed: {task_data.get('failureReason')}")
                        return None
                    elif task_data.get('endTime'):
                        self.logger.info(f"Task completed successfully")
                        return task_data.get('data')
                    else:
                        time.sleep(5)  # Wait 5 seconds before checking again
                else:
                    self.logger.error(f"Task status check failed: {response.status_code}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Task monitoring error: {str(e)}")
                return None
        
        self.logger.error(f"Task timeout after {timeout} seconds")
        return None

    def provision_devices_from_topology(self, topology_file: str, template_dir: str) -> bool:
        """
        Provision all devices defined in topology file
        
        Args:
            topology_file: Path to topology YAML file
            template_dir: Directory containing Jinja2 templates
            
        Returns:
            bool: True if all devices provisioned successfully
        """
        # Load topology
        topology = self.load_topology(topology_file)
        if not topology:
            return False
        
        success_count = 0
        total_devices = len(topology.get('devices', {}))
        
        # Process each device
        for device_name, device_config in topology.get('devices', {}).items():
            self.logger.info(f"Processing device: {device_name}")
            
            # Load appropriate template
            template_file = os.path.join(template_dir, device_config['template'])
            try:
                with open(template_file, 'r') as f:
                    template_content = f.read()
            except FileNotFoundError:
                self.logger.error(f"Template file not found: {template_file}")
                continue
            
            # Create template in Catalyst Center
            template_name = f"{device_name}_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            template_id = self.create_configuration_template(
                template_name,
                device_config.get('device_family', 'Switches and Hubs'),
                template_content,
                device_config.get('software_type', 'IOS-XE')
            )
            
            if template_id:
                # Prepare configuration parameters
                config_params = {
                    'device': device_config,
                    'topology': topology,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Find PnP devices by serial number (if configured)
                pnp_devices = self.get_pnp_devices()
                target_device = None
                
                if 'serial_number' in device_config:
                    for pnp_device in pnp_devices:
                        if pnp_device.get('deviceInfo', {}).get('serialNumber') == device_config['serial_number']:
                            target_device = pnp_device
                            break
                
                if target_device:
                    # Claim and provision device
                    device_id = target_device['id']
                    if self.claim_pnp_device(device_id, template_id, config_params):
                        success_count += 1
                        self.logger.info(f"Successfully provisioned {device_name}")
                    else:
                        self.logger.error(f"Failed to provision {device_name}")
                else:
                    self.logger.warning(f"PnP device not found for {device_name}")
            else:
                self.logger.error(f"Failed to create template for {device_name}")
        
        self.logger.info(f"Provisioning complete: {success_count}/{total_devices} devices successful")
        return success_count == total_devices

def main():
    """
    Main function for command-line usage
    """
    parser = argparse.ArgumentParser(description='Cisco PnP Automation Script')
    parser.add_argument('--host', required=True, help='Catalyst Center IP/FQDN')
    parser.add_argument('--username', required=True, help='Username')
    parser.add_argument('--password', required=True, help='Password')
    parser.add_argument('--topology', required=True, help='Topology YAML file')
    parser.add_argument('--templates', required=True, help='Templates directory')
    parser.add_argument('--verify-ssl', action='store_true', help='Verify SSL certificates')
    
    args = parser.parse_args()
    
    # Initialize PnP client
    pnp_client = CatalystCenterPnP(args.host, args.username, args.password, args.verify_ssl)
    
    # Authenticate
    if not pnp_client.authenticate():
        print("Authentication failed. Exiting.")
        return 1
    
    # Provision devices
    success = pnp_client.provision_devices_from_topology(args.topology, args.templates)
    
    if success:
        print("All devices provisioned successfully!")
        return 0
    else:
        print("Some devices failed to provision. Check logs for details.")
        return 1

if __name__ == "__main__":
    exit(main())