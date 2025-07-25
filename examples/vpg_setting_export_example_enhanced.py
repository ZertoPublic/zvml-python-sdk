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
Zerto VPG Settings Export/Import Example Script 

This script demonstrates how to export and import Virtual Protection Group (VPG) settings
using the Zerto Virtual Manager (ZVM) API. It allows for backup and restoration of VPG
configurations, which is useful for disaster recovery planning and VPG replication.

Key Features:
1. Export Selection:
   - List all available exports with timestamps and status
   - Display VPGs in each export with source and target sites
   - Compare requested VPGs with available ones in the export
   - Allow user to select which export to use

2. Resource Validation:
   - Check and validate datastores, hosts, folders, and networks
   - Allow user to select replacements for missing resources
   - Handle both VPG-level and VM-level resource mappings
   - Support for journal, scratch, and recovery settings

3. Settings Import:
   - Import validated settings back to create new VPGs
   - Display detailed import results including:
     - Validation failures with error messages
     - Import failures with specific errors
     - Successfully initiated imports with task IDs
   - Allow user to verify changes before proceeding

Required Arguments:
    --zvm_address: Protected site ZVM address
    --client_id: Protected site Keycloak client ID
    --client_secret: Protected site Keycloak client secret
    --ignore_ssl: Ignore SSL certificate verification (optional)
    --vpg_names: Comma-separated list of VPG names to process (optional)

Example Usage:
    python examples/vpg_setting_export_example_enhanced.py \
        --zvm_address "192.168.111.20" \
        --client_id "zerto-api" \
        --client_secret "your-secret-here" \
        --vpg_names "VpgTest1,VpgTest2" \
        --ignore_ssl

Script Flow:
1. Connect to protected site ZVM
2. List available exports and let user select one
3. Display VPGs in selected export and compare with requested ones
4. Get peer site resources (datastores, hosts, folders, networks)
5. Validate and update resource mappings:
   - VPG-level settings (journal, scratch, recovery)
   - VM-level settings (host, datastore, folder, network)
6. Save updated settings to file
7. Allow user to verify changes
8. Import settings to recreate VPGs
9. Display import results with task IDs

Note: This script requires only protected site credentials. It's designed for VPG
configuration backup and restore scenarios, allowing you to quickly recreate VPGs
with identical settings after changes or in disaster recovery situations.
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
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from zvml import ZVMLClient
from typing import List, Dict

# Disable SSL warningss
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

def select_resource(resource_type: str, resources: List[Dict]) -> str:
    """Let user select a resource from available options
    
    Args:
        resource_type: Type of resource (datastore, host, folder)
        resources: List of available resources
        
    Returns:
        str: Selected resource identifier or None if skipped
    """
    print(f"\nAvailable {resource_type}s:")
    for i, resource in enumerate(resources, 1):
        if resource_type == "datastore":
            name = resource.get('DatastoreName', 'Unknown')
            id_key = 'DatastoreIdentifier'
        elif resource_type == "host":
            name = resource.get('VirtualizationHostName', 'Unknown')
            id_key = 'HostIdentifier'
        elif resource_type == "folder":
            name = resource.get('FolderName', 'Unknown')
            id_key = 'FolderIdentifier'
        else:
            name = 'Unknown'
            id_key = 'Identifier'
            
        print(f"{i}. {name} (ID: {resource.get(id_key, 'Unknown')})")
    
    while True:
        try:
            selection = input(f"\nSelect a {resource_type} number to replace the missing one(or 'q' to skip): ")
            if selection.lower() == 'q':
                return None
            
            selection = int(selection)
            if 1 <= selection <= len(resources):
                return resources[selection - 1]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number or 'q' to skip.")

def check_vpg_datastore(datastore_id: str, available_datastores: List[Dict]) -> str:
    """Check if a datastore ID exists in the available datastores list.
    If not found, ask user to select a replacement.
    
    Args:
        datastore_id: The datastore identifier to check
        available_datastores: List of available datastores from the peer site
        
    Returns:
        str: Original datastore ID if found, or selected replacement datastore ID
    """
    if not datastore_id:
        return None
        
    if any(ds['DatastoreIdentifier'] == datastore_id for ds in available_datastores):
        return datastore_id
        
    # If not found, ask user to select a replacement
    logging.warning(f"Datastore {datastore_id} not found in peer site")
    return select_resource("datastore", available_datastores)

