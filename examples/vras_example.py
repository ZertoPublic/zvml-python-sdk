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
Zerto Virtual Replication Appliance (VRA) Management Example Script

This script demonstrates how to manage VRAs using the Zerto Virtual Manager (ZVM) API.
It showcases VRA deployment, configuration, and cleanup operations.

Key Features:
1. VRA Management:
   - List existing VRAs and their details
   - Delete existing VRAs
   - Deploy new VRAs with custom configurations
   - Monitor VRA deployment status

2. Resource Selection:
   - Interactive selection of hosts
   - Interactive selection of datastores
   - Interactive selection of networks
   - Custom IP configuration for VRAs

3. Parallel Operations:
   - Deploy multiple VRAs simultaneously
   - Delete multiple VRAs in parallel
   - Monitor multiple VRA operations

Required Arguments:
    --zvm_address: ZVM server address
    --client_id: Keycloak client ID
    --client_secret: Keycloak client secret
    --ignore_ssl: Ignore SSL certificate verification (optional)

Example Usage:
    python examples/vras_example.py \
        --zvm_address "192.168.111.20" \
        --client_id "zerto-api" \
        --client_secret "your-secret-here" \
        --ignore_ssl

Script Flow:
1. Lists all existing VRAs and their details
2. Optionally deletes all existing VRAs
3. Creates new VRAs with user-selected resources:
   - First VRA with IP 192.168.111.30
   - Second VRA with IP 192.168.111.31 (optional)
4. Verifies final VRA configuration

