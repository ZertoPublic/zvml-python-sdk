#!/usr/bin/python3

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
Zerto Virtual Machines Example Script

This script demonstrates how to manage and retrieve information about protected virtual machines in Zerto.

The script performs the following steps:
1. Connects to Zerto Virtual Manager (ZVM)
2. Gets site information and resources:
   - Local and peer site details
   - Available datastores
   - Network configurations
3. Demonstrates VM operations:
   - Lists all protected VMs
   - Gets detailed information for specific VMs
   - Filters VMs by VPG name
   - Manages VM restore points:
     * Lists available checkpoints
     * Gets points in time
     * Retrieves recovery statistics
4. Shows VM restore capabilities:
   - Configures restore settings
   - Handles network and storage mappings
   - Manages restore operations

Required Arguments:
    --zvm_address: ZVM address
    --client_id: Keycloak client ID
    --client_secret: Keycloak client secret

Optional Arguments:
    --ignore_ssl: Ignore SSL certificate verification

Example Usage:
    python examples/vms_example.py \
        --zvm_address <zvm_address> \
        --client_id <client_id> \
        --client_secret <client_secret> \
        --ignore_ssl

Note: VM restore functionality is commented out in this example as it may return a 500 error.
"""

# NOTE
# this example assumes that at least one VPG exists on the ZVM and protected VMs exist in the VPG
# the vm restore is commnted out as it fails with a 500 

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import logging
import urllib3
import json
from zvml import ZVMLClient

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    parser = argparse.ArgumentParser(description="Zerto Virtual Machines Example")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument('--client_id', required=True, help='Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        # Connect to ZVM
        logging.info(f"Connecting to ZVM at {args.zvm_address}")
        client = ZVMLClient(
            zvm_address=args.zvm_address,
            client_id=args.client_id,
            client_secret=args.client_secret,
            verify_certificate=not args.ignore_ssl
        )

        # Get both sites information
        sites = client.virtualization_sites.get_virtualization_sites()
        logging.info(f"Found {len(sites)} sites:")
        for site in sites:
            logging.info(f"Site: {site['VirtualizationSiteName']} (ID: {site['SiteIdentifier']})")

        # Get the peer (second) site identifier
        local_site = client.localsite.get_local_site()
        local_site_id = local_site['SiteIdentifier']
        logging.info(f"Local site identifier: {local_site_id}")

        peer_site = next(site for site in sites 
                        if site['SiteIdentifier'] != local_site['SiteIdentifier'])
        peer_site_id = peer_site['SiteIdentifier']
        logging.info(f"Peer site identifier: {peer_site_id}")

        # Get datastores from peer site
        datastores = client.virtualization_sites.get_virtualization_site_datastores(peer_site_id)
        if not datastores:
            raise ValueError("No datastores found in peer site")
        # logging.info(json.dumps(datastores, indent=2))
        datastore_id = datastores[0]['DatastoreIdentifier']  # Use first datastore
        logging.info(f"Selected datastore ID from peer site: {datastore_id}")

        # Get networks from peer site
        networks = client.virtualization_sites.get_virtualization_site_networks(peer_site_id)
        if not networks:
            raise ValueError("No networks found in peer site")
        network_id = networks[0]['NetworkIdentifier']  # Use first network
        logging.info(f"Selected network ID from peer site: {network_id}")

        # Example 1: Get all protected VMs
        logging.info("\nExample 1: Getting all protected VMs")
        vms = client.vms.list_vms()
        logging.info(f'vms: {json.dumps(vms, indent=2)}')
        if len(vms) == 0:
            raise ValueError("No protected VMs found")  
        
        # Example 1.1: Get all unprotected VMs at the local site
        unprotected_vms = client.virtualization_sites.get_virtualization_site_vms(local_site_id)
        if not unprotected_vms:
            raise ValueError("No unprotected vms found at local site")
        logging.info(f"Unprotected vms at the local site: {json.dumps(unprotected_vms, indent=2)}")

        # Example 2: If we found any VMs, get details for the first one
        first_vm = vms[0]
        vm_id = first_vm['VmIdentifier']
        vpg_id = first_vm.get('VpgIdentifier')  # VpgIdentifier might be optional
        
        logging.info(f"\nExample 2: Getting details for VM {vm_id}")
        vm_details = client.vms.list_vms(
            vm_identifier=vm_id,
            vpg_identifier=vpg_id
        )
        # logging.info("VM details:")
        # logging.info(json.dumps(vm_details, indent=2))
        
        # Example 3: Get VMs filtered by VPG name
        vpg_name = first_vm.get('VpgName')
        if vpg_name:
            logging.info(f"\nExample 3: Getting VMs filtered by VPG name: {vpg_name}")
            filtered_vms = client.vms.list_vms(vpg_name=vpg_name)
            # logging.info(f"Found {len(filtered_vms)} VMs in VPG {vpg_name}:")
            # logging.info(json.dumps(filtered_vms, indent=2))

        # Example 4: Restore the VM if it has checkpoints
        logging.info("\nExample 4: Restoring VM from checkpoint")

        vpg_info = client.vpgs.list_vpgs(vpg_identifier=vpg_id)
        vpg_name = vpg_info['VpgName']

        checkpoints = client.vpgs.list_checkpoints(vpg_name=vpg_name)
        # logging.info(f"checkpoints: {json.dumps(checkpoints, indent=2)}")
        if not checkpoints:
            logging.warning("No checkpoints found for VPG")
            raise ValueError("No checkpoints found for VPG")

        checkpoint_id = checkpoints[0]['CheckpointIdentifier']
            
        # Prepare restore settings using IDs from peer site
        restore_settings = {
            "datastoreIdentifier": datastore_id,
            "nics": [
                {
                    "hypervisor": {
                        "dnsSuffix": "",
                        "ipConfig": {
                            "gateway": "",
                            "isDhcp": True,
                            "primaryDns": "",
                            "secondaryDns": "",
                            "staticIp": "",
                            "subnetMask": ""
                        },
                        "networkIdentifier": network_id,
                        "shouldReplaceMacAddress": True
                    },
                    "nicIdentifier": first_vm['Nics'][0]['NicIdentifier']
                }
            ],
            "volumes": [
                {
                    "datastore": {
                        "datastoreIdentifier": datastore_id,
                        "isThin": True
                    },
                    "volumeIdentifier": volume['VmVolumeIdentifier']
                } for volume in first_vm['Volumes']
            ]
        }
        
        # Initiate VM restore
        # temporary commented out as it fails with a 500
        # logging.info(f"Restoring VM {first_vm['VmName']} from checkpoint {checkpoint_id}")
        # restore_result = client.vms.restore_vm(
        #     vm_identifier=vm_id,
        #     vpg_identifier=vpg_id,
        #     restored_vm_name=f"{first_vm['VmName']}_restored",
        #     checkpoint_identifier=checkpoint_id,
        #     journal_vm_restore_settings=restore_settings
        # )
        # logging.info(f"Restore initiated: {json.dumps(restore_result, indent=2)}")
        
        # Example 7: Get points in time for a VM
        logging.info("\nExample 7: Getting points in time for VM")
        try:
            # You can optionally specify start_date and end_date in ISO format
            # e.g., "2024-01-01T00:00:00.000Z"
            points_in_time = client.vms.list_vm_points_in_time(
                vm_identifier=vm_id,
                vpg_identifier=vpg_id
            )
            logging.info(f"Found {len(points_in_time)} points in time:")
            logging.debug(json.dumps(points_in_time, indent=2))
        except Exception as e:
            logging.error(f"Failed to get VM points in time: {e}")
        
        # Example 8: Get points in time stats for a VM
        logging.info("\nExample 8: Getting points in time stats for VM")
        try:
            points_in_time_stats = client.vms.list_vm_points_in_time_stats(
                vm_identifier=vm_id,
                vpg_identifier=vpg_id  # Optional, but may be required if VM is in multiple VPGs
            )
            logging.info("Points in time stats:")
            logging.debug(json.dumps(points_in_time_stats, indent=2))
        except Exception as e:
            logging.error(f"Failed to get VM points in time stats: {e}")
        
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 