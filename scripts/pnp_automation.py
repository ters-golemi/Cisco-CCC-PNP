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
        self.token_expires = None
        self.token_timestamp = None
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
        Compatible with Catalyst Center 3.1.x API requirements
        
        Returns:
            bool: True if successful, False otherwise
        """
        auth_url = f"{self.base_url}/dna/system/api/v1/auth/token"
        
        try:
            # Enhanced authentication headers for 3.1.x compatibility
            auth_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Cisco-PnP-Automation/3.1.0'
            }
            
            response = requests.post(
                auth_url,
                auth=HTTPBasicAuth(self.username, self.password),
                headers=auth_headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get('Token')
                if self.token:
                    self.headers['X-Auth-Token'] = self.token
                    # Store token expiration if available (3.1.x feature)
                    self.token_expires = token_data.get('expires_in', 3600)  # Default 1 hour
                    self.token_timestamp = time.time()
                    self.logger.info("Successfully authenticated with Catalyst Center 3.1.x")
                    return True
                else:
                    self.logger.error("Authentication response missing token")
                    return False
            elif response.status_code == 401:
                self.logger.error("Authentication failed: Invalid credentials")
                return False
            elif response.status_code == 403:
                self.logger.error("Authentication failed: Insufficient privileges")
                return False
            else:
                self.logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.ConnectTimeout:
            self.logger.error(f"Connection timeout to Catalyst Center at {self.host}")
            return False
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Connection error to Catalyst Center at {self.host}")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return False

    def is_token_valid(self) -> bool:
        """
        Check if current token is still valid
        
        Returns:
            bool: True if token is valid, False if expired or missing
        """
        if not self.token or not hasattr(self, 'token_timestamp'):
            return False
        
        # Check token expiration (with 5-minute buffer)
        elapsed_time = time.time() - self.token_timestamp
        return elapsed_time < (self.token_expires - 300)

    def ensure_authentication(self) -> bool:
        """
        Ensure valid authentication, re-authenticate if necessary
        
        Returns:
            bool: True if authentication is valid, False otherwise
        """
        if not self.is_token_valid():
            self.logger.info("Token expired or missing, re-authenticating...")
            return self.authenticate()
        return True

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
                                    template_content: str, software_type: str = "IOS-XE",
                                    project_name: str = "PnP_Automation", 
                                    template_params: List[Dict] = None) -> Optional[str]:
        """
        Create configuration template in Catalyst Center 3.1.x with enhanced features
        
        Args:
            template_name: Name of the template
            device_type: Device type (e.g., "Switches and Hubs", "Routers")
            template_content: Jinja2 template content
            software_type: Software type (default: IOS-XE)
            project_name: Template project name (3.1.x feature)
            template_params: Template parameters for validation
            
        Returns:
            Template ID if successful, None otherwise
        """
        if not self.ensure_authentication():
            self.logger.error("Authentication failed, cannot create template")
            return None
            
        url = f"{self.base_url}/dna/intent/api/v1/template-programmer/template"
        
        # Enhanced payload for 3.1.x compatibility
        payload = {
            "name": template_name,
            "description": f"Auto-generated template for {device_type} - Catalyst Center 3.1.x",
            "deviceTypes": [{"productFamily": device_type}],
            "softwareType": software_type,
            "softwareVariant": "XE",
            "templateContent": template_content,
            "version": "1.0",
            "author": "PnP Automation Script 3.1.x",
            "projectName": project_name,
            "language": "JINJA"
        }
        
        # Add template parameters if provided (3.1.x feature)
        if template_params:
            payload["templateParams"] = template_params
        
        # Add rollback template support (3.1.x feature)
        payload["rollbackTemplateContent"] = ""
        payload["composite"] = False
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                data=json.dumps(payload),
                verify=self.verify_ssl,
                timeout=60  # Increased timeout for template processing
            )
            
            if response.status_code == 200:
                result = response.json().get('response', {})
                template_id = result.get('templateId')
                if template_id:
                    self.logger.info(f"Created template '{template_name}' with ID: {template_id}")
                    
                    # Commit template (3.1.x requirement)
                    if self.commit_template(template_id):
                        return template_id
                    else:
                        self.logger.warning(f"Template created but commit failed for {template_name}")
                        return template_id
                else:
                    self.logger.error("Template creation response missing template ID")
                    return None
            elif response.status_code == 401:
                self.logger.error("Authentication token expired during template creation")
                if self.authenticate():
                    return self.create_configuration_template(template_name, device_type, template_content, 
                                                            software_type, project_name, template_params)
                return None
            else:
                self.logger.error(f"Template creation failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Template creation error: {str(e)}")
            return None

    def commit_template(self, template_id: str) -> bool:
        """
        Commit template changes in Catalyst Center 3.1.x
        
        Args:
            template_id: Template ID to commit
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ensure_authentication():
            return False
            
        url = f"{self.base_url}/dna/intent/api/v1/template-programmer/template/version"
        
        payload = {
            "templateId": template_id,
            "comments": "Auto-commit by PnP Automation Script"
        }
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                data=json.dumps(payload),
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code in [200, 202]:
                self.logger.info(f"Template {template_id} committed successfully")
                return True
            else:
                self.logger.warning(f"Template commit failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Template commit error: {str(e)}")
            return False

    def get_templates(self, project_name: str = None) -> List[Dict[str, Any]]:
        """
        Get configuration templates from Catalyst Center 3.1.x
        
        Args:
            project_name: Filter by project name
            
        Returns:
            List of templates
        """
        if not self.ensure_authentication():
            return []
            
        url = f"{self.base_url}/dna/intent/api/v1/template-programmer/template"
        
        params = {}
        if project_name:
            params['projectName'] = project_name
            
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                templates = response.json().get('response', [])
                self.logger.info(f"Retrieved {len(templates)} templates")
                return templates
            else:
                self.logger.error(f"Failed to get templates: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting templates: {str(e)}")
            return []

    def get_pnp_devices(self, device_state: str = None, serial_number: str = None) -> List[Dict[str, Any]]:
        """
        Get PnP devices from Catalyst Center with enhanced filtering (3.1.x compatible)
        
        Args:
            device_state: Filter by device state (e.g., 'Unclaimed', 'Planned', 'Provisioned')
            serial_number: Filter by specific serial number
            
        Returns:
            List of PnP devices
        """
        # Ensure valid authentication before API call
        if not self.ensure_authentication():
            self.logger.error("Authentication failed, cannot retrieve PnP devices")
            return []
            
        url = f"{self.base_url}/dna/intent/api/v1/onboarding/pnp-device"
        
        # Add query parameters for filtering (3.1.x feature)
        params = {}
        if device_state:
            params['state'] = device_state
        if serial_number:
            params['serialNumber'] = serial_number
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                devices = response.json().get('response', [])
                self.logger.info(f"Retrieved {len(devices)} PnP devices" + 
                               (f" with state '{device_state}'" if device_state else ""))
                return devices
            elif response.status_code == 401:
                self.logger.error("Authentication token expired, attempting re-authentication")
                if self.authenticate():
                    return self.get_pnp_devices(device_state, serial_number)
                return []
            else:
                self.logger.error(f"Failed to get PnP devices: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting PnP devices: {str(e)}")
            return []

    def claim_pnp_device(self, device_id: str, template_id: str = None, 
                         config_parameters: Dict[str, Any] = None, site_id: str = None,
                         workflow_name: str = "Onboarding Configuration Workflow") -> Optional[str]:
        """
        Claim and provision a PnP device using Catalyst Center 3.1.x API
        
        Args:
            device_id: PnP device ID
            template_id: Configuration template ID (optional for basic claim)
            config_parameters: Template parameters
            site_id: Site ID for device placement
            workflow_name: PnP workflow name (3.1.x feature)
            
        Returns:
            Task ID if successful, None otherwise
        """
        # Ensure valid authentication before API call
        if not self.ensure_authentication():
            self.logger.error("Authentication failed, cannot claim device")
            return None
            
        url = f"{self.base_url}/dna/intent/api/v1/onboarding/pnp-device/site-claim"
        
        # Enhanced payload structure for 3.1.x compatibility
        payload = {
            "deviceId": device_id,
            "siteId": site_id or "Global",
            "type": "Default",
            "imageInfo": {"imageId": "", "skip": False},
            "configInfo": {
                "configId": template_id or "",
                "configParameters": config_parameters or []
            },
            "rfProfile": None,
            "staticIP": None,
            "vlanId": None,
            "ipInterfaceName": None
        }
        
        # Add workflow information for 3.1.x
        if workflow_name:
            payload["workflowName"] = workflow_name
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                data=json.dumps(payload),
                verify=self.verify_ssl,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get('response', {}).get('taskId')
                if task_id:
                    self.logger.info(f"Successfully initiated claim for device {device_id}, Task ID: {task_id}")
                    return task_id
                else:
                    self.logger.info(f"Device {device_id} claim initiated (no task ID returned)")
                    return "SUCCESS"
            elif response.status_code == 401:
                self.logger.error("Authentication token expired during device claim")
                if self.authenticate():
                    return self.claim_pnp_device(device_id, template_id, config_parameters, site_id, workflow_name)
                return None
            else:
                self.logger.error(f"Device claim failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Device claim error: {str(e)}")
            return None

    def get_device_provisioning_status(self, device_id: str) -> Dict[str, Any]:
        """
        Get provisioning status of a PnP device with enhanced details (3.1.x compatible)
        
        Args:
            device_id: PnP device ID
            
        Returns:
            Dict containing device status information
        """
        # Ensure valid authentication before API call
        if not self.ensure_authentication():
            self.logger.error("Authentication failed, cannot get device status")
            return {}
            
        url = f"{self.base_url}/dna/intent/api/v1/onboarding/pnp-device/{device_id}"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                device_data = response.json().get('response', {})
                
                # Extract enhanced status information for 3.1.x
                status_info = {
                    'deviceId': device_data.get('id'),
                    'serialNumber': device_data.get('deviceInfo', {}).get('serialNumber'),
                    'state': device_data.get('deviceInfo', {}).get('state'),
                    'onbState': device_data.get('deviceInfo', {}).get('onbState'),
                    'lastContact': device_data.get('deviceInfo', {}).get('lastContact'),
                    'provisionDetails': device_data.get('runSummaryList', []),
                    'workflowParameters': device_data.get('workflowParameters', {}),
                    'dayZeroConfig': device_data.get('dayZeroConfig', {}),
                    'dayZeroConfigPreview': device_data.get('dayZeroConfigPreview')
                }
                
                return status_info
            elif response.status_code == 401:
                self.logger.error("Authentication token expired during status check")
                if self.authenticate():
                    return self.get_device_provisioning_status(device_id)
                return {}
            else:
                self.logger.error(f"Failed to get device status: {response.status_code} - {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting device status: {str(e)}")
            return {}

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get task execution status (3.1.x Task API)
        
        Args:
            task_id: Task ID from previous API call
            
        Returns:
            Dict containing task status information
        """
        if not self.ensure_authentication():
            return {}
            
        url = f"{self.base_url}/dna/intent/api/v1/task/{task_id}"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                task_data = response.json().get('response', {})
                
                # Enhanced task status for 3.1.x
                return {
                    'taskId': task_data.get('id'),
                    'status': task_data.get('isError', False),
                    'progress': task_data.get('progress', ''),
                    'errorCode': task_data.get('errorCode'),
                    'failure_reason': task_data.get('failureReason'),
                    'startTime': task_data.get('startTime'),
                    'endTime': task_data.get('endTime'),
                    'data': task_data.get('data')
                }
            else:
                self.logger.error(f"Failed to get task status: {response.status_code}")
                return {}
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting task status: {str(e)}")
            return {}

    def wait_for_task_completion(self, task_id: str, max_wait_time: int = 300) -> Optional[str]:
        """
        Wait for task completion with enhanced monitoring (3.1.x compatible)
        
        Args:
            task_id: Task ID to monitor
            max_wait_time: Maximum wait time in seconds
            
        Returns:
            Task result data if successful, None otherwise
        """
        if not task_id:
            return None
            
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait_time:
            task_status = self.get_task_status(task_id)
            
            if not task_status:
                self.logger.error(f"Failed to get status for task {task_id}")
                return None
            
            if task_status.get('endTime'):
                if task_status.get('status') is False:  # Success
                    self.logger.info(f"Task {task_id} completed successfully")
                    return task_status.get('data')
                else:
                    self.logger.error(f"Task {task_id} failed: {task_status.get('failure_reason')}")
                    return None
            
            # Log progress if available
            progress = task_status.get('progress', '')
            if progress:
                self.logger.info(f"Task {task_id} progress: {progress}")
            
            time.sleep(10)  # Wait 10 seconds before next check
        
        self.logger.warning(f"Task {task_id} timeout after {max_wait_time} seconds")
        return None

    def create_site_hierarchy(self, site_name: str, site_type: str = "area", 
                              parent_name: str = "Global", address: str = None,
                              country: str = "United States", latitude: float = None, 
                              longitude: float = None) -> Optional[str]:
        """
        Create enhanced site hierarchy in Catalyst Center 3.1.x
        
        Args:
            site_name: Name of the site
            site_type: Type of site ('area', 'building', 'floor')
            parent_name: Parent site name (default: Global)
            address: Physical address of the site
            country: Country name
            latitude: Geographic latitude
            longitude: Geographic longitude
            
        Returns:
            Site ID if successful, None otherwise
        """
        if not self.ensure_authentication():
            self.logger.error("Authentication failed, cannot create site")
            return None
            
        url = f"{self.base_url}/dna/intent/api/v1/site"
        
        # Enhanced site payload for 3.1.x
        site_data = {
            "name": site_name,
            "parentName": parent_name
        }
        
        # Add optional geographic and address information
        if address:
            site_data["address"] = address
        if country:
            site_data["country"] = country
        if latitude is not None and longitude is not None:
            site_data["latitude"] = latitude
            site_data["longitude"] = longitude
            
        payload = {"site": {site_type: site_data}}
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                data=json.dumps(payload),
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 202:
                result = response.json().get('response', {})
                execution_id = result.get('executionId')
                if execution_id:
                    # Monitor task completion using enhanced method
                    task_result = self.wait_for_task_completion(execution_id)
                    if task_result:
                        self.logger.info(f"Created {site_type} site '{site_name}' successfully")
                        return execution_id  # Return execution ID as site reference
                    else:
                        self.logger.error(f"Site creation task failed for '{site_name}'")
                        return None
                else:
                    self.logger.warning(f"Site creation initiated for '{site_name}' but no execution ID returned")
                    return "INITIATED"
            elif response.status_code == 401:
                self.logger.error("Authentication token expired during site creation")
                if self.authenticate():
                    return self.create_site_hierarchy(site_name, site_type, parent_name, address, country, latitude, longitude)
                return None
            else:
                self.logger.error(f"Site creation failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Site creation error: {str(e)}")
            return None

    def get_sites(self, site_name: str = None, site_type: str = None) -> List[Dict[str, Any]]:
        """
        Get sites from Catalyst Center with filtering (3.1.x compatible)
        
        Args:
            site_name: Filter by specific site name
            site_type: Filter by site type
            
        Returns:
            List of sites matching criteria
        """
        if not self.ensure_authentication():
            return []
            
        url = f"{self.base_url}/dna/intent/api/v1/site"
        
        params = {}
        if site_name:
            params['name'] = site_name
        if site_type:
            params['type'] = site_type
            
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                sites = response.json().get('response', [])
                self.logger.info(f"Retrieved {len(sites)} sites")
                return sites
            else:
                self.logger.error(f"Failed to get sites: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting sites: {str(e)}")
            return []

    def assign_device_to_site(self, device_id: str, site_id: str) -> bool:
        """
        Assign device to site in Catalyst Center 3.1.x
        
        Args:
            device_id: Device UUID
            site_id: Site UUID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ensure_authentication():
            return False
            
        url = f"{self.base_url}/dna/intent/api/v1/site-assignment"
        
        payload = {
            "deviceId": device_id,
            "siteId": site_id
        }
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                data=json.dumps(payload),
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code in [200, 202]:
                self.logger.info(f"Device {device_id} assigned to site {site_id}")
                return True
            else:
                self.logger.error(f"Device assignment failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Device assignment error: {str(e)}")
            return False



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