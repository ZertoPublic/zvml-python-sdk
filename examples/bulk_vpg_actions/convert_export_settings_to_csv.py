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
import json
import csv
import sys
from pathlib import Path


"""
Zerto VPG Settings JSON to CSV Converter

This script converts Zerto VPG settings from JSON format to CSV format, making it easier to
view and edit the settings in spreadsheet applications. It's designed to work with the JSON
output from export_vpg_settings_nics_to_csv.py.

Key Features:
1. JSON to CSV Conversion:
   - Convert VPG settings from JSON to CSV format
   - Preserve all NIC and network settings
   - Maintain data structure and relationships
   - Support for both DHCP and static IP configurations

2. Data Formatting:
   - Format boolean values as "True"/"False"
   - Preserve network identifiers
   - Handle null/empty values appropriately
   - Maintain consistent field ordering

3. Output Generation:
   - Generate timestamped CSV files
   - Include all relevant VPG settings
   - Preserve data integrity
   - Easy to read and edit format

Required Arguments:
    --json_file: Path to the JSON file containing VPG settings

Example Usage:
    python convert_export_settings_to_csv.py \
        --json_file "ExportedSettings_2024-05-12.json"

Output:
    - Generates a CSV file with the same base name as the input JSON
    - Includes all VPG settings in a tabular format
    - Preserves all network and IP configurations
    - Maintains compatibility with import_vpg_settings_nics_from_csv.py

Note: This script is part of a suite of tools for managing Zerto VPG settings. It's designed
to work seamlessly with both the export and import scripts, providing a convenient way to
view and edit VPG settings in spreadsheet applications.
"""

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
                    'Failover IP': failover_ip_config.get('StaticIp', ''),
                    'Failover Subnet': failover_ip_config.get('SubnetMask', ''),
                    'Failover Gateway': failover_ip_config.get('Gateway', ''),
                    'Failover DNS1': failover_ip_config.get('PrimaryDns', ''),
                    'Failover DNS2': failover_ip_config.get('SecondaryDns', ''),
                    'Failover DHCP': 'Yes' if failover_ip_config.get('IsDhcp', False) else 'No',
                    'Failover IsDhcp': failover_ip_config.get('IsDhcp', False),
                    'Failover Test Network': failover_test_network,
                    'Failover Test IP': failover_test_ip_config.get('StaticIp', ''),
                    'Failover Test Subnet': failover_test_ip_config.get('SubnetMask', ''),
                    'Failover Test Gateway': failover_test_ip_config.get('Gateway', ''),
                    'Failover Test DNS1': failover_test_ip_config.get('PrimaryDns', ''),
                    'Failover Test DNS2': failover_test_ip_config.get('SecondaryDns', ''),
                    'Failover Test DHCP': 'Yes' if failover_test_ip_config.get('IsDhcp', False) else 'No',
                    'Failover Test IsDhcp': failover_test_ip_config.get('IsDhcp', False)
                }
                nic_settings.append(row)
    
    return nic_settings

def main():
    if len(sys.argv) != 2:
        print("Usage: python vpg_nic_settings_to_csv.py <json_file>")
        sys.exit(1)
    
    json_file = Path(sys.argv[1])
    if not json_file.exists():
        print(f"Error: File {json_file} does not exist")
        sys.exit(1)
    
    # Read JSON file
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    
    # Extract NIC settings
    nic_settings = extract_nic_settings(json_data)
    
    # Create CSV file
    csv_file = json_file.with_suffix('.csv')
    fieldnames = [
        'VPG Name', 'VM Identifier', 'NIC Identifier',
        'Failover Network', 'Failover IP', 'Failover Subnet', 'Failover Gateway',
        'Failover DNS1', 'Failover DNS2', 'Failover DHCP', 'Failover IsDhcp',
        'Failover Test Network', 'Failover Test IP', 'Failover Test Subnet',
        'Failover Test Gateway', 'Failover Test DNS1', 'Failover Test DNS2',
        'Failover Test DHCP', 'Failover Test IsDhcp'
    ]
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(nic_settings)
    
    print(f"CSV file created: {csv_file}")

if __name__ == '__main__':
    main()