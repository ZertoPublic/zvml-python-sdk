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
Zerto VPG Failover Example Script

This script demonstrates how to perform parallel failover tests for multiple Virtual Protection Groups (VPGs)
using the Zerto Virtual Manager (ZVM) API. It showcases complete VPG lifecycle management from creation
to testing and cleanup.

Key Features:
1. Site Management:
   - Connect to protected site
   - Retrieve local and peer site identifiers
   - Manage cross-site replication using peer site information

2. VPG Operations:
   - Create multiple VPGs with custom settings
   - Add VMs to VPGs
   - Monitor initial synchronization
   - Create checkpoints
   - Run parallel failover tests
   - Generate test reports
   - Clean up resources

3. Resource Management:
   - Identify and select peer site datastores
   - Configure peer site hosts and networks
   - Set up peer site resource pools
   - Manage VM folders
   - Monitor volume replication

Required Arguments:
    --zvm_address: Protected site ZVM address
    --client_id: Protected site Keycloak client ID
    --client_secret: Protected site Keycloak client secret
    --ignore_ssl: Ignore SSL certificate verification (optional)

Example Usage:
    python examples/vpg_failover_example.py \
        --zvm_address "192.168.111.20" \
        --client_id "zerto-api" \
        --client_secret "your-secret-here" \
        --ignore_ssl

Note: This script requires credentials only for the protected site. All recovery site information
is retrieved using the peer site API, eliminating the need for direct access to the recovery site.
Resource identifiers and configuration details for both sites are managed through the protected
site's ZVM API.

Script Flow:
1. Connects to protected site ZVM
2. Gets local and peer site information
3. Creates two VPGs in parallel:
   - VpgTest1 protecting VM 'SmallCentOS'
   - VpgTest2 protecting VM 'light-vm1'
4. Waits for both VPGs to reach MeetingSLA status
5. Performs parallel failover tests
6. Waits for user confirmation to stop tests
7. Stops failover tests in parallel
8. Generates test reports
9. Cleans up by deleting both VPGs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import logging
import urllib3
import json
from zvml import ZVMLClient
import time
from zvml.common import ZertoVPGStatus, ZertoVPGSubstatus
from zvml.recovery_reports import RecoveryReports
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#name sure the api client lifespan settion is complete the initial sync, in my case I set it to 3600 seconds

def setup_clients(args):
    """
    Initialize and return Zerto clients and their local site identifiers for both sites
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        tuple: (zvm_client, client2, local_site1_id, local_site2_id)
    """
    # Create clients for both sites
    zvm_client = ZVMLClient(
        zvm_address=args.zvm_address,
        client_id=args.client_id,
        client_secret=args.client_secret,
        verify_certificate=not args.ignore_ssl
    )
    
    #get all virtualization sites
    virtualization_sites = zvm_client.virtualization_sites.get_virtualization_sites()
    logging.info(f"Virtualization Sites: {json.dumps(virtualization_sites, indent=4)}")

    # Get local site ids
    local_site_identifier = zvm_client.localsite.get_local_site().get('SiteIdentifier')
    logging.info(f"Site 1 Local Site ID: {local_site_identifier}")

    #peer_site_identifier is site in the list that is not the local site
    peer_site_identifier = next((site['SiteIdentifier'] for site in virtualization_sites if site['SiteIdentifier'] != local_site_identifier), None)
    logging.info(f"Site 2 Local Site ID: {peer_site_identifier}")
    
    return zvm_client, local_site_identifier, peer_site_identifier

def construct_vpg_settings(vpg_name, local_site_identifier, peer_site_identifier, site2_datastore_identifier,
                           site2_host_identifier, resource_pool_identifier, site2_folder_identifier, site2_network_identifier):
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
        "DatastoreIdentifier": site2_datastore_identifier,
        "Limitation": {
            "HardLimitInMB": 153600,
            "WarningThresholdInMB": 115200
        }
    }

    # Fill recovery structure
    recovery = {  
            "DefaultHostIdentifier": site2_host_identifier,
            "DefaultDatastoreIdentifier": site2_datastore_identifier,
            "DefaultResourcePoolIdentifier": resource_pool_identifier,
            "DefaultFolderIdentifier": site2_folder_identifier
    }

     # Fill Networks structure
    networks = {
            "Failover": {
                "Hypervisor": {
                "DefaultNetworkIdentifier": site2_network_identifier
                }
            },
            "FailoverTest": {
                "Hypervisor": {
                "DefaultNetworkIdentifier": site2_network_identifier
                }
            }
    }

    return basic, journal, recovery, networks

