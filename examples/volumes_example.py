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
Zerto Volumes Example Script

This script demonstrates how to retrieve volume information from Zerto Virtual Manager (ZVM).
It shows how to list and filter volumes based on different criteria, making it useful for
volume management and monitoring.

Key Features:
1. List all volumes in the system
2. Filter volumes by:
   - VPG association
   - Datastore location
   - Protected VM attachment
3. Display volume details:
   - Volume identifiers
   - Storage information
   - Protection status
   - Resource associations

Required Arguments:
    --zvm_address: Site 1 ZVM address
    client_id: Site 1 Keycloak client ID
    client_secret: Site 1 Keycloak client secret
    --ignore_ssl: Ignore SSL certificate verification (optional)

Example Usage:
    python examples/volumes_example.py \
        --zvm_address "192.168.1.100" \
        client_id "zerto-api" \
        client_secret "your-secret-here" \
        --ignore_ssl

Note: This script focuses on volume operations and requires only Site 1 credentials
since it performs read-only operations on the protected site.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import urllib3
import argparse
import logging
import json
from zvml import ZVMLClient

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser(description="Zerto Volumes Example")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument('--client_id', required=True, help='Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        # Initialize the client
        client = ZVMLClient(args.zvm_address, args.client_id, args.client_secret, not args.ignore_ssl)

        # Example 1: List all volumes
        logging.info("\nExample 1: Listing all volumes")
        try:
            volumes = client.volumes.list_volumes()
            logging.info(f"Found {len(volumes)} volumes:")
            logging.info(json.dumps(volumes, indent=2))
        except Exception as e:
            logging.error(f"Failed to list volumes: {e}")

        # Example 2: List volumes for a specific VPG
        logging.info("\nExample 2: Listing volumes for a specific VPG")
        try:
            # First get a VPG ID
            vpgs = client.vpgs.list_vpgs()
            # logging.info(f"vpgs: {json.dumps(vpgs, indent=2)}")
            if vpgs:
                vpg_id = vpgs[0]['VpgIdentifier']
                logging.info(f"vpg_id: {vpg_id}")
                volumes = client.volumes.list_volumes(vpg_identifier=vpg_id)
                logging.info(f"Found {len(volumes)} volumes for VPG {vpg_id}:")
                logging.info(json.dumps(volumes, indent=2))
        except Exception as e:
            logging.error(f"Failed to list volumes for VPG: {e}")

        # Example 3: List volumes for a specific datastore
        logging.info("\nExample 3: Listing volumes for a specific datastore")
        try:
            local_site1_identifier = client.localsite.get_local_site().get('SiteIdentifier')
            logging.info(f"local_site1_identifier: {local_site1_identifier}")
            # First get a datastore ID
            datastores = client.virtualization_sites.get_virtualization_site_datastores(
                site_identifier=local_site1_identifier
            )

            for datastore in datastores:
                datastore_id = datastore['DatastoreIdentifier']
                volumes = client.volumes.list_volumes(datastore_identifier=datastore_id)
                logging.info(f"Found {len(volumes)} volumes for datastore {datastore_id}:")
                logging.info(json.dumps(volumes, indent=2))
        except Exception as e:
            logging.error(f"Failed to list volumes for datastore: {e}")

        # Example 4: List volumes for a specific protected VM
        logging.info("\nExample 4: Listing volumes for a specific protected VM")
        try:
            # First get a VM ID
            vms = client.vms.list_vms()
            if vms:
                vm_id = vms[0]['VmIdentifier']
                volumes = client.volumes.list_volumes(protected_vm_identifier=vm_id)
                logging.info(f"Found {len(volumes)} volumes for protected VM {vm_id}:")
                logging.info(json.dumps(volumes, indent=2))
        except Exception as e:
            logging.error(f"Failed to list volumes for protected VM: {e}")

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 