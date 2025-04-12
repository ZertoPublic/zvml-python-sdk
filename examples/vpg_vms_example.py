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
Zerto VPG VM Management Example Script

This script demonstrates how to manage Virtual Machines (VMs) within Virtual Protection Groups (VPGs)
using the Zerto Virtual Manager (ZVM) API. It showcases VPG creation, VM addition/removal, and cleanup.

Key Features:
1. Site Management:
   - Connect to protected site
   - Retrieve local and peer site identifiers
   - Manage cross-site replication using peer site information

2. VPG Operations:
   - Create multiple VPGs with custom settings
   - Add multiple VMs to a VPG
   - Remove VMs from VPGs
   - Move VMs between VPGs
   - Clean up resources

3. Resource Management:
   - Identify and select peer site datastores, hosts,  networks, folders and resource pools
   
Required Arguments:
    --zvm_address: Protected site ZVM address
    --client_id: Protected site Keycloak client ID
    --client_secret: Protected site Keycloak client secret
    --ignore_ssl: Ignore SSL certificate verification (optional)

Example Usage:
    python examples/vpg_vms_example.py \
        --zvm_address "192.168.111.20" \
        --client_id "zerto-api" \
        --client_secret "your-secret-here" \
        --ignore_ssl

Note: This script requires credentials only for the protected site. All recovery site information
is retrieved using the peer site API, eliminating the need for direct access to the recovery site.