def perform_failover_test(client, vpg_name):
    """Execute failover test for a single VPG and get its report"""
    try:
        task_id = client.vpgs.failover_test(vpg_name)
        logging.info(f"Failover test started for VPG {vpg_name}, task ID: {task_id}")
        
        # Wait for task completion
        client.tasks.wait_for_task_completion(task_id)
        
        # Get the latest failover test report
        latest_report = client.recovery_reports.get_latest_failover_test_report(vpg_name)
        if latest_report:
            logging.info(f"Failover test completed for VPG {vpg_name}")
            return vpg_name, latest_report
        return vpg_name, None
    except Exception as e:
        logging.error(f"Error in failover test for VPG {vpg_name}: {e}")
        raise

def run_parallel_failover_tests(client, vpg_names):
    """Run failover tests in parallel for multiple VPGs"""
    logging.info(f"Starting parallel failover tests for VPGs: {vpg_names}")
    
    with ThreadPoolExecutor(max_workers=len(vpg_names)) as executor:
        # Submit all failover tasks
        future_to_vpg = {
            executor.submit(perform_failover_test, client, vpg_name): vpg_name 
            for vpg_name in vpg_names
        }
        
        # Wait for all tasks to complete and collect results
        results = {}
        for future in as_completed(future_to_vpg):
            vpg_name = future_to_vpg[future]
            try:
                vpg_name, report = future.result()
                results[vpg_name] = report
                logging.info(f"Completed failover test for VPG {vpg_name}")
            except Exception as e:
                logging.error(f"Failover test failed for VPG {vpg_name}: {e}")
                results[vpg_name] = None
    
    return results

