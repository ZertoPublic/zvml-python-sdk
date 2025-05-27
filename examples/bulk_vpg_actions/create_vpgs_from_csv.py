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

"""
Zerto VPG Creation from CSV Script

This script reads VPG settings from a CSV file and creates VPGs with the specified settings.
It supports creating multiple VPGs with different VMs using a single CSV file.

Key Features:
1. CSV-based VPG Creation:
   - Read VPG settings from CSV template
   - Create VPGs with specified settings
   - Add VMs to VPGs based on CSV entries

2. Resource Management:
   - Uses existing site resources (datastores, networks, etc.)
   - Validates resource IDs before VPG creation
   
Required Arguments:
    --zvm_address: ZVM IP address
    --client_id: API client ID
    --client_secret: API client secret
    --csv_file: Path to CSV file with VPG settings
    --ignore_ssl: Ignore SSL certificate validation (optional)

Example Usage:
    python create_vpgs_from_csv.py \
        --zvm_address "192.168.111.20" \
        --client_id "zerto-api" \
        --client_secret "your-secret-here" \
        --csv_file "vpg_template.csv" \
        --ignore_ssl
"""

import argparse
import csv
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
import sys
import os
import urllib3
import json
from typing import Dict, List
from collections import defaultdict

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from zvml import ZVMLClient

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_argparse() -> argparse.ArgumentParser:
    """Set up command line argument parsing."""
    parser = argparse.ArgumentParser(description='Create VPGs from CSV settings')
    parser.add_argument('--zvm_address', required=True, help='ZVM IP address')
    parser.add_argument('--client_id', required=True, help='API client ID')
    parser.add_argument('--client_secret', required=True, help='API client secret')
    parser.add_argument('--csv_file', required=True, help='Path to CSV file with VPG settings')
    parser.add_argument('--ignore_ssl', action='store_true', help='Ignore SSL certificate validation')

    return parser

def read_vpg_settings(csv_file: str) -> Dict[str, List[Dict]]:
    """Read VPG settings from CSV file and group by VPG name."""
    vpg_settings = defaultdict(list)
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            vpg_name = row['VPG Name']
            vpg_settings[vpg_name].append(row)
    
    return vpg_settings

def create_vpg_payload(vpg_row: Dict) -> Dict:
    """Create VPG payload from CSV row."""
    # Basic settings
    basic = {
        "Name": vpg_row['VPG Name'],
        "VpgType": vpg_row['VPG Type'],
        "RpoInSeconds": int(vpg_row['RPO (seconds)']),
        "TestIntervalInMinutes": int(vpg_row['Test Interval (minutes)']),
        "JournalHistoryInHours": int(vpg_row['Journal History (hours)']),
        "Priority": vpg_row['Priority'],
        "UseWanCompression": vpg_row['Use WAN Compression'].lower() == 'true',
        "ProtectedSiteIdentifier": vpg_row['Protected Site ID'],
        "RecoverySiteIdentifier": vpg_row['Recovery Site ID']
    }

    # Journal settings
    journal = {
        "DatastoreIdentifier": vpg_row['Journal Datastore ID'],
        "Limitation": {
            "HardLimitInMB": int(vpg_row['Journal Hard Limit (MB)']),
            "WarningThresholdInMB": int(vpg_row['Journal Warning Threshold (MB)'])
        }
    }

    # Recovery settings
    recovery = {
        "DefaultHostClusterIdentifier": vpg_row['Recovery Host Cluster ID'],
        "DefaultDatastoreIdentifier": vpg_row['Recovery Datastore ID'],
        "DefaultFolderIdentifier": vpg_row['Recovery Folder ID']
    }

    # Network settings
    networks = {
        "Failover": {
            "Hypervisor": {
                "DefaultNetworkIdentifier": vpg_row['Failover Network ID']
            }
        },
        "FailoverTest": {
            "Hypervisor": {
                "DefaultNetworkIdentifier": vpg_row['Failover Test Network ID']
            }
        }
    }

    return {
        "basic": basic,
        "journal": journal,
        "recovery": recovery,
        "networks": networks
    }