Script Flow:
1. Connects to protected site ZVM
2. Gets local and peer site information
3. Creates first VPG 'VpgTest1'
4. Adds two VMs (vm1 and vm2) to first VPG
5. Removes vm1 from first VPG
6. Creates second VPG 'VpgTest2'
7. Adds removed VM (vm1) to second VPG
8. Cleans up by deleting both VPGs
"""

import logging
# Configure logging before any other imports or code
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

import argparse
import urllib3
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from zvml import ZVMLClient


# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def setup_clients(args):
    """
    Initialize and return Zerto clients and their local site identifiers for both sites
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        tuple: (client1, local_site1_id, local_peer_id)
    """
    # Create clients for both sites
    client = ZVMLClient(
        zvm_address=args.zvm_address,
        client_id=args.client_id,
        client_secret=args.client_secret,
        verify_certificate=not args.ignore_ssl
    )

    return client

def main():
    parser = argparse.ArgumentParser(description="zvml Client")
    parser.add_argument("--zvm_address", required=True, help="Site 1 ZVM address")
    parser.add_argument('--client_id', required=True, help='Site 1 Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Site 1 Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    parser.add_argument("--vm1", required=True, help="Name of first VM to protect")
    parser.add_argument("--vm2", required=True, help="Name of second VM to protect")
    args = parser.parse_args()

    try:
        # Setup clients and get site identifiers
        client1 = setup_clients(args)

        virtualization_sites = client1.virtualization_sites.get_virtualization_sites()
        logging.debug(f"Virtualization Sites: {json.dumps(virtualization_sites, indent=4)}")

        # Get local site ids
        local_site_identifier = client1.localsite.get_local_site().get('SiteIdentifier')
        logging.info(f"Site 1 Local Site ID: {local_site_identifier}")

        peer_site_identifier = next((site['SiteIdentifier'] for site in virtualization_sites if site['SiteIdentifier'] != local_site_identifier), None)
        logging.info(f"Site 2 Local Site ID: {peer_site_identifier}")

        # Get datastore identifier from site 2
        peer_datastores = client1.virtualization_sites.get_virtualization_site_datastores(
            site_identifier=peer_site_identifier
        )
        logging.debug(f"Site 2 Datastores: {json.dumps(peer_datastores, indent=4)}")

        selected_datastore = next((ds for ds in peer_datastores if ds.get('DatastoreName') == "DS_VM_Right"), None)
        peer_datastore_identifier = selected_datastore.get('DatastoreIdentifier')
        logging.info(f"Site 2 Datastore ID: {peer_datastore_identifier}")

        # Fill basic VPG settings info
        vpg_name = 'VpgTest1'
        basic = {
            "Name": vpg_name,
            "VpgType": "Remote",
            "RpoInSeconds": 300,
            "JournalHistoryInHours": 1,
            "Priority": "Medium",
            "UseWanCompression": True,
            "ProtectedSiteIdentifier": local_site_identifier,
            "RecoverySiteIdentifier": peer_site_identifier
        }
        # Fill journal structure
        journal = {
            "DatastoreIdentifier": peer_datastore_identifier,
            "Limitation": {
                "HardLimitInMB": 153600,
                "WarningThresholdInMB": 115200
            }
        }

        resource_pools = client1.virtualization_sites.get_virtualization_site_resource_pools(
            site_identifier=peer_site_identifier
        )
        logging.debug(f"Resource Pools: {json.dumps(resource_pools, indent=4)}")

        # Extract resource pool identifier from the first resource pool on the list
        if resource_pools:
            resource_pool_identifier = resource_pools[0].get('Identifier')
            logging.info(f"Resource Pool Identifier from the first resource pool: {resource_pool_identifier}")
        else:
            logging.error("No resource pools found on site 2.")
            return

        # List networks from peer site
        networks_list = client1.virtualization_sites.get_virtualization_site_networks(
            site_identifier=peer_site_identifier
        )
        logging.debug(f"Networks: {json.dumps(networks_list, indent=4)}")

        # Extract network identifier from the first network on the list
        if networks_list:
            network_identifier = networks_list[0].get('NetworkIdentifier')
            logging.info(f"Network Identifier from the first network: {network_identifier}")
        else:
            logging.error("No networks found on site 2.")
            return
        
        #list folders from peer     
        folders = client1.virtualization_sites.get_virtualization_site_folders(
            site_identifier=peer_site_identifier
        )
        logging.debug(f"Site 2 Folders: {json.dumps(folders, indent=4)}")

        for folder in folders:
            if folder.get('FolderName') == '/':
                peer_folder_identifier = folder.get('FolderIdentifier')
                logging.info(f"Folder Identifier: {peer_folder_identifier}")
                break

        peer_hosts = client1.virtualization_sites.get_virtualization_site_hosts(
            site_identifier=peer_site_identifier
        )
        logging.debug(f"Site 2 Hosts: {json.dumps(peer_hosts, indent=4)}")  

        # get the second host from the list
        peer_site_host_identifier = peer_hosts[1].get('HostIdentifier')
        logging.info(f"Host Identifier from the second host: {peer_site_host_identifier}")

        # Fill recovery structure
        recovery = {
            "DefaultHostIdentifier": peer_site_host_identifier,
            "DefaultDatastoreIdentifier": peer_datastore_identifier,
            "DefaultResourcePoolIdentifier": resource_pool_identifier,
            "DefaultFolderIdentifier": peer_folder_identifier
        }

        # Fill Networks structure
        networks = {
            "Failover": {
                "Hypervisor": {
                "DefaultNetworkIdentifier": network_identifier
                }
            },
            "FailoverTest": {
                "Hypervisor": {
                "DefaultNetworkIdentifier": network_identifier
                }
            }
        }
        
        input("Press Enter to create the first VPG...")

        vpg_id = client1.vpgs.create_vpg(basic=basic, journal=journal, 
                                         recovery=recovery, networks=networks, sync=True)
        logging.info(f"VPG ID: {vpg_id} created successfully.")

        # Add VMs to the first VPG
        vms = client1.virtualization_sites.get_virtualization_site_vms(
            site_identifier=local_site_identifier
        )
        logging.debug(f"Site 1 VMs: {json.dumps(vms, indent=4)}")

        vms_to_add = [args.vm1, args.vm2]
        vm_list = []
        for vm in vms:
            logging.info(f"VM: Name={vm.get('VmName')}, VM Identifier={vm.get('VmIdentifier')}")
            if vm.get('VmName') in vms_to_add:
                logging.info(f"Adding VM {vm.get('VmName')} to VPG...")
                vm_payload = {
                    "VmIdentifier": vm.get('VmIdentifier'),
                    "Recovery": {
                        "HostIdentifier": peer_site_host_identifier,
                        "DatastoreIdentifier": peer_datastore_identifier,
                        "FolderIdentifier": peer_folder_identifier
                    }
                }
                vm_list.append(vm_payload)
                task_id = client1.vpgs.add_vm_to_vpg(vpg_name, vm_list_payload=vm_payload)
                logging.info(f"Task ID: {task_id} to add VM {vm.get('VmName')} to VPG.")

        input(f"Press Enter to remove {args.vm1} VM from the first VPG...")

        # Remove first VM from the first VPG
        vm_to_remove = args.vm1
        vm_identifier_to_remove = None
        for vm in vms:
            if vm.get('VmName') == vm_to_remove:
                vm_identifier_to_remove = vm.get('VmIdentifier')
                task_id = client1.vpgs.remove_vm_from_vpg(vpg_name, vm_identifier_to_remove)
                logging.info(f"Task ID: {task_id} to remove VM {vm_to_remove} from VPG {vpg_name}")
                break

        input("Press Enter to create second VPG...")

        # Create second VPG
        vpg_name_2 = 'VpgTest2'
        basic['Name'] = vpg_name_2  # Update VPG name for second VPG
        
        vpg_id_2 = client1.vpgs.create_vpg(basic=basic, journal=journal, 
                                          recovery=recovery, networks=networks, sync=True)
        logging.info(f"Second VPG ID: {vpg_id_2} created successfully.")

        # Add the removed VM to the second VPG
        if vm_identifier_to_remove:
            vm_payload = {
                "VmIdentifier": vm_identifier_to_remove,
                "Recovery": {
                    "HostIdentifier": peer_site_host_identifier,
                    "DatastoreIdentifier": peer_datastore_identifier,
                    "FolderIdentifier": peer_folder_identifier
                }
            }
            task_id = client1.vpgs.add_vm_to_vpg(vpg_name_2, vm_list_payload=vm_payload)
            logging.info(f"Task ID: {task_id} to add VM {vm_to_remove} to VPG {vpg_name_2}")

    except Exception as e:
        logging.exception("Error:")
        logging.error(f"Error: {e}")


    # wait for user input to continue
    input("Press Enter to delete the VPGs...")

    # Delete the VPGs
    client1.vpgs.delete_vpg(vpg_name, force=True, keep_recovery_volumes=False)
    logging.info(f"VPG {vpg_name} deleted successfully.")   
    client1.vpgs.delete_vpg(vpg_name_2, force=True, keep_recovery_volumes=False)
    logging.info(f"VPG {vpg_name_2} deleted successfully.")

if __name__ == "__main__":
    main()