def main():
    parser = argparse.ArgumentParser(description="zvml Client")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument('--client_id', required=True, help='Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Keycloak client secret')
    # parser.add_argument("--site2_address", required=True, help="Site 2 ZVM address")
    # parser.add_argument('--site2_client_id', required=True, help='Site 2 Keycloak client ID')
    # parser.add_argument('--site2_client_secret', required=True, help='Site 2 Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    try:
        vpg_structure = [
            {
                'vpg_name': 'VpgTest1',
                'vm_name': 'SmallCentOS'
            },
            {
                'vpg_name': 'VpgTest2',
                'vm_name': 'light-vm1'
            }
        ]
        
        # Setup clients and get site identifiers
        zvm_client, local_site_identifier, peer_site_identifier = setup_clients(args)

        # Get datastore identifier from site 2 using ZVM API
        site2_datastores = zvm_client.virtualization_sites.get_virtualization_site_datastores(
            site_identifier=peer_site_identifier
        )
        selected_datastore = next((ds for ds in site2_datastores if ds.get('DatastoreName') == "DS_VM_Right"), None)
        site2_datastore_identifier = selected_datastore.get('DatastoreIdentifier')
        logging.info(f"Site 2 Datastore ID: {site2_datastore_identifier}")

        # Get host identifier from site 2 using ZVM API
        site2_hosts = zvm_client.virtualization_sites.get_virtualization_site_hosts(
            site_identifier=peer_site_identifier
        )
        # logging.info(f"Site 2 Hosts: {site2_hosts}")
        # Get the first host from the list
        selected_host = site2_hosts[0]
        site2_host_identifier = selected_host.get('HostIdentifier')
        # logging.info(f"Site 2 Host ID: {site2_host_identifier}")

        # Get resource pools from site 2 using ZVM API
        resource_pools = zvm_client.virtualization_sites.get_virtualization_site_resource_pools(
            site_identifier=peer_site_identifier
        )
        if resource_pools:
            resource_pool_identifier = resource_pools[0].get('ResourcePoolIdentifier')
            logging.info(f"Resource Pool ID: {resource_pool_identifier}")
        else:
            logging.error("No resource pools found on site 2.")
            return

        # Get networks from site 2 using ZVM API
        networks = zvm_client.virtualization_sites.get_virtualization_site_networks(
            site_identifier=peer_site_identifier
        )
        if networks:
            site2_network_identifier = networks[0].get('NetworkIdentifier')
            logging.info(f"Network ID: {site2_network_identifier}")
        else:
            logging.error("No networks found on site 2.")
            return

        # Get folders from site 2 using ZVM API
        folders = zvm_client.virtualization_sites.get_virtualization_site_folders(
            site_identifier=peer_site_identifier
        )
        for folder in folders:
            if folder.get('FolderName') == '/':
                site2_folder_identifier = folder.get('FolderIdentifier')
                logging.info(f"Folder ID: {site2_folder_identifier}")
                break

        # Get VMs from site 1 using ZVM API
        site_1_vms = zvm_client.virtualization_sites.get_virtualization_site_vms(
            site_identifier=local_site_identifier
        )
        logging.info(f"Found {len(site_1_vms)} VMs on site 1")
        
        def create_vpg_with_vm(vpg_config):
            """Create a VPG and add a VM to it"""
            try:
                vpg_name = vpg_config['vpg_name']
                vm_name = vpg_config['vm_name']
                
                # Create VPG settings
                basic, journal, recovery, networks = construct_vpg_settings(
                    vpg_name, local_site_identifier, peer_site_identifier,
                    site2_datastore_identifier, site2_host_identifier,
                    resource_pool_identifier, site2_folder_identifier, site2_network_identifier
                )

                # Create VPG
                vpg_id = zvm_client.vpgs.create_vpg(
                    basic=basic, journal=journal, recovery=recovery, networks=networks, sync=True
                )
                logging.info(f"VPG {vpg_name} created successfully with ID: {vpg_id}")

                # Find and add VM to VPG
                vm = next((vm for vm in site_1_vms if vm.get('VmName') == vm_name), None)
                if vm:
                    vm_payload = {
                        "VmIdentifier": vm.get('VmIdentifier'),
                        "Recovery": {
                            "HostIdentifier": site2_host_identifier,
                            "DatastoreIdentifier": site2_datastore_identifier,
                            "FolderIdentifier": site2_folder_identifier
                        }
                    }
                    task_id = zvm_client.vpgs.add_vm_to_vpg(vpg_name, vm_list_payload=vm_payload)
                    logging.info(f"Task ID: {task_id} to add VM {vm_name} to VPG {vpg_name}")
                    return vpg_name, vpg_id
                else:
                    logging.error(f"VM {vm_name} not found")
                    return vpg_name, None
            except Exception as e:
                logging.error(f"Error creating VPG {vpg_name}: {e}")
                return vpg_name, None

        # Create VPGs in parallel
        with ThreadPoolExecutor(max_workers=len(vpg_structure)) as executor:
            # Submit all VPG creation tasks
            future_to_vpg = {
                executor.submit(create_vpg_with_vm, vpg_config): vpg_config
                for vpg_config in vpg_structure
            }
            
            # Wait for all tasks to complete
            created_vpgs = []
            for future in as_completed(future_to_vpg):
                vpg_name, vpg_id = future.result()
                if vpg_id:
                    created_vpgs.append(vpg_name)
                    logging.info(f"Successfully created VPG {vpg_name}")

        # Wait for all VPGs to reach MeetingSLA status
        if created_vpgs:
            logging.info("Waiting for VPGs to reach MeetingSLA status...")
            while True:
                all_vpgs_ready = True
                for vpg_name in created_vpgs:
                    vpg_info = zvm_client.vpgs.list_vpgs(vpg_name=vpg_name)
                    status = vpg_info.get('Status')
                    substatus = vpg_info.get('SubStatus')
                    logging.info(f"VPG {vpg_name} - Status: {ZertoVPGStatus.get_name_by_value(status)}, "
                               f"SubStatus: {ZertoVPGSubstatus.get_name_by_value(substatus)}")
                    
                    if not ((status == ZertoVPGStatus.MeetingSLA.value and 
                            (substatus == ZertoVPGSubstatus.Sync.value or substatus == ZertoVPGSubstatus.NONE.value)) or 
                           (status == ZertoVPGStatus.HistoryNotMeetingSLA.value)):
                        all_vpgs_ready = False
                        break

                if all_vpgs_ready:
                    logging.info("All VPGs are now meeting SLA")
                    break

                logging.info("Waiting for VPGs to reach MeetingSLA status...")
                time.sleep(30)  # Wait 30 seconds before checking again

        input("Press Enter to start parallel failover tests for both VPGs...")
        
        # Run parallel failover tests
        failover_results = run_parallel_failover_tests(zvm_client, created_vpgs)
        logging.info(f"Failover results: {json.dumps(failover_results, indent=4)}")
        
        input("Press Enter to stop failover tests and rollback both VPGs...")
        
        # Stop failover tests in parallel
        with ThreadPoolExecutor(max_workers=len(created_vpgs)) as executor:
            futures = [
                executor.submit(zvm_client.vpgs.stop_failover_test, vpg_name)
                for vpg_name in created_vpgs
            ]
            for future in as_completed(futures):
                try:
                    task_id = future.result()
                    logging.info(f"Failover test stop initiated, task ID: {task_id}")
                except Exception as e:
                    logging.error(f"Error stopping failover test: {e}")

        # After running failover tests
        for vpg_name in created_vpgs:
            # Get the latest failover test report
            latest_report = zvm_client.recovery_reports.get_latest_failover_test_report(vpg_name)
            if latest_report:
                logging.info(f"Failover test report for {vpg_name} latest_report=:{json.dumps(latest_report, indent=4)}")

        input("Press Enter to delete both VPGs...")

        # Delete both VPGs
        zvm_client.vpgs.delete_vpg(created_vpgs[0], force=True, keep_recovery_volumes=False)
        logging.info(f"VPG {created_vpgs[0]} deleted successfully.")
        
        zvm_client.vpgs.delete_vpg(created_vpgs[1], force=True, keep_recovery_volumes=False)
        logging.info(f"VPG {created_vpgs[1]} deleted successfully.")

    except Exception as e:
        logging.exception("Error:")
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()