def check_vpg_host(host_id: str, available_hosts: List[Dict]) -> str:
    """Check if a host ID exists in the available hosts list.
    If not found, ask user to select a replacement.
    
    Args:
        host_id: The host identifier to check
        available_hosts: List of available hosts from the peer site
        
    Returns:
        str: Original host ID if found, or selected replacement host ID
    """
    if not host_id:
        return None
        
    if any(host['HostIdentifier'] == host_id for host in available_hosts):
        return host_id
        
    # If not found, ask user to select a replacement
    logging.warning(f"Host {host_id} not found in peer site")
    return select_resource("host", available_hosts)

def check_vpg_folder(folder_id: str, available_folders: List[Dict]) -> str:
    """Check if a folder ID exists in the available folders list.
    If not found, ask user to select a replacement.
    
    Args:
        folder_id: The folder identifier to check
        available_folders: List of available folders from the peer site
        
    Returns:
        str: Original folder ID if found, or selected replacement folder ID
    """
    if not folder_id:
        return None
        
    if any(folder['FolderIdentifier'] == folder_id for folder in available_folders):
        return folder_id
        
    # If not found, ask user to select a replacement
    logging.warning(f"Folder {folder_id} not found in peer site")
    return select_resource("folder", available_folders).get('FolderIdentifier')

def check_vpg_network(network_id: str, available_networks: List[Dict]) -> str:
    """Check if a network ID exists in the available networks list.
    If not found, ask user to select a replacement.
    
    Args:
        network_id: The network identifier to check
        available_networks: List of available networks from the peer site
        
    Returns:
        str: Original network ID if found, or selected replacement network ID
    """
    if not network_id:
        return None
        
    if any(net['NetworkIdentifier'] == network_id for net in available_networks):
        return network_id
        
    # If not found, ask user to select a replacement
    logging.warning(f"Network {network_id} not found in peer site")
    return select_resource("network", available_networks).get('NetworkIdentifier')

