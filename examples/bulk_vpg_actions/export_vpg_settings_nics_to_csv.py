#!/usr/bin/env python3

# Legal Disclaimer
# This script is an example script and is not supported under any Zerto support program or service. 
# The author and Zerto further disclaim all implied warranties including, without limitation, 
# any implied warranties of merchantability or of fitness for a particular purpose.
# In no event shall Zerto, its authors or anyone else involved in the creation, 
# production or delivery of the scripts be liable for any damages whatsoever (including, 
# without limitation, damages for loss of business profits, business interruption, loss of business 
# information, or other pecuniary loss) arising out of the use of or the inability to use the sample 
# scripts or documentation, even if the author or Zerto has been advised of the possibility of such damages. 
# The entire risk arising out of the use or performance of the sample scripts and documentation remains with you.
import argparse
import logging
import json
import csv
import sys
import os
from pathlib import Path
import urllib3
from typing import List, Dict
import codecs

# Add parent directory to path to import zvml
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from zvml import ZVMLClient

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


"""
Zerto VPG NIC Settings Export Script

This script exports Virtual Protection Group (VPG) NIC settings to a CSV file, focusing on network
and IP configuration details. It's designed to help with bulk management of VPG NIC settings.

Key Features:
1. VPG NIC Settings Export:
   - Export NIC settings for specific VPGs or all VPGs
   - Save settings to both JSON and CSV formats
   - Include network and IP configuration details
   - Capture DHCP and static IP settings

2. CSV Format:
   - Organized by VPG, VM, and NIC
   - Includes network identifiers
   - DHCP settings (True/False)
   - Static IP configuration (IP, Subnet, Gateway, DNS)
   - ShouldReplaceIpConfiguration flag

3. Settings Management:
   - Export current VPG settings
   - Convert to CSV format
   - Save with timestamp
   - Support for Windows line endings

Required Arguments:
    --zvm_address: ZVM address
    --client_id: Keycloak client ID
    --client_secret: Keycloak client secret
    --ignore_ssl: Ignore SSL certificate verification (optional)
    --vpg_names: Comma-separated list of VPG names to export (optional)

Example Usage:
    python export_vpg_settings_nics_to_csv.py \
        --zvm_address "192.168.111.20" \
        --client_id "zerto-api" \
        --client_secret "your-secret-here" \
        --vpg_names "VpgTest1,VpgTest2" \
        --ignore_ssl

Output Files:
    - ExportedSettings_[timestamp].json: Full VPG settings in JSON format
    - ExportedSettings_[timestamp].csv: NIC settings in CSV format

Note: This script is part of a pair with import_vpg_settings_nics_from_csv.py, allowing for
export and import of VPG NIC settings in bulk. The CSV format is designed to be easily
editable in spreadsheet applications.
"""

def setup_client(args):
    """Initialize and return Zerto client"""
    client = ZVMLClient(
        zvm_address=args.zvm_address,
        client_id=args.client_id,
        client_secret=args.client_secret,
        verify_certificate=not args.ignore_ssl
    )
    return client

def extract_nic_settings(json_data):
    """Extract NIC settings from VPG JSON data."""
    nic_settings = []
    
    for vpg in json_data:
        vpg_name = vpg['Basic']['Name']
        
        for vm in vpg['Vms']:
            vm_id = vm['VmIdentifier']
            
            for nic in vm['Nics']:
                nic_id = nic['NicIdentifier']
                
                # Extract failover settings
                failover = nic['Failover']['Hypervisor'] if nic['Failover'] and nic['Failover']['Hypervisor'] else {}
                failover_network = failover.get('NetworkIdentifier', '')
                failover_ip_config = failover.get('IpConfig', {}) or {}
                
                # Extract failover test settings
                failover_test = nic['FailoverTest']['Hypervisor'] if nic['FailoverTest'] and nic['FailoverTest']['Hypervisor'] else {}
                failover_test_network = failover_test.get('NetworkIdentifier', '')
                failover_test_ip_config = failover_test.get('IpConfig', {}) or {}
                
                # Create a row for each NIC
                row = {
                    'VPG Name': vpg_name,
                    'VM Identifier': vm_id,
                    'NIC Identifier': nic_id,
                    'Failover Network': failover_network,
                    'Failover ShouldReplaceIpConfiguration': str(failover.get('ShouldReplaceIpConfiguration', False)),
                    'Failover DHCP': str(failover_ip_config.get('IsDhcp', False)),
                    'Failover IP': failover_ip_config.get('StaticIp', ''),
                    'Failover Subnet': failover_ip_config.get('SubnetMask', ''),
                    'Failover Gateway': failover_ip_config.get('Gateway', ''),
                    'Failover DNS1': failover_ip_config.get('PrimaryDns', ''),
                    'Failover DNS2': failover_ip_config.get('SecondaryDns', ''),
                    'Failover Test Network': failover_test_network,
                    'Failover Test ShouldReplaceIpConfiguration': str(failover_test.get('ShouldReplaceIpConfiguration', False)),
                    'Failover Test DHCP': str(failover_test_ip_config.get('IsDhcp', False)),
                    'Failover Test IP': failover_test_ip_config.get('StaticIp', ''),
                    'Failover Test Subnet': failover_test_ip_config.get('SubnetMask', ''),
                    'Failover Test Gateway': failover_test_ip_config.get('Gateway', ''),
                    'Failover Test DNS1': failover_test_ip_config.get('PrimaryDns', ''),
                    'Failover Test DNS2': failover_test_ip_config.get('SecondaryDns', '')
                }
                nic_settings.append(row)
    
    return nic_settings