Note: This script includes interactive prompts for resource selection and operation
confirmation. It demonstrates proper error handling and logging for VRA management
operations.
"""

# Configure logging BEFORE any imports
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
import argparse
import urllib3
import json
import sys
import os
import time
from typing import Dict, List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from zvml import ZVMLClient

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def setup_client(args):
    """Initialize and return Zerto client"""
    client = ZVMLClient(
        zvm_address=args.zvm_address,
        client_id=args.client_id,
        client_secret=args.client_secret,
        verify_certificate=not args.ignore_ssl
    )
    return client

def get_user_confirmation(prompt: str) -> bool:
    """Get user confirmation for an action"""
    while True:
        response = input(f"\n{prompt} (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            return True
        if response in ['no', 'n']:
            return False
        print("Please answer 'yes' or 'no'")

def select_from_list(items, item_type: str):
    """Let user select an item from a list"""
    logging.info(f"select_from_list: {json.dumps(items, indent=2)}")
    print(f"\nAvailable {item_type}s:")
    for idx, item in enumerate(items, 1):
        if 'VirtualizationHostName' in item:  # For hosts
            print(f"{idx}. {item['VirtualizationHostName']} ({item['HostIdentifier']})")
        elif 'DatastoreName' in item:  # For datastores
            print(f"{idx}. {item['DatastoreName']} ({item['DatastoreIdentifier']})")
        elif 'VirtualizationNetworkName' in item:  # For networks
            print(f"{idx}. {item['VirtualizationNetworkName']} ({item['NetworkIdentifier']})")
    
    while True:
        try:
            choice = int(input(f"\nSelect {item_type} (1-{len(items)}): "))
            if 1 <= choice <= len(items):
                return items[choice - 1]
        except ValueError:
            pass
        print(f"Please enter a number between 1 and {len(items)}")

def list_vras(client: ZVMLClient):
    """List all VRAs and their details"""
    vras = client.vras.list_vras()
    print(f"\nFound {len(vras)} VRAs:")
    for vra in vras:
        print(f"\nVRA Details:")
        print(f"  Name: {vra.get('VraName')}")
        print(f"  Status: {vra.get('Status')}")
        print(f"  IP Address: {vra.get('IpAddress')}")
        print(f"  Version: {vra.get('VraVersion')}")
        print(f"  Host: {vra.get('HostName')}")

def create_vra_with_selection(client: ZVMLClient, vra_number: int) -> Dict:
    """Create a VRA with user-selected resources"""
    # Get local site information
    local_site = client.localsite.get_local_site()
    site_id = local_site['SiteIdentifier']

    # Get available resources for the local site
    print("\nRetrieving available resources...")
    hosts = client.virtualization_sites.get_virtualization_site_hosts(site_id)
    if not hosts:
        raise ValueError("No hosts found in local site")
    
    datastores = client.virtualization_sites.get_virtualization_site_datastores(site_id)
    if not datastores:
        raise ValueError("No datastores found in local site")
    
    networks = client.virtualization_sites.get_virtualization_site_networks(site_id)
    if not networks:
        raise ValueError("No networks found in local site")

    # Let user select resources
    print("\nSelect resources for VRA deployment:")
    host = select_from_list(hosts, "Host")
    datastore = select_from_list(datastores, "Datastore")
    network = select_from_list(networks, "Network")

    while True:
        # Let user customize IP address
        default_ip = f"192.168.111.{30 + vra_number - 1}"
        custom_ip = input(f"\nEnter VRA IP address (press Enter to use default {default_ip}): ").strip()
        vra_ip = custom_ip if custom_ip else default_ip

        # Create VRA configuration
        vra_config = {
            "hostIdentifier": host['HostIdentifier'],
            "datastoreIdentifier": datastore['DatastoreIdentifier'],
            "networkIdentifier": network['NetworkIdentifier'],
            "hostRootPassword": input("\nEnter host root password: "),
            "memoryInGb": 3,
            "groupName": f"VRA_Group{vra_number}",
            "vraNetworkDataApi": {
                "vraIPConfigurationTypeApi": "Static",
                "vraIPAddress": vra_ip,
                "vraIPAddressRangeEnd": "",
                "subnetMask": "255.255.255.0",
                "defaultGateway": "192.168.111.254"
            },
            "usePublicKeyInsteadOfCredentials": False,
            "populatePostInstallation": True,
            "numOfCpus": 1,
            "vmInstanceType": ""
        }

        # Create VRA
        print(f"\nCreating VRA {vra_number} with configuration:")
        print(json.dumps(vra_config, indent=2))
        
        response = input("\nProceed with VRA creation? (yes/no/edit): ").lower().strip()
        if response in ['yes', 'y']:
            result = client.vras.create_vra(vra_config)
            print(f"VRA creation initiated: {json.dumps(result, indent=2)}")
            return result
        elif response in ['no', 'n']:
            return None
        elif response in ['edit', 'e']:
            print("\nRestarting VRA configuration...")
            continue
        else:
            print("Please answer 'yes', 'no', or 'edit'")

def main():
    parser = argparse.ArgumentParser(description="VRA Management Example")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument('--client_id', required=True, help='Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    args = parser.parse_args()

    try:
        # Setup client
        client = setup_client(args)
        
        # Step 1: List existing VRAs
        print("\nStep 1: Listing existing VRAs...")
        list_vras(client)

        # Step 2: Ask for deletion confirmation
        if get_user_confirmation("Would you like to delete all existing VRAs?"):
            print("\nStep 2: Deleting existing VRAs...")
            vras = client.vras.list_vras()
            for vra in vras:
                vra_id = vra.get('VraIdentifier')
                print(f"Deleting VRA: {vra.get('VraName')} ({vra_id})")
                client.vras.delete_vra(vra_id)
                print("Waiting for deletion to complete...")
                time.sleep(5)  # Give some time for deletion to process

        # Step 3: Create new VRAs
        if get_user_confirmation("Would you like to create new VRAs?"):
            print("\nStep 3: Creating new VRAs...")
            
            # Create first VRA
            print("\nConfiguring first VRA...")
            result1 = create_vra_with_selection(client, 1)
            if result1:
                print("Waiting for first VRA deployment to complete...")
                time.sleep(30)

            # Create second VRA
            if get_user_confirmation("Would you like to create a second VRA?"):
                print("\nConfiguring second VRA...")
                result2 = create_vra_with_selection(client, 2)
                if result2:
                    print("Waiting for second VRA deployment to complete...")
                    time.sleep(30)

        # Step 4: Verify final state
        print("\nStep 4: Verifying final VRA configuration...")
        list_vras(client)

    except Exception as e:
        logging.exception("Error occurred:")
        sys.exit(1)

if __name__ == "__main__":
    main() 