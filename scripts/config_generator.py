#!/usr/bin/env python3
"""
Device Configuration Generator
Generates device configurations from Jinja2 templates and topology data
"""

import yaml
import json
from jinja2 import Environment, FileSystemLoader, Template
import argparse
import os
from datetime import datetime
from typing import Dict, Any
import logging

class ConfigurationGenerator:
    """
    Configuration generator for network devices using Jinja2 templates
    """
    
    def __init__(self, templates_dir: str, output_dir: str = "generated_configs"):
        """
        Initialize configuration generator
        
        Args:
            templates_dir: Directory containing Jinja2 templates
            output_dir: Directory for generated configurations
        """
        self.templates_dir = templates_dir
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Configure Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def load_topology(self, topology_file: str) -> Dict[str, Any]:
        """
        Load topology configuration from YAML file
        
        Args:
            topology_file: Path to topology YAML file
            
        Returns:
            Dictionary containing topology data
        """
        try:
            with open(topology_file, 'r') as file:
                topology = yaml.safe_load(file)
            self.logger.info(f"Loaded topology from {topology_file}")
            return topology
        except Exception as e:
            self.logger.error(f"Failed to load topology: {str(e)}")
            return {}

    def generate_device_config(self, device_name: str, device_config: Dict[str, Any], 
                             topology: Dict[str, Any]) -> str:
        """
        Generate configuration for a single device
        
        Args:
            device_name: Name of the device
            device_config: Device-specific configuration
            topology: Complete topology data
            
        Returns:
            Generated configuration as string
        """
        template_name = device_config.get('template')
        if not template_name:
            self.logger.error(f"No template specified for device {device_name}")
            return ""
        
        try:
            # Load template
            template = self.jinja_env.get_template(template_name)
            
            # Prepare template variables
            template_vars = {
                'device': device_config,
                'topology': topology,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'device_name': device_name
            }
            
            # Render configuration
            config = template.render(**template_vars)
            self.logger.info(f"Generated configuration for {device_name}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to generate config for {device_name}: {str(e)}")
            return ""

    def generate_all_configs(self, topology_file: str) -> Dict[str, str]:
        """
        Generate configurations for all devices in topology
        
        Args:
            topology_file: Path to topology YAML file
            
        Returns:
            Dictionary mapping device names to configurations
        """
        topology = self.load_topology(topology_file)
        if not topology:
            return {}
        
        configs = {}
        devices = topology.get('devices', {})
        
        for device_name, device_config in devices.items():
            self.logger.info(f"Generating configuration for {device_name}")
            
            config = self.generate_device_config(device_name, device_config, topology)
            if config:
                configs[device_name] = config
                
                # Save configuration to file
                output_file = os.path.join(self.output_dir, f"{device_name}.cfg")
                try:
                    with open(output_file, 'w') as f:
                        f.write(config)
                    self.logger.info(f"Saved configuration to {output_file}")
                except Exception as e:
                    self.logger.error(f"Failed to save config file: {str(e)}")
        
        return configs

    def validate_template_syntax(self, template_name: str) -> bool:
        """
        Validate Jinja2 template syntax
        
        Args:
            template_name: Name of template file
            
        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            self.jinja_env.get_template(template_name)
            self.logger.info(f"Template {template_name} syntax is valid")
            return True
        except Exception as e:
            self.logger.error(f"Template {template_name} syntax error: {str(e)}")
            return False

    def generate_dhcp_option43_config(self, catalyst_center_ip: str, 
                                    catalyst_center_port: int = 80) -> str:
        """
        Generate DHCP Option 43 configuration for PnP
        
        Args:
            catalyst_center_ip: Catalyst Center IP address
            catalyst_center_port: Catalyst Center port (default: 80)
            
        Returns:
            DHCP Option 43 hex string
        """
        # Format: 5A1D;B2;K4;I<IP>;J<PORT>
        option43_string = f"5A1D;B2;K4;I{catalyst_center_ip};J{catalyst_center_port}"
        
        # Convert to hex
        option43_hex = option43_string.encode('ascii').hex()
        
        self.logger.info(f"Generated Option 43: {option43_string} -> {option43_hex}")
        return option43_hex

    def create_deployment_summary(self, topology: Dict[str, Any]) -> str:
        """
        Create deployment summary document
        
        Args:
            topology: Topology configuration
            
        Returns:
            Summary as formatted string
        """
        summary = []
        summary.append("=" * 60)
        summary.append("CISCO NETWORK PLUG AND PLAY DEPLOYMENT SUMMARY")
        summary.append("=" * 60)
        summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        # Catalyst Center Information
        cc_info = topology.get('catalyst_center', {})
        summary.append("CATALYST CENTER CONFIGURATION:")
        summary.append(f"  IP Address: {cc_info.get('ip_address')}")
        summary.append(f"  Domain: {cc_info.get('settings', {}).get('domain')}")
        summary.append(f"  DHCP Option 43: {cc_info.get('settings', {}).get('dhcp_option_43')}")
        summary.append("")
        
        # Network Information
        summary.append("NETWORK TOPOLOGY:")
        vlans = topology.get('vlans', [])
        for vlan in vlans:
            summary.append(f"  VLAN {vlan['vlan_id']} ({vlan['name'].upper()}):")
            summary.append(f"    Network: {vlan['network']}")
            summary.append(f"    Gateway: {vlan['gateway']}")
        summary.append("")
        
        # Device Information
        summary.append("DEVICES:")
        devices = topology.get('devices', {})
        for device_name, device_config in devices.items():
            summary.append(f"  {device_name}:")
            summary.append(f"    Type: {device_config.get('type')}")
            summary.append(f"    Role: {device_config.get('role')}")
            summary.append(f"    Management IP: {device_config.get('mgmt_ip')}")
            summary.append(f"    Template: {device_config.get('template')}")
            if 'serial_number' in device_config:
                summary.append(f"    Serial: {device_config.get('serial_number')}")
        summary.append("")
        
        # PnP Information
        summary.append("PnP CONFIGURATION STEPS:")
        summary.append("1. Configure DHCP server with Option 43")
        summary.append("2. Power on devices and wait for PnP discovery")
        summary.append("3. Run automation script to claim and provision devices")
        summary.append("4. Verify device configurations and network connectivity")
        summary.append("")
        
        summary.append("=" * 60)
        
        return "\n".join(summary)

def main():
    """
    Main function for command-line usage
    """
    parser = argparse.ArgumentParser(description='Device Configuration Generator')
    parser.add_argument('--topology', required=True, help='Topology YAML file')
    parser.add_argument('--templates', required=True, help='Templates directory')
    parser.add_argument('--output', default='generated_configs', help='Output directory')
    parser.add_argument('--validate', action='store_true', help='Validate template syntax only')
    parser.add_argument('--summary', action='store_true', help='Generate deployment summary')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = ConfigurationGenerator(args.templates, args.output)
    
    if args.validate:
        # Validate all templates
        template_files = [f for f in os.listdir(args.templates) if f.endswith('.j2')]
        valid_count = 0
        
        for template_file in template_files:
            if generator.validate_template_syntax(template_file):
                valid_count += 1
        
        print(f"Template validation: {valid_count}/{len(template_files)} templates valid")
        return 0 if valid_count == len(template_files) else 1
    
    # Generate configurations
    configs = generator.generate_all_configs(args.topology)
    
    if configs:
        print(f"Generated configurations for {len(configs)} devices")
        print(f"Configurations saved to: {args.output}")
        
        if args.summary:
            # Generate deployment summary
            topology = generator.load_topology(args.topology)
            summary = generator.create_deployment_summary(topology)
            
            summary_file = os.path.join(args.output, "deployment_summary.txt")
            with open(summary_file, 'w') as f:
                f.write(summary)
            
            print(f"Deployment summary saved to: {summary_file}")
        
        return 0
    else:
        print("No configurations generated")
        return 1

if __name__ == "__main__":
    exit(main())