def get_safe_filename(timestamp):
    """Convert timestamp to a URL-safe filename."""
    # Replace colons with underscores and remove any other problematic characters
    return timestamp.replace(':', '_').replace('/', '_').replace('\\', '_')

def setup_argparse() -> argparse.ArgumentParser:
    """Set up command line argument parsing."""
    parser = argparse.ArgumentParser(description="Export VPG settings to CSV")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument('--client_id', required=True, help='Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    parser.add_argument("--vpg_names", help="Comma-separated list of VPG names to export (optional)")
    parser.add_argument("--output_dir", default='.', help="Directory to save exported files (default: current directory)")
    return parser

def ensure_output_dir(output_dir: str) -> None:
    """Ensure the output directory exists."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")

def main():
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        # Ensure output directory exists
        ensure_output_dir(args.output_dir)

        # Setup client
        client = setup_client(args)

        # Process VPG names if provided
        vpg_names = None
        if args.vpg_names:
            vpg_names = [name.strip() for name in args.vpg_names.split(',')]
            logging.info(f"Exporting settings for VPGs: {vpg_names}")
        else:
            logging.info("No VPG names provided, exporting all VPGs")

        # Export VPG settings
        print("\nExporting VPG settings...")
        export_result = client.vpgs.export_vpg_settings(vpg_names)
        
        if not export_result or 'TimeStamp' not in export_result:
            logging.error("Failed to export VPG settings")
            sys.exit(1)

        timestamp = export_result['TimeStamp']
        safe_timestamp = get_safe_filename(timestamp)
        print(f"Export completed successfully. Timestamp: {timestamp}")

        # Get the exported settings
        export_settings = client.vpgs.read_exported_vpg_settings(timestamp, vpg_names)
        
        # Save the JSON export
        json_file_name = os.path.join(args.output_dir, f"ExportedSettings_{safe_timestamp}.json")
        with open(json_file_name, 'w') as f:
            json.dump(export_settings['ExportedVpgSettingsApi'], f, indent=2)
        print(f"\nJSON export saved to: {json_file_name}")

        # Convert to CSV
        nic_settings = extract_nic_settings(export_settings['ExportedVpgSettingsApi'])
        
        # Create CSV file with Windows line endings
        csv_file_name = os.path.join(args.output_dir, f"ExportedSettings_{safe_timestamp}.csv")
        fieldnames = [
            'VPG Name', 'VM Identifier', 'NIC Identifier',
            'Failover Network', 'Failover ShouldReplaceIpConfiguration', 'Failover DHCP',
            'Failover IP', 'Failover Subnet', 'Failover Gateway',
            'Failover DNS1', 'Failover DNS2',
            'Failover Test Network', 'Failover Test ShouldReplaceIpConfiguration', 'Failover Test DHCP',
            'Failover Test IP', 'Failover Test Subnet',
            'Failover Test Gateway', 'Failover Test DNS1', 'Failover Test DNS2'
        ]
        
        # Write CSV content directly
        with open(csv_file_name, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
                delimiter=',',
                quoting=csv.QUOTE_ALL,
                quotechar='"',
                lineterminator='\r\n'
            )
            writer.writeheader()
            for row in nic_settings:
                # Ensure all fields are present and properly formatted
                for field in fieldnames:
                    if field not in row:
                        row[field] = ''
                    # No need to convert boolean values since they're already strings
                writer.writerow(row)
        
        print(f"CSV file created: {csv_file_name}")

    except Exception as e:
        logging.exception("Error occurred:")
        sys.exit(1)

if __name__ == "__main__":
    main()