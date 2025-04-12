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
Zerto Virtualization Sites Example Script

This script demonstrates how to retrieve and manage virtualization site information from Zerto.

The script performs the following steps:
1. Connects to Zerto Virtual Manager (ZVM)
2. Retrieves information about virtualization sites:
   - Basic site details
   - Unprotected VMs and vApps
   - Storage resources (datastores, clusters)
   - Network configurations
   - Host information
   - Cloud resources (networks, subnets, security)
3. For each site, retrieves detailed information about:
   - Organization VDCs
   - Storage policies
   - Network configurations
   - Host devices and clusters

Required Arguments:
    --zvm_address: ZVM address
    --client_id: Keycloak client ID
    --client_secret: Keycloak client secret

Optional Arguments:
    --ignore_ssl: Ignore SSL certificate verification

Example Usage:
    python examples/virtualization_sites_example.py \
        --zvm_address <zvm_address> \
        --client_id <client_id> \
        --client_secret <client_secret> \
        --ignore_ssl
"""

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
    parser = argparse.ArgumentParser(description="Zerto Virtualization Sites Example")
    parser.add_argument("--zvm_address", required=True, help="ZVM IP address")
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
        # Initialize the client
        client = ZVMLClient(
            zvm_address=args.zvm_address,
            client_id=args.client_id,
            client_secret=args.client_secret,
            verify_certificate=not args.ignore_ssl
        )

        # Example 1: Get all virtualization sites
        logging.info("\nExample 1: Getting all virtualization sites")
        sites = client.virtualization_sites.get_virtualization_sites()
        logging.info("All sites:")
        logging.info(json.dumps(sites, indent=2))

        # Example 2: Get details for each site individually
        for site in sites:
            site_id = site['SiteIdentifier']
            site_name = site['VirtualizationSiteName']
            
            logging.info(f"\nExample 2: Getting details for site {site_name} (ID: {site_id})")
            site_details = client.virtualization_sites.get_virtualization_sites(site_identifier=site_id)
            logging.info("Site Details:")
            logging.info(json.dumps(site_details, indent=2))

            # Example 3: Get unprotected VMs for each site
            logging.info(f"\nExample 3: Getting unprotected VMs for site {site_name}")
            vms = client.virtualization_sites.get_virtualization_site_vms(site_id)
            logging.info(f"Found {len(vms)} unprotected VMs:")
            logging.info(json.dumps(vms, indent=2))

            # Example 4: Get unprotected VCD vApps for each site
            logging.info(f"\nExample 4: Getting unprotected VCD vApps for site {site_name}")
            vapps = client.virtualization_sites.get_virtualization_site_vcd_vapps(site_id)
            logging.info(f"Found {len(vapps)} unprotected VCD vApps:")
            logging.info(json.dumps(vapps, indent=2))

            # Example 5: Get datastores for each site
            logging.info(f"\nExample 5: Getting datastores for site {site_name}")
            datastores = client.virtualization_sites.get_virtualization_site_datastores(site_id)
            logging.info(f"Found {len(datastores)} datastores:")
            logging.info(json.dumps(datastores, indent=2))

            # Example 6: Get folders for each site
            logging.info(f"\nExample 6: Getting folders for site {site_name}")
            folders = client.virtualization_sites.get_virtualization_site_folders(site_id)
            logging.info(f"Found {len(folders)} folders:")
            logging.info(json.dumps(folders, indent=2))

            # Example 7: Get datastore clusters for each site
            logging.info(f"\nExample 7: Getting datastore clusters for site {site_name}")
            datastore_clusters = client.virtualization_sites.get_virtualization_site_datastore_clusters(site_id)
            logging.info(f"Found {len(datastore_clusters)} datastore clusters:")
            logging.info(json.dumps(datastore_clusters, indent=2))

            # Example 8: Get resource pools for each site
            logging.info(f"\nExample 8: Getting resource pools for site {site_name}")
            resource_pools = client.virtualization_sites.get_virtualization_site_resource_pools(site_id)
            logging.info(f"Found {len(resource_pools)} resource pools:")
            logging.info(json.dumps(resource_pools, indent=2))

            # Example 9: Get organization VDCs for each site
            logging.info(f"\nExample 9: Getting organization VDCs for site {site_name}")
            org_vdcs = client.virtualization_sites.get_virtualization_site_org_vdcs(site_id)
            logging.info(f"Found {len(org_vdcs)} organization VDCs:")
            logging.info(json.dumps(org_vdcs, indent=2))

            # Example 10: Get networks for each site
            logging.info(f"\nExample 10: Getting networks for site {site_name}")
            networks = client.virtualization_sites.get_virtualization_site_networks(site_id)
            logging.info(f"Found {len(networks)} networks:")
            logging.info(json.dumps(networks, indent=2))

            # Example 11: Get hosts for each site
            logging.info(f"\nExample 11: Getting hosts for site {site_name}")
            hosts = client.virtualization_sites.get_virtualization_site_hosts(site_id)
            logging.info(f"Found {len(hosts)} hosts:")
            logging.info(json.dumps(hosts, indent=2))

            # Example 12: Get host clusters for each site
            logging.info(f"\nExample 12: Getting host clusters for site {site_name}")
            host_clusters = client.virtualization_sites.get_virtualization_site_host_clusters(site_id)
            logging.info(f"Found {len(host_clusters)} host clusters:")
            logging.info(json.dumps(host_clusters, indent=2))

            # Example 13: Get repositories for each site
            logging.info(f"\nExample 13: Getting repositories for site {site_name}")
            repositories = client.virtualization_sites.get_virtualization_site_repositories(site_id)
            logging.info(f"Found {len(repositories)} repositories:")
            logging.info(json.dumps(repositories, indent=2))

            # Example 14: Get networks for each org VDC
            logging.info(f"\nExample 14: Getting org VDC networks for site {site_name}")
            org_vdcs = client.virtualization_sites.get_virtualization_site_org_vdcs(site_id)
            for org_vdc in org_vdcs:
                org_vdc_id = org_vdc['OrgVdcIdentifier']
                org_vdc_name = org_vdc['VcdVdcName']
                logging.info(f"\nFetching networks for org VDC: {org_vdc_name}")
                networks = client.virtualization_sites.get_virtualization_site_org_vdc_networks(site_id, org_vdc_id)
                logging.info(f"Found {len(networks)} networks in org VDC {org_vdc_name}:")
                logging.info(json.dumps(networks, indent=2))

                # Example 15: Get storage policies for each org VDC
                logging.info(f"\nExample 15: Getting storage policies for org VDC: {org_vdc_name}")
                storage_policies = client.virtualization_sites.get_virtualization_site_org_vdc_storage_policies(site_id, org_vdc_id)
                logging.info(f"Found {len(storage_policies)} storage policies in org VDC {org_vdc_name}:")
                logging.info(json.dumps(storage_policies, indent=2))

                # Example 16: Get devices for each site
                logging.info(f"\nExample 16a: Getting all devices for site {site_name}")
                devices = client.virtualization_sites.get_virtualization_site_devices(site_id)
                logging.info(f"Found {len(devices)} devices:")
                logging.info(json.dumps(devices, indent=2))

                # If we have hosts, get devices for the first host
                if hosts:
                    host_id = hosts[0]['HostIdentifier']
                    logging.info(f"\nExample 16b: Getting devices for host {host_id} in site {site_name}")
                    host_devices = client.virtualization_sites.get_virtualization_site_devices(
                        site_id, 
                        host_identifier=host_id
                    )
                    logging.info(f"Found {len(host_devices)} devices for host {host_id}:")
                    logging.info(json.dumps(host_devices, indent=2))

                    # If we found any devices, try filtering by the first device name
                    if host_devices:
                        device_name = host_devices[0]['DeviceName']
                        logging.info(f"\nExample 16c: Getting devices with name {device_name} in site {site_name}")
                        filtered_devices = client.virtualization_sites.get_virtualization_site_devices(
                            site_id, 
                            device_name=device_name
                        )
                        logging.info(f"Found {len(filtered_devices)} devices with name {device_name}:")
                        logging.info(json.dumps(filtered_devices, indent=2))

            # Example 17: Get public cloud virtual networks for each site
            logging.info(f"\nExample 17: Getting public cloud virtual networks for site {site_name}")
            cloud_networks = client.virtualization_sites.get_virtualization_site_public_cloud_networks(site_id)
            logging.info(f"Found {len(cloud_networks)} public cloud virtual networks:")
            logging.info(json.dumps(cloud_networks, indent=2))

            # Example 18: Get public cloud subnets for each site
            logging.info(f"\nExample 18: Getting public cloud subnets for site {site_name}")
            cloud_subnets = client.virtualization_sites.get_virtualization_site_public_cloud_subnets(site_id)
            logging.info(f"Found {len(cloud_subnets)} public cloud subnets:")
            logging.info(json.dumps(cloud_subnets, indent=2))

            # Example 19: Get public cloud security groups for each site
            logging.info(f"\nExample 19: Getting public cloud security groups for site {site_name}")
            security_groups = client.virtualization_sites.get_virtualization_site_public_cloud_security_groups(site_id)
            logging.info(f"Found {len(security_groups)} public cloud security groups:")
            logging.info(json.dumps(security_groups, indent=2))

            # Example 20: Get public cloud VM instance types for each site
            logging.info(f"\nExample 20: Getting public cloud VM instance types for site {site_name}")
            instance_types = client.virtualization_sites.get_virtualization_site_public_cloud_vm_instance_types(site_id)
            logging.info(f"Found {len(instance_types)} public cloud VM instance types:")
            logging.info(json.dumps(instance_types, indent=2))

            # Example 21: Get public cloud resource groups for each site
            # currently this API returns a 500 error
            # logging.info(f"\nExample 21: Getting public cloud resource groups for site {site_name}")
            # resource_groups = client.virtualization_sites.get_virtualization_site_public_cloud_resource_groups(site_id)
            # logging.info(f"Found {len(resource_groups)} public cloud resource groups:")
            # logging.info(json.dumps(resource_groups, indent=2))

            # Example 22: Get public cloud keys containers for each site
            # currently this API returns a 500 error
            # logging.info(f"\nExample 22: Getting public cloud keys containers for site {site_name}")
            # keys_containers = client.virtualization_sites.get_virtualization_site_public_cloud_keys_containers(site_id)
            # logging.info(f"Found {len(keys_containers)} public cloud keys containers:")
            # logging.info(json.dumps(keys_containers, indent=2))

            # Example 23: Get all encryption keys
            # currently this API returns a 500 error if does not exist
            # logging.info(f"\nExample 23a: Getting all encryption keys for site {site_name}")
            # encryption_keys = client.virtualization_sites.get_virtualization_site_public_cloud_encryption_keys(site_id)
            # logging.info(f"Found {len(encryption_keys)} encryption keys:")
            # logging.info(json.dumps(encryption_keys, indent=2))

            # Example 23b: Get details of specific encryption keys if any exist
            # if encryption_keys:
            #     key_id = encryption_keys[0]['Id']
            #     logging.info(f"\nExample 23b: Getting details for encryption key {key_id}")
            #     key_details = client.virtualization_sites.get_virtualization_site_public_cloud_encryption_keys(site_id, key_id)
            #     logging.info("Encryption key details:")
            #     logging.info(json.dumps(key_details, indent=2))

            # Example 24: Get public cloud managed identities for each site
            # currently this API returns a 500 error if does not exist
            # logging.info(f"\nExample 24: Getting public cloud managed identities for site {site_name}")
            # managed_identities = client.virtualization_sites.get_virtualization_site_public_cloud_managed_identities(site_id)
            # logging.info(f"Found {len(managed_identities)} managed identities:")
            # logging.info(json.dumps(managed_identities, indent=2))

            # Example 25: Get public cloud disk encryption keys for each site
            # currently this API returns a 500 error if does not exist
            # logging.info(f"\nExample 25: Getting public cloud disk encryption keys for site {site_name}")
            # disk_encryption_keys = client.virtualization_sites.get_virtualization_site_public_cloud_disk_encryption_keys(site_id)
            # logging.info(f"Found {len(disk_encryption_keys)} disk encryption keys:")
            # logging.info(json.dumps(disk_encryption_keys, indent=2))
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 