def validate_vpg_and_vms(client: ZVMLClient, vpg_settings: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
    """
    Validate VPGs and VMs before creation.
    Returns a dictionary of valid VPGs and VMs to create.
    """
    try:
        # Get existing VPGs and VMs
        existing_vpgs = {vpg['VpgName']: vpg for vpg in client.vpgs.list_vpgs()}
        existing_vms = {vm['VmIdentifier']: vm for vm in client.vms.list_vms()}
        local_site_id = client.localsite.get_local_site()['Link']['identifier']
        eligible_vms = {vm['VmIdentifier']: vm for vm in client.virtualization_sites.get_virtualization_site_vms(local_site_id)}
        logger.debug(f"validate_vpg_and_vms: existing_vms: {json.dumps(existing_vms, indent=4)}")
        logger.debug(f"validate_vpg_and_vms: eligible_vms: {json.dumps(eligible_vms, indent=4)}")

        # Track VMs that appear in multiple VPGs
        vm_id_occurrences = defaultdict(list)
        vm_name_occurrences = defaultdict(list)
        valid_vpg_settings = defaultdict(list)
        vm_warnings = []  # Track warnings for VMs that are already protected

        # First pass: collect all VM occurrences
        for vpg_name, vpg_rows in vpg_settings.items():
            for row in vpg_rows:
                vm_id = row['VM ID']
                vm_name = row.get('VM Name', '')
                vm_id_occurrences[vm_id].append(vpg_name)
                if vm_name:
                    vm_name_occurrences[vm_name].append(vpg_name)

        # Check for duplicates
        for vm_id, vpgs in vm_id_occurrences.items():
            if len(vpgs) > 1:
                logger.error(f"ERROR: VM ID '{vm_id}' found in multiple VPGs: {', '.join(vpgs)}. Exiting...")
                sys.exit(1)

        for vm_name, vpgs in vm_name_occurrences.items():
            if len(vpgs) > 1:
                logger.error(f"ERROR: VM Name '{vm_name}' found in multiple VPGs: {', '.join(vpgs)}. Exiting...")
                sys.exit(1)

        # Second pass: validate VPGs and VMs
        for vpg_name, vpg_rows in vpg_settings.items():
            if vpg_name in existing_vpgs:
                logger.error(f"ERROR: VPG '{vpg_name}' already exists. Skipping VPG creation...")
                sys.exit(1)

            valid_vms = []
            for row in vpg_rows:
                vm_id = row['VM ID']
                vm_name = row.get('VM Name', '')
                
                # Check if VM exists in eligible and existing VMs list
                if vm_id not in eligible_vms and vm_id not in existing_vms:
                    logger.error(f"ERROR: VM '{vm_name}' with ID '{vm_id}' is not found in the eligible and existing VMs list. Exiting")
                    sys.exit(1)
                
                # Check if VM is already in a VPG
                if vm_id in existing_vms:
                    existing_vm = existing_vms[vm_id]
                    warning_msg = f"WARNING: VM '{vm_name}' with ID '{vm_id}' already exists in VPG '{existing_vm['VpgName']}' on site '{existing_vm.get('RecoverySiteName', 'N/A')}'.\n\
                        Creating a new VPG {vpg_name} will only succeed if the target site is different than {existing_vm.get('RecoverySiteName', 'N/A')}"
                    vm_warnings.append(warning_msg)
                    logger.warning(warning_msg)
                
                # Add VM to valid list
                valid_vms.append(row)
            
            # Add VPG to valid settings if it has any valid VMs
            if valid_vms:
                valid_vpg_settings[vpg_name] = valid_vms

        # Print validation summary
        print("\nValidation Summary:")
        print("------------------")
        
        if vm_warnings:
            print("\nWarnings:")
            print("---------")
            for warning in vm_warnings:
                print(f"  - {warning}")
            print("\nNote: Some VMs are already protected but will be added to new VPGs.")
        
        if valid_vpg_settings:
            print(f"\nVPGs to be created ({len(valid_vpg_settings)}):")
            for vpg_name, vms in valid_vpg_settings.items():
                print(f"  - {vpg_name} with {len(vms)} VMs:")
                for vm in vms:
                    vm_id = vm['VM ID']
                    vm_name = vm.get('VM Name', 'N/A')
                    print(f"    * {vm_id} ({vm_name})")
        else:
            print("\nNo VPGs to create - all VPGs were skipped")
        
        print("\nDo you want to continue with VPG creation? (y/n)")
        try:
            response = input().lower()
            if response != 'y':
                logger.info("Operation cancelled by user")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user (Ctrl+C)")
            sys.exit(0)
        
        return valid_vpg_settings
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.exception("Error during validation:")
        sys.exit(1)

def main():
    """Main function to execute the script."""
    try:
        parser = setup_argparse()
        args = parser.parse_args()
        
        # Initialize ZVM client
        client = ZVMLClient(
            zvm_address=args.zvm_address,
            client_id=args.client_id,
            client_secret=args.client_secret,
            verify_certificate=not args.ignore_ssl
        )
        
        # Read VPG settings from CSV
        logger.info(f"Reading VPG settings from {args.csv_file}...")
        vpg_settings = read_vpg_settings(args.csv_file)
        
        # Validate VPGs and VMs
        logger.info("Validating VPGs and VMs...")
        valid_vpg_settings = validate_vpg_and_vms(client, vpg_settings)
        
        if not valid_vpg_settings:
            logger.error("No valid VPGs to create. Exiting...")
            sys.exit(1)
        
        # Process each valid VPG
        for vpg_name, vpg_rows in valid_vpg_settings.items():
            vpg_id = None
            try:
                logger.info(f"Processing VPG: {vpg_name}")
                
                # Use first row for VPG settings (they should be the same for all VMs in a VPG)
                vpg_payload = create_vpg_payload(vpg_rows[0])
                
                # Create VPG
                logger.info(f"Creating VPG {vpg_name}...")
                vpg_id = client.vpgs.create_vpg(
                    basic=vpg_payload['basic'],
                    journal=vpg_payload['journal'],
                    recovery=vpg_payload['recovery'],
                    networks=vpg_payload['networks']
                )
                logger.info(f"VPG {vpg_name} created successfully with ID: {vpg_id}")
                
                # Track if all VMs were added successfully
                all_vms_added = True
                failed_vms = []
                
                # Add VMs to VPG
                for row in vpg_rows:
                    vm_id = row['VM ID']
                    vm_name = row.get('VM Name', 'N/A')
                    try:
                        logger.info(f"Adding VM {vm_id} ({vm_name}) to VPG {vpg_name}...")
                        vm_payload = {
                            "VmIdentifier": vm_id,
                            "Recovery": {
                                "HostClusterIdentifier": vpg_payload['recovery']['DefaultHostClusterIdentifier'],
                                "DatastoreIdentifier": vpg_payload['recovery']['DefaultDatastoreIdentifier'],
                                "FolderIdentifier": vpg_payload['recovery']['DefaultFolderIdentifier']
                            }
                        }
                        task_id = client.vpgs.add_vm_to_vpg(vpg_name, vm_list_payload=vm_payload)
                        logger.info(f"Task ID: {task_id} to add VM {vm_id} to VPG {vpg_name}")
                    except Exception as e:
                        logger.error(f"Failed to add VM {vm_id} ({vm_name}) to VPG {vpg_name}: {str(e)}")
                        all_vms_added = False
                        failed_vms.append((vm_id, vm_name, str(e)))
                
                # If any VM addition failed, delete the VPG
                if not all_vms_added:
                    logger.error(f"Failed to add some VMs to VPG {vpg_name}. Deleting VPG...")
                    if vpg_id:
                        try:
                            client.vpgs.delete_vpg(vpg_name)
                            logger.info(f"Successfully deleted VPG {vpg_name}")
                        except Exception as e:
                            logger.error(f"Failed to delete VPG {vpg_name}: {str(e)}")
                    
                    # Print detailed error summary
                    print("\nFailed VM Additions:")
                    print("-------------------")
                    for vm_id, vm_name, error in failed_vms:
                        print(f"  - VM: {vm_name} (ID: {vm_id})")
                        print(f"    Error: {error}")
                    print(f"\nVPG {vpg_name} was deleted due to VM addition failures.")
                    continue
                    
            except KeyboardInterrupt:
                print(f"\nOperation cancelled by user (Ctrl+C) while processing VPG {vpg_name}")
                # Try to clean up the VPG if it was created
                if vpg_id:
                    try:
                        logger.info(f"Cleaning up - deleting VPG {vpg_name}...")
                        client.vpgs.delete_vpg(vpg_name)
                        logger.info(f"Successfully deleted VPG {vpg_name}")
                    except Exception as e:
                        logger.error(f"Failed to delete VPG {vpg_name}: {str(e)}")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Error processing VPG {vpg_name}: {str(e)}")
                # Try to clean up the VPG if it was created
                if vpg_id:
                    try:
                        logger.info(f"Cleaning up - deleting VPG {vpg_name}...")
                        client.vpgs.delete_vpg(vpg_name)
                        logger.info(f"Successfully deleted VPG {vpg_name}")
                    except Exception as e:
                        logger.error(f"Failed to delete VPG {vpg_name}: {str(e)}")
                continue
        
        logger.info("VPG creation completed successfully")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.exception("Error occurred:")
        sys.exit(1)

if __name__ == '__main__':
    main() 