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
Zerto VPG Bulk Update Example Script

This script demonstrates how to update multiple Virtual Protection Groups (VPGs) settings in bulk.

The script performs the following steps:
1. Connects to Zerto Virtual Manager (ZVM)
2. Lists peer sites and their resources:
   - Available datastores
   - Available networks
3. Retrieves current VPG settings for all VPGs
4. Prompts for new settings:
   - Target datastore
   - Failover network
   - Test network
5. Updates all VPGs with the new settings after confirmation

Required Arguments:
    --zvm_address: Site 1 ZVM address
    --client_id: Site 1 Keycloak client ID
    --client_secret: Site 1 Keycloak client secret

Optional Arguments:
    --ignore_ssl: Ignore SSL certificate verification

Example Usage:
    python examples/update_existing_vpgs.py \
        --zvm_address <zvm_address> \
        --client_id <client_id> \
        --client_secret <client_secret> \
        --ignore_ssl
"""
# Configure logging BEFORE any imports
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
import argparse
import urllib3
import sys
import os
import json
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

def print_site_resources(client, site_identifier: str, site_name: str):
    """Print site resources in a visual way"""
    print(f"\nSite: {site_name}")
    print(f"Site ID: {site_identifier}")
    
    # Get and print datastores
    print("\nDatastores:")
    datastores = client.virtualization_sites.get_virtualization_site_datastores(site_identifier)
    datastore_map = {}
    for idx, ds in enumerate(datastores, 1):
        datastore_map[idx] = ds['DatastoreIdentifier']
        name = ds.get('DatastoreName', 'N/A')
        logical_name = ds.get('LogicalName', 'N/A')
        print(f"  {idx}. ID: {ds['DatastoreIdentifier']}")
        print(f"     Name: {name}")
        print(f"     Logical Name: {logical_name}")
    
    # Get and print networks
    print("\nNetworks:")
    networks = client.virtualization_sites.get_virtualization_site_networks(site_identifier)
    network_map = {}
    for idx, net in enumerate(networks, 1):
        network_map[idx] = net['NetworkIdentifier']
        name = net.get('VirtualizationNetworkName', 'N/A')
        print(f"  {idx}. ID: {net['NetworkIdentifier']}")
        print(f"     Name: {name}")
    
    return datastore_map, network_map

def get_vpg_settings(client, vpgs: List[Dict]):
    """Get current VPG settings"""
    vpg_settings = []
    for vpg in vpgs:
        vpg_id = vpg['VpgIdentifier']
        vpg_name = vpg['VpgName']
        
        # Create new settings based on existing VPG
        settings_id = client.vpgs.create_vpg_settings(
            basic=None, 
            journal=None, 
            recovery=None, 
            networks=None, 
            vpg_identifier=vpg_id
        )
        
        # Get the settings details
        settings = client.vpgs.get_vpg_settings_by_id(vpg_settings_id=settings_id)
        
        vpg_settings.append({
            'vpg_name': vpg_name,
            'vpg_id': vpg_id,
            'settings_id': settings_id,
            'current_settings': settings,
            'default_datastore': settings.get('Recovery', {}).get('DefaultDatastoreIdentifier'),
            'failover_network': settings.get('Networks', {}).get('Failover', {}).get('Hypervisor', {}).get('DefaultNetworkIdentifier'),
            'test_network': settings.get('Networks', {}).get('FailoverTest', {}).get('Hypervisor', {}).get('DefaultNetworkIdentifier')
        })
        
        print(f"\nVPG: {vpg_name}")
        print(f"  Current Datastore: {settings.get('Recovery', {}).get('DefaultDatastoreIdentifier')}")
        print(f"  Current Failover Network: {settings.get('Networks', {}).get('Failover', {}).get('Hypervisor', {}).get('DefaultNetworkIdentifier')}")
        print(f"  Current Test Network: {settings.get('Networks', {}).get('FailoverTest', {}).get('Hypervisor', {}).get('DefaultNetworkIdentifier')}")
    
    return vpg_settings

def update_vpg_settings(client, vpg_settings: List[Dict], new_datastore: str, new_failover_network: str, new_test_network: str):
    """Update all VPG settings with new values"""
    for vpg in vpg_settings:
        settings = vpg['current_settings']
        
        # Update datastore
        settings['Recovery']['DefaultDatastoreIdentifier'] = new_datastore
        
        # Update networks
        if 'Networks' not in settings:
            settings['Networks'] = {'Failover': {'Hypervisor': {}}, 'FailoverTest': {'Hypervisor': {}}}
        
        
        settings['Networks']['Failover']['Hypervisor']['DefaultNetworkIdentifier'] = new_failover_network
        settings['Networks']['FailoverTest']['Hypervisor']['DefaultNetworkIdentifier'] = new_test_network
        
        # Update the settings
        client.vpgs.update_vpg_settings(vpg_settings_id=vpg['settings_id'], payload=settings)

        # Commit the changes
        client.vpgs.commit_vpg(vpg['settings_id'], vpg['vpg_name'], sync=False)
        
        print(f"Updated and committed settings for VPG: {vpg['vpg_name']}")

def main():
    parser = argparse.ArgumentParser(description="Update existing VPGs settings")
    parser.add_argument("--zvm_address", required=True, help="Site 1 ZVM address")
    parser.add_argument('--client_id', required=True, help='Site 1 Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Site 1 Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    args = parser.parse_args()

    try:
        # Setup client
        client = setup_client(args)
        
        # Get peer sites
        peer_sites = client.peersites.get_peer_sites()
        logging.debug(f"Peer sites: {peer_sites}")
        if not peer_sites:
            raise ValueError("No peer sites found")
        
        # Get the first peer site
        peer_site = peer_sites[0]
        peer_site_id = peer_site['SiteIdentifier']
        peer_site_name = peer_site.get('PeerSiteName')
        
        # Print resources and get mapping for peer site
        datastore_map, network_map = print_site_resources(client, peer_site_id, peer_site_name)
        
        # Get and print current VPG settings
        vpgs = client.vpgs.list_vpgs()
        vpg_settings = get_vpg_settings(client, vpgs)
        logging.debug(f"VPG settings: {json.dumps(vpg_settings, indent=4)}")
        
        # Get user input
        print("\nEnter sequential numbers for new settings:")
        ds_num = int(input("Datastore number: "))
        fo_net_num = int(input("Failover network number: "))
        test_net_num = int(input("Failover test network number: "))
        
        # Validate input
        if not all(num in datastore_map for num in [ds_num]) or \
           not all(num in network_map for num in [fo_net_num, test_net_num]):
            raise ValueError("Invalid sequential number entered")
        
        # Get actual IDs
        new_datastore = datastore_map[ds_num]
        new_failover_network = network_map[fo_net_num]
        new_test_network = network_map[test_net_num]
        
        # Confirm with user
        print(f"\nAbout to update all VPGs with:")
        print(f"New datastore: {new_datastore}")
        print(f"New failover network: {new_failover_network}")
        print(f"New test network: {new_test_network}")
        
        if input("\nContinue? (y/n): ").lower() != 'y':
            print("Operation cancelled")
            return
        
        # Update all VPGs
        update_vpg_settings(client, vpg_settings, new_datastore, new_failover_network, new_test_network)
        
        print("\nAll VPGs have been updated successfully")

    except Exception as e:
        logging.exception("Error occurred:")
        sys.exit(1)

if __name__ == "__main__":
    main() 