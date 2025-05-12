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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
import json
import csv
import sys
import os
from pathlib import Path
import urllib3
from typing import List, Dict, Tuple
from datetime import datetime

# Add parent directory to path to import zvml
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from zvml import ZVMLClient

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


"""
Zerto VPG NIC Settings Import Script

This script imports Virtual Protection Group (VPG) NIC settings from a CSV file, allowing for
bulk updates of network and IP configurations. It's designed to work with the exported CSV
from export_vpg_settings_nics_to_csv.py.

Key Features:
1. VPG NIC Settings Import:
   - Import NIC settings from CSV file
   - Update specific VPGs or all VPGs
   - Validate settings before applying
   - Support for both DHCP and static IP configurations

2. Settings Validation:
   - Validate DHCP and static IP settings
   - Check ShouldReplaceIpConfiguration flag
   - Ensure no conflicting configurations
   - Verify network identifiers

3. Bulk Updates:
   - Process multiple VPGs in one operation
   - Show changes before applying
   - Require confirmation before updates
   - Detailed logging of changes

Required Arguments:
    --zvm_address: ZVM address
    --client_id: Keycloak client ID
    --client_secret: Keycloak client secret
    --ignore_ssl: Ignore SSL certificate verification (optional)
    --csv_file: Path to the CSV file with updated settings
    --vpg_names: Comma-separated list of VPG names to update (optional)

Example Usage:
    python import_vpg_settings_nics_from_csv.py \
        --zvm_address "192.168.111.20" \
        --client_id "zerto-api" \
        --client_secret "your-secret-here" \
        --csv_file "ExportedSettings_2024-05-12.csv" \
        --vpg_names "VpgTest1,VpgTest2" \
        --ignore_ssl

CSV Format Requirements:
    - Must include VPG Name, VM Identifier, and NIC Identifier
    - DHCP values must be "True" or "False" (case-insensitive)
    - ShouldReplaceIpConfiguration must be "True" to modify IP settings
    - Static IP settings (IP, Subnet, Gateway, DNS) are optional when DHCP is True

Note: This script is part of a pair with export_vpg_settings_nics_to_csv.py. It's designed
to safely update VPG NIC settings in bulk, with validation and confirmation steps to
prevent unintended changes.
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

def read_csv_settings(csv_path: str) -> List[Dict]:
    """Read settings from CSV file."""
    settings = []
    with open(csv_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            settings.append(row)
    return settings

def get_current_settings(client: ZVMLClient, vpg_names: List[str] = None) -> Tuple[str, List[Dict]]:
    """Get current VPG settings and convert to CSV format."""
    # Export current settings
    export_result = client.vpgs.export_vpg_settings(vpg_names)
    if not export_result or 'TimeStamp' not in export_result:
        raise Exception("Failed to export VPG settings")
    
    timestamp = export_result['TimeStamp']
    export_settings = client.vpgs.read_exported_vpg_settings(timestamp, vpg_names)
    # logging.info(f"get_current_settings: export_settings: {json.dumps(export_settings, indent=4)}")
    # Convert to CSV format
    nic_settings = []
    for vpg in export_settings['ExportedVpgSettingsApi']:
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
    
    return timestamp, nic_settings

def normalize_value(value):
    """Normalize values for comparison."""
    # Treat None, empty string, and 'None' as the same
    if value in ['', None, 'None', 'null']:
        return ''
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, str):
        value = value.lower()
        if value == 'true':
            return 'true'
        if value == 'false':
            return 'false'
    return str(value)

def compare_settings(client, current: List[Dict], updated: List[Dict]) -> List[Dict]:
    """Compare current and updated settings and return changes."""
    changes = []
    
    # Create lookup dictionaries for faster comparison
    current_lookup = {
        (row['VPG Name'], row['VM Identifier'], row['NIC Identifier']): row
        for row in current
    }
    
    def validate_dhcp_settings(client, row: Dict, vpg_name: str, vm_id: str, nic_id: str):
        """Validate that DHCP and IP settings are not conflicting."""
        vm_name = client.vms.list_vms(vm_identifier=vm_id).get('VmName')

        def validate_ip_settings(prefix: str):
            should_replace = normalize_value(row.get(f'{prefix} ShouldReplaceIpConfiguration', '')) == 'true'
            dhcp = normalize_value(row.get(f'{prefix} DHCP', '')) == 'true'
            has_static_ip = any(row.get(f'{prefix} {field}') for field in ['IP', 'Subnet', 'Gateway', 'DNS1', 'DNS2'])

            if not should_replace and (dhcp or has_static_ip):
                raise ValueError(
                    f"Invalid configuration for VPG '{vpg_name}', VM Name '{vm_name}', VM ID '{vm_id}', NIC '{nic_id}': "
                    f"{prefix} ShouldReplaceIpConfiguration is False but IP settings are present. "
                    f"Set ShouldReplaceIpConfiguration to True to modify IP settings."
                )

            if should_replace and not dhcp and not has_static_ip:
                raise ValueError(
                    f"Invalid configuration for VPG '{vpg_name}', VM Name '{vm_name}', VM ID '{vm_id}', NIC '{nic_id}': "
                    f"{prefix} ShouldReplaceIpConfiguration is True but no IP configuration is provided. "
                    f"Either set DHCP=True or provide IP configuration (IP, Subnet, Gateway, DNS1, DNS2)."
                )

            if dhcp and has_static_ip:
                raise ValueError(
                    f"Invalid configuration for VPG '{vpg_name}', VM Name '{vm_name}', VM ID '{vm_id}', NIC '{nic_id}': "
                    f"Cannot have {prefix} DHCP=True and static IP settings. "
                    f"Please remove static IP settings or set DHCP=False."
                )

        # Validate both failover and failover test settings
        validate_ip_settings('Failover')
        validate_ip_settings('Failover Test')
    
    for updated_row in updated:
        key = (updated_row['VPG Name'], updated_row['VM Identifier'], updated_row['NIC Identifier'])
        
        # Validate DHCP settings before processing changes
        validate_dhcp_settings(
            client,
            updated_row,
            updated_row['VPG Name'],
            updated_row['VM Identifier'],
            updated_row['NIC Identifier']
        )
        
        if key in current_lookup:
            current_row = current_lookup[key]
            row_changes = {}
            
            # Compare each field
            for field in updated_row:
                if field in ['VPG Name', 'VM Identifier', 'NIC Identifier']:
                    continue
                
                current_value = normalize_value(current_row.get(field, ''))
                updated_value = normalize_value(updated_row.get(field, ''))
                
                # Only include the change if the values are different after normalization
                if current_value != updated_value:
                    row_changes[field] = {
                        'current': current_row.get(field, ''),
                        'updated': updated_row.get(field, '')
                    }
            
            if row_changes:
                vm_name = client.vms.list_vms(vm_identifier=updated_row['VM Identifier']).get('VmName')
                logging.info(f"compare_settings: vm_name {vm_name}")

                changes.append({
                    'VPG Name': updated_row['VPG Name'],
                    'VM Identifier': updated_row['VM Identifier'],
                    'NIC Identifier': updated_row['NIC Identifier'],
                    'VM Name': vm_name,
                    'changes': row_changes
                })
    
    return changes

def display_changes(client, changes: List[Dict]):
    """Display changes in a user-friendly format."""
    if not changes:
        print("\nNo changes found in the CSV file.")
        return
    
    # Group changes by VPG
    vpg_changes = {}
    for change in changes:
        vpg_name = change['VPG Name']
        if vpg_name not in vpg_changes:
            vpg_changes[vpg_name] = {}
        
        vm_id = change['VM Identifier']
        if vm_id not in vpg_changes[vpg_name]:
            vpg_changes[vpg_name][vm_id] = {}
        
        nic_id = change['NIC Identifier']
        vpg_changes[vpg_name][vm_id][nic_id] = change['changes']
    
    print("\nThe following changes will be applied:")
    print("=" * 80)
    
    for vpg_name, vm_changes in vpg_changes.items():
        # Skip VPGs with no actual changes
        has_vpg_changes = False
        for vm_id, nic_changes in vm_changes.items():
            for nic_id, changes in nic_changes.items():
                if any(values['current'] != values['updated'] for values in changes.values()):
                    has_vpg_changes = True
                    break
            if has_vpg_changes:
                break
        
        if not has_vpg_changes:
            continue
            
        print(f"\nVPG: {vpg_name}")
        print("-" * 40)
        
        for vm_id, nic_changes in vm_changes.items():
            # Skip VMs with no actual changes
            has_vm_changes = False
            for nic_id, changes in nic_changes.items():
                if any(values['current'] != values['updated'] for values in changes.values()):
                    has_vm_changes = True
                    break
            
            if not has_vm_changes:
                continue

            vm_name = client.vms.list_vms(vm_identifier=vm_id).get('VmName')
            print(f"  VM name: {vm_name}, VM ID: {vm_id}")
            
            for nic_id, changes in nic_changes.items():
                # Skip NICs with no actual changes
                if not any(values['current'] != values['updated'] for values in changes.values()):
                    continue
                    
                print(f"    NIC: {nic_id}")
                print("    Changes:")
                for field, values in changes.items():
                    # Only show fields that have actual changes
                    if values['current'] != values['updated']:
                        print(f"      {field}:")
                        print(f"        Current: {values['current']}")
                        print(f"        Updated: {values['updated']}")
                print()
    
    print("=" * 80)
    print(f"\nTotal changes: {len(changes)} NIC(s) across {len(vpg_changes)} VPG(s)")

def update_vpg_settings(client: ZVMLClient, changes: List[Dict]):
    """Update VPG settings based on changes."""
    # Group changes by VPG
    vpg_changes = {}
    for change in changes:
        vpg_name = change['VPG Name']
        if vpg_name not in vpg_changes:
            vpg_changes[vpg_name] = []
        vpg_changes[vpg_name].append(change)
    
    # Process each VPG
    for vpg_name, vpg_change_list in vpg_changes.items():
        logging.info(f"update_vpg_settings: Processing VPG: {vpg_name}")
        logging.info(f"update_vpg_settings: VPG change list: {json.dumps(vpg_change_list, indent=4)}")
        
        # Get VPG identifier
        vpg_info = client.vpgs.list_vpgs(vpg_name=vpg_name)
        if not vpg_info:
            logging.error(f"update_vpg_settings: VPG {vpg_name} not found")
            continue
        vpg_identifier = vpg_info['VpgIdentifier']
        
        # Create new VPG settings
        vpg_settings_id = client.vpgs.create_vpg_settings(vpg_identifier=vpg_identifier)
        vpg_settings = client.vpgs.get_vpg_settings_by_id(vpg_settings_id)
        logging.info(f"update_vpg_settings: VPG settings: {json.dumps(vpg_settings, indent=4)}")

        # Process each NIC change
        for change in vpg_change_list:
            vm_id = change['VM Identifier']
            nic_id = change['NIC Identifier']
            vm_name = change['VM Name']
            logging.info(f"update_vpg_settings: Processing NIC: {nic_id} for VM: {vm_name} VM ID: {vm_id}")
            # Find the VM and NIC in the settings
            vm = None
            for v in vpg_settings['Vms']:
                if v['VmIdentifier'] == vm_id:
                    vm = v
                    # logging.info(f"update_vpg_settings: Found VM: {vm_id} in VPG {vpg_name} vm={json.dumps(vm, indent=4)}")
                    break
            
            if not vm:
                logging.error(f"update_vpg_settings: VM {vm_id} not found in VPG {vpg_name}")
                continue
            
            # Find the NIC
            nic = None
            for n in vm['Nics']:
                if n['NicIdentifier'] == nic_id:
                    nic = n
                    logging.info(f"update_vpg_settings: Found NIC: {nic_id} in VM {vm_name} VPG {vpg_name} nic={json.dumps(nic, indent=4)}") 
                    break
            
            if not nic:
                logging.error(f"update_vpg_settings: NIC {nic_id} not found in VM {vm_id}")
                continue
            
            # Initialize structures if needed
            if not nic.get('Failover'):
                nic['Failover'] = {'Hypervisor': {}}
            if not nic.get('FailoverTest'):
                nic['FailoverTest'] = {'Hypervisor': {}}

            # Process each change for this NIC
            for field, values in change['changes'].items():
                # Handle Failover settings
                if field in ['Failover Network', 'Failover ShouldReplaceIpConfiguration', 'Failover IP', 
                           'Failover Subnet', 'Failover Gateway', 'Failover DNS1', 'Failover DNS2', 
                           'Failover DHCP']:
                    if field == 'Failover ShouldReplaceIpConfiguration':
                        nic['Failover']['Hypervisor']['ShouldReplaceIpConfiguration'] = normalize_value(values['updated']) == 'true'
                    elif field == 'Failover Network':
                        nic['Failover']['Hypervisor']['NetworkIdentifier'] = values['updated']
                    elif field == 'Failover DHCP':
                        if not nic['Failover']['Hypervisor'].get('IpConfig'):
                            nic['Failover']['Hypervisor']['IpConfig'] = {
                                'StaticIp': None,
                                'SubnetMask': None,
                                'Gateway': None,
                                'PrimaryDns': None,
                                'SecondaryDns': None,
                                'IsDhcp': False
                            }
                        nic['Failover']['Hypervisor']['IpConfig']['IsDhcp'] = normalize_value(values['updated']) == 'true'
                        # If DHCP is enabled, clear other IP settings
                        if normalize_value(values['updated']) == 'true':
                            nic['Failover']['Hypervisor']['IpConfig'].update({
                                'StaticIp': None,
                                'SubnetMask': None,
                                'Gateway': None,
                                'PrimaryDns': None,
                                'SecondaryDns': None
                            })
                    elif field in ['Failover IP', 'Failover Subnet', 'Failover Gateway', 
                                 'Failover DNS1', 'Failover DNS2']:
                        if not nic['Failover']['Hypervisor'].get('IpConfig'):
                            nic['Failover']['Hypervisor']['IpConfig'] = {
                                'StaticIp': None,
                                'SubnetMask': None,
                                'Gateway': None,
                                'PrimaryDns': None,
                                'SecondaryDns': None,
                                'IsDhcp': False
                            }
                        if field == 'Failover IP':
                            nic['Failover']['Hypervisor']['IpConfig']['StaticIp'] = values['updated'] if values['updated'] else None
                        elif field == 'Failover Subnet':
                            nic['Failover']['Hypervisor']['IpConfig']['SubnetMask'] = values['updated'] if values['updated'] else '255.255.255.0'
                        elif field == 'Failover Gateway':
                            nic['Failover']['Hypervisor']['IpConfig']['Gateway'] = values['updated'] if values['updated'] else None
                        elif field == 'Failover DNS1':
                            nic['Failover']['Hypervisor']['IpConfig']['PrimaryDns'] = values['updated'] if values['updated'] else None
                        elif field == 'Failover DNS2':
                            nic['Failover']['Hypervisor']['IpConfig']['SecondaryDns'] = values['updated'] if values['updated'] else None

                # Handle Failover Test settings
                elif field in ['Failover Test Network', 'Failover Test ShouldReplaceIpConfiguration', 
                             'Failover Test IP', 'Failover Test Subnet', 'Failover Test Gateway', 
                             'Failover Test DNS1', 'Failover Test DNS2', 'Failover Test DHCP']:
                    if field == 'Failover Test ShouldReplaceIpConfiguration':
                        nic['FailoverTest']['Hypervisor']['ShouldReplaceIpConfiguration'] = normalize_value(values['updated']) == 'true'
                    elif field == 'Failover Test Network':
                        nic['FailoverTest']['Hypervisor']['NetworkIdentifier'] = values['updated']
                    elif field == 'Failover Test DHCP':
                        if not nic['FailoverTest']['Hypervisor'].get('IpConfig'):
                            nic['FailoverTest']['Hypervisor']['IpConfig'] = {
                                'StaticIp': None,
                                'SubnetMask': None,
                                'Gateway': None,
                                'PrimaryDns': None,
                                'SecondaryDns': None,
                                'IsDhcp': False
                            }
                        nic['FailoverTest']['Hypervisor']['IpConfig']['IsDhcp'] = normalize_value(values['updated']) == 'true'
                        # If DHCP is enabled, clear other IP settings
                        if normalize_value(values['updated']) == 'true':
                            nic['FailoverTest']['Hypervisor']['IpConfig'].update({
                                'StaticIp': None,
                                'SubnetMask': None,
                                'Gateway': None,
                                'PrimaryDns': None,
                                'SecondaryDns': None
                            })
                    elif field in ['Failover Test IP', 'Failover Test Subnet', 'Failover Test Gateway', 
                                 'Failover Test DNS1', 'Failover Test DNS2']:
                        if not nic['FailoverTest']['Hypervisor'].get('IpConfig'):
                            nic['FailoverTest']['Hypervisor']['IpConfig'] = {
                                'StaticIp': None,
                                'SubnetMask': None,
                                'Gateway': None,
                                'PrimaryDns': None,
                                'SecondaryDns': None,
                                'IsDhcp': False
                            }
                        if field == 'Failover Test IP':
                            nic['FailoverTest']['Hypervisor']['IpConfig']['StaticIp'] = values['updated'] if values['updated'] else None
                        elif field == 'Failover Test Subnet':
                            nic['FailoverTest']['Hypervisor']['IpConfig']['SubnetMask'] = values['updated'] if values['updated'] else '255.255.255.0'
                        elif field == 'Failover Test Gateway':
                            nic['FailoverTest']['Hypervisor']['IpConfig']['Gateway'] = values['updated'] if values['updated'] else None
                        elif field == 'Failover Test DNS1':
                            nic['FailoverTest']['Hypervisor']['IpConfig']['PrimaryDns'] = values['updated'] if values['updated'] else None
                        elif field == 'Failover Test DNS2':
                            nic['FailoverTest']['Hypervisor']['IpConfig']['SecondaryDns'] = values['updated'] if values['updated'] else None

            logging.info(f"update_vpg_settings: Updated NIC structure: VPG {vpg_name} VM {vm_name} NIC {nic_id} nic={json.dumps(nic, indent=4)}")
        
        # Update VPG settings with all changes
        logging.info(f"update_vpg_settings: Updating VPG settings for {vpg_name}")
        logging.info(f"update_vpg_settings: VPG settings: {json.dumps(vpg_settings, indent=4)}")
        client.vpgs.update_vpg_settings(vpg_settings_id, vpg_settings)
        
        # Commit changes
        logging.info(f"update_vpg_settings: Committing changes for VPG: {vpg_name}")
        client.vpgs.commit_vpg(vpg_settings_id, vpg_name, sync=False)
        logging.info(f"update_vpg_settings: Successfully updated VPG: {vpg_name}")

def main():
    parser = argparse.ArgumentParser(description="Import VPG settings from CSV")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument('--client_id', required=True, help='Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    parser.add_argument("--csv_file", required=True, help="Path to the CSV file with updated settings")
    parser.add_argument("--vpg_names", help="Comma-separated list of VPG names to update (optional)")
    args = parser.parse_args()

    try:
        # Setup client
        client = setup_client(args)

        # Process VPG names if provided
        vpg_names = None
        if args.vpg_names:
            vpg_names = [name.strip() for name in args.vpg_names.split(',')]
            logging.info(f"Updating settings for VPGs: {json.dumps(vpg_names, indent=4)}")
        else:
            logging.info("No VPG names provided, will update all VPGs in the CSV file")

        # Read updated settings from CSV
        print("\nReading updated settings from CSV...")
        updated_settings = read_csv_settings(args.csv_file)
        # logging.info(f"Updated settings: {updated_settings}")
        
        # Get current settings
        print("Getting current VPG settings...")
        timestamp, current_settings = get_current_settings(client, vpg_names)
        
        # Compare settings
        print("Comparing settings...")
        try:
            changes = compare_settings(client, current_settings, updated_settings)
        except ValueError as e:
            print(f"\nError: {str(e)}")
            print("\nPlease fix the configuration in the CSV file and try again.")
            return
        
        # Display changes
        display_changes(client, changes)
        
        if not changes:
            print("\nNo changes to apply.")
            return
        
        # Ask for confirmation
        while True:
            response = input("\nDo you want to apply these changes? (yes/no): ").lower()
            if response in ['yes', 'y']:
                break
            elif response in ['no', 'n']:
                print("Changes cancelled.")
                return
            else:
                print("Please answer 'yes' or 'no'.")
        
        # Apply changes
        print("\nApplying changes...")
        update_vpg_settings(client, changes)
        print("\nAll changes have been applied successfully.")

    except Exception as e:
        if isinstance(e, ValueError):
            print(f"\nError: {str(e)}")
            print("\nPlease fix the configuration in the CSV file and try again.")
        else:
            logging.exception("Error occurred:")
        sys.exit(1)

if __name__ == "__main__":
    main() 