def main():
    parser = argparse.ArgumentParser(description="Export and Import VPG settings example")
    parser.add_argument("--zvm_address", required=True, help="Site 1 ZVM address")
    parser.add_argument('--client_id', required=True, help='Site 1 Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Site 1 Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    parser.add_argument("--vpg_names", required=True, help="Comma-separated list of VPG names to process")
    args = parser.parse_args()

    try:
        # Setup client
        client = setup_client(args)

        # Split the comma-separated string and strip whitespace
        vpg_names = [name.strip() for name in args.vpg_names.split(',')]
        logging.info(f"Processing VPGs: {vpg_names}")

        # Export selection loop
        while True:
            # List all available exports
            print("\nAvailable exports:")
            exports = client.vpgs.list_exported_vpg_settings()
            if not exports:
                logging.error("No exports found")
                sys.exit(1)

            # Display available exports
            for i, export in enumerate(exports, 1):
                print(f"{i}. Timestamp: {export.get('TimeStamp')}")
                print(f"   Status: {export.get('Status')}")
                print()

            # Let user select an export
            while True:
                try:
                    selection = input("\nSelect an export number to use (or 'q' to quit): ")
                    if selection.lower() == 'q':
                        logging.info("User chose to quit")
                        sys.exit(0)
                    
                    selection = int(selection)
                    if 1 <= selection <= len(exports):
                        selected_export = exports[selection - 1]
                        break
                    else:
                        print("Invalid selection. Please try again.")
                except ValueError:
                    print("Please enter a valid number or 'q' to quit.")

            # Get VPGs from selected export
            print("\nVPGs in selected export:")
            export_vpgs = client.vpgs.list_vpgs_from_exported_settings(selected_export['TimeStamp'])
            for vpg in export_vpgs:
                print(f"- {vpg['VpgName']} (Source: {vpg['SourceSiteName']}, Target: {vpg['TargetSiteName']})")

            # Compare with requested VPGs if specified
            if vpg_names:
                missing_vpgs = [name for name in vpg_names if name not in [vpg['VpgName'] for vpg in export_vpgs]]
                if missing_vpgs:
                    print(f"\nWarning: The following requested VPGs are not in the selected export:")
                    for vpg in missing_vpgs:
                        print(f"- {vpg}")
                    print("\nYou can either:")
                    print("1. Select a different export")
                    print("2. Continue with the available VPGs")
                    print("3. Quit")
                    
                    choice = input("\nEnter your choice (1/2/3): ")
                    if choice == '1':
                        continue  # Restart the export selection loop
                    elif choice == '3':
                        logging.info("User chose to quit")
                        sys.exit(0)
                    # If choice is 2, continue with available VPGs

            # Ask for confirmation to proceed
            confirm = input("\nDo you want to proceed with this export? (y/n): ")
            if confirm.lower() != 'y':
                logging.info("User chose not to proceed")
                sys.exit(0)
            break  # Exit the export selection loop if confirmed

        # Get the selected export settings
        export_settings = client.vpgs.read_exported_vpg_settings(selected_export['TimeStamp'], vpg_names)
        
        # Save the selected export to a file
        file_name = f"{selected_export['TimeStamp']}-original-exported-vpg-settings.json"
        with open(file_name, 'w') as f:
            json.dump(export_settings, f, indent=2)
        print(f"\nSelected export saved to: {file_name}")

        # Get peer site resources
        virtualization_sites = client.virtualization_sites.get_virtualization_sites()
        logging.debug(f"Virtualization Sites: {json.dumps(virtualization_sites, indent=4)}")

        # Get local site ids
        local_site_identifier = client.localsite.get_local_site().get('SiteIdentifier')
        logging.info(f"Local Site ID: {local_site_identifier}")

        peer_site_identifier = next((site['SiteIdentifier'] for site in virtualization_sites if site['SiteIdentifier'] != local_site_identifier), None)
        logging.info(f"Peer Site ID: {peer_site_identifier}")

        # Get peer site resources
        peer_datastores = client.virtualization_sites.get_virtualization_site_datastores(
            site_identifier=peer_site_identifier
        )
        logging.info(f"Peer Datastores: {json.dumps(peer_datastores, indent=4)}")

        peer_hosts = client.virtualization_sites.get_virtualization_site_hosts(
            site_identifier=peer_site_identifier
        )
        logging.info(f"Peer Hosts: {json.dumps(peer_hosts, indent=4)}")

        peer_folders = client.virtualization_sites.get_virtualization_site_folders(
            site_identifier=peer_site_identifier
        )
        logging.info(f"Peer Folders: {json.dumps(peer_folders, indent=4)}")

        peer_networks = client.virtualization_sites.get_virtualization_site_networks(
            site_identifier=peer_site_identifier
        )
        logging.info(f"Peer Networks: {json.dumps(peer_networks, indent=4)}")

        # Process each VPG
        for vpg in export_settings['ExportedVpgSettingsApi']:
            vpg_name = vpg['Basic']['Name']
            logging.info(f"\nProcessing VPG: {vpg_name}")
            
            # Check journal datastore
            journal_ds = vpg['Journal'].get('DatastoreIdentifier')
            new_ds = check_vpg_datastore(journal_ds, peer_datastores)
            if new_ds:
                vpg['Journal']['DatastoreIdentifier'] = new_ds
            
            # Check scratch datastore
            scratch_ds = vpg['Scratch'].get('DatastoreIdentifier')
            new_ds = check_vpg_datastore(scratch_ds, peer_datastores)
            if new_ds:
                vpg['Scratch']['DatastoreIdentifier'] = new_ds
            
            # Check recovery settings
            recovery = vpg['Recovery']
            new_host = check_vpg_host(recovery['DefaultHostIdentifier'], peer_hosts)
            if new_host:
                recovery['DefaultHostIdentifier'] = new_host
            
            new_ds = check_vpg_datastore(recovery['DefaultDatastoreIdentifier'], peer_datastores)
            if new_ds:
                recovery['DefaultDatastoreIdentifier'] = new_ds
            
            new_folder = check_vpg_folder(recovery['DefaultFolderIdentifier'], peer_folders)
            if new_folder:
                recovery['DefaultFolderIdentifier'] = new_folder
            
            # Check VPG-level network settings
            networks = vpg['Networks']
            # Check failover network
            failover_net = networks['Failover']['Hypervisor'].get('DefaultNetworkIdentifier')
            new_net = check_vpg_network(failover_net, peer_networks)
            if new_net:
                networks['Failover']['Hypervisor']['DefaultNetworkIdentifier'] = new_net
            
            # Check failover test network
            failover_test_net = networks['FailoverTest']['Hypervisor'].get('DefaultNetworkIdentifier')
            new_net = check_vpg_network(failover_test_net, peer_networks)
            if new_net:
                networks['FailoverTest']['Hypervisor']['DefaultNetworkIdentifier'] = new_net
            
            # Check VM-specific settings
            for vm in vpg.get('Vms', []):
                vm_recovery = vm['Recovery']
                new_host = check_vpg_host(vm_recovery['HostIdentifier'], peer_hosts)
                if new_host:
                    vm_recovery['HostIdentifier'] = new_host
                
                new_ds = check_vpg_datastore(vm_recovery['DatastoreIdentifier'], peer_datastores)
                if new_ds:
                    vm_recovery['DatastoreIdentifier'] = new_ds
                
                new_folder = check_vpg_folder(vm_recovery['FolderIdentifier'], peer_folders)
                if new_folder:
                    vm_recovery['FolderIdentifier'] = new_folder
                
                # Check VM journal datastore
                vm_journal_ds = vm['Journal'].get('DatastoreIdentifier')
                new_ds = check_vpg_datastore(vm_journal_ds, peer_datastores)
                if new_ds:
                    vm['Journal']['DatastoreIdentifier'] = new_ds
                
                # Check VM scratch datastore
                vm_scratch_ds = vm['Scratch'].get('DatastoreIdentifier')
                new_ds = check_vpg_datastore(vm_scratch_ds, peer_datastores)
                if new_ds:
                    vm['Scratch']['DatastoreIdentifier'] = new_ds

                # Check VM network settings
                for nic in vm.get('Nics', []):
                    # Check failover network
                    failover_net = nic['Failover']['Hypervisor'].get('NetworkIdentifier')
                    new_net = check_vpg_network(failover_net, peer_networks)
                    if new_net:
                        nic['Failover']['Hypervisor']['NetworkIdentifier'] = new_net
                    
                    # Check failover test network
                    failover_test_net = nic['FailoverTest']['Hypervisor'].get('NetworkIdentifier')
                    new_net = check_vpg_network(failover_test_net, peer_networks)
                    if new_net:
                        nic['FailoverTest']['Hypervisor']['NetworkIdentifier'] = new_net
        
        # Save updated settings
        updated_file_name = f"{selected_export['TimeStamp']}-updated-exported-vpg-settings.json"
        with open(updated_file_name, 'w') as f:
            json.dump(export_settings, f, indent=2)
        logging.info(f"\nUpdated settings saved to: {updated_file_name}")

        # ask users if they want to import the settings back
        # print the name of the original file and the updated file and ask to confirm the changes where compared
        print(f"\nOriginal file: {file_name}")
        print(f"Updated file: {updated_file_name}")
        print(f"Please compare those file and confirm the changes where done correctly")
        input("\nPress Enter when you done comparing the files to continue...")

        import_settings = input("\nDo you want to import the settings back? (y/n): ")
        if import_settings.lower() != 'y':
            logging.info("User did not confirm the changes, exiting the script")
            sys.exit(1)

        #pause
        input(f"\nNow you can delete the selected VPGs [{vpg_names}] and then press Enter to continue...")

        # Step 3: Import the settings back
        print("\nStep 3: Importing VPG settings...")
        import_result = client.vpgs.import_vpg_settings(export_settings)
        print("\nImport Result:")
        
        # Display validation failures
        if import_result.get('ValidationFailedResults'):
            print("\nValidation Failed:")
            for failure in import_result['ValidationFailedResults']:
                print(f"- VPG: {failure['VpgName']}")
                for error in failure['ErrorMessages']:
                    print(f"  Error: {error}")
        
        # Display import failures
        if import_result.get('ImportFailedResults'):
            print("\nImport Failed:")
            for failure in import_result['ImportFailedResults']:
                print(f"- VPG: {failure['VpgName']}")
                print(f"  Error: {failure['ErrorMessage']}")
        
        # Display successful imports
        if import_result.get('ImportTaskIdentifiers'):
            print("\nSuccessfully Initiated Imports:")
            for task in import_result['ImportTaskIdentifiers']:
                print(f"- VPG: {task['VpgName']}")
                print(f"  Task ID: {task['TaskIdentifier']}")
        
        #pause
        input("\nLook at the VPGs and verify whether the manual changes are reverted back to the original settings. Press Enter to exit")

    except Exception as e:
        logging.exception("Error occurred:")
        sys.exit(1)

if __name__ == "__main__":
    main() 