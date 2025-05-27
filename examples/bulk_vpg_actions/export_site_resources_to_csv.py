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
Zerto Site Resources Export Script

This script exports Zerto site resources (datastores, networks, VMs) to CSV files for both local and peer sites.
It helps in documenting and analyzing the available resources for VPG creation and management.

Key Features:
1. Site Resource Export:
   - Export peer site datastores with names and IDs
   - Export peer site networks with names and IDs
   - Export local site VMs with names and IDs

2. CSV File Generation:
   - Creates timestamped CSV files for each resource type
   - Includes detailed resource information
   - Uses site names in filenames for easy identification

Required Arguments:
    --zvm_address: ZVM IP address
    --client_id: API client ID
    --client_secret: API client secret
    --ignore_ssl: Ignore SSL certificate validation (optional)
    --output_dir: Directory to save CSV files (default: current directory)

Example Usage:
    python export_site_resources.py \
        --zvm_address "192.168.111.20" \
        --client_id "zerto-api" \
        --client_secret "your-secret-here" \
        --ignore_ssl
        --output_dir "output_dir"
"""

import argparse
import csv
from datetime import datetime
import logging
import os
import sys
import urllib3
from typing import Dict, List, Optional
import json

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
    parser = argparse.ArgumentParser(description='Export Zerto site resources to CSV files')
    parser.add_argument('--zvm_address', required=True, help='ZVM IP address')
    parser.add_argument('--client_id', required=True, help='API client ID')
    parser.add_argument('--client_secret', required=True, help='API client secret')
    parser.add_argument('--ignore_ssl', action='store_true', help='Ignore SSL certificate validation')
    parser.add_argument('--output_dir', default='.', help='Directory to save CSV files (default: current directory)')
    return parser

def ensure_output_dir(output_dir: str) -> None:
    """Ensure the output directory exists."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

def get_site_info(client: ZVMLClient) -> Dict[str, str]:
    """Get local and peer site information."""
    virtualization_sites = client.virtualization_sites.get_virtualization_sites()
    logger.info(f"Virtualization sites: {json.dumps(virtualization_sites, indent=4)}")
    if not virtualization_sites:
        raise ValueError("No sites found in ZVM")
    
    # Get local site id and name
    local_site = client.localsite.get_local_site()
    logger.info(f"Local site: {json.dumps(local_site, indent=4)}")
    local_site_id = local_site.get('SiteIdentifier')
    
    # Find local site in virtualization sites to get VirtualizationSiteName
    local_virtualization_site = next(
        (site for site in virtualization_sites if site['SiteIdentifier'] == local_site_id),
        None
    )
    if not local_virtualization_site:
        raise ValueError("Local site not found in virtualization sites")
    
    # Update local site with VirtualizationSiteName
    local_site['VirtualizationSiteName'] = local_virtualization_site['VirtualizationSiteName']
    
    # create an array of peer sites
    peer_sites = []
    for site in virtualization_sites:
        if site['SiteIdentifier'] != local_site_id:
            peer_sites.append(site)
    
    return {
        'local': local_site,
        'peers': peer_sites
    }

def export_datastores(client: ZVMLClient, site_info: Dict, output_dir: str) -> None:
    """Export datastores information to CSV."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Get peer site datastores
    peer_datastores = client.virtualization_sites.get_virtualization_site_datastores(
        site_identifier=site_info['SiteIdentifier']
    )
    
    # Create filename using VirtualizationSiteName
    filename = os.path.join(output_dir, f"{site_info['VirtualizationSiteName']}_datastores_{timestamp}.csv")
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Datastore Name', 'Datastore ID'])
        
        for ds in peer_datastores:
            writer.writerow([
                ds.get('DatastoreName'),
                ds.get('DatastoreIdentifier')
            ])
    
    logger.info(f"Exported {len(peer_datastores)} datastores to {filename}")

def export_networks(client: ZVMLClient, site_info: Dict, output_dir: str) -> None:
    """Export networks information to CSV."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Get peer site networks
    peer_networks = client.virtualization_sites.get_virtualization_site_networks(
        site_identifier=site_info['SiteIdentifier']
    )
    logger.info(f"export_networks: peer_networks: {json.dumps(peer_networks, indent=4)}")
    
    # Create filename using VirtualizationSiteName
    filename = os.path.join(output_dir, f"{site_info['VirtualizationSiteName']}_networks_{timestamp}.csv")
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Network VirtualizationNetworkName', 'Network ID'])
        
        for net in peer_networks:
            writer.writerow([
                net.get('VirtualizationNetworkName'),
                net.get('NetworkIdentifier')
            ])
    
    logger.info(f"Exported {len(peer_networks)} networks to {filename}")

def export_vms(client: ZVMLClient, site_info: Dict, output_dir: str) -> None:
    """Export VMs information to CSV."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Get local site VMs
    local_vms = client.virtualization_sites.get_virtualization_site_vms(
        site_identifier=site_info['SiteIdentifier']
    )
    
    # Create filename using VirtualizationSiteName
    filename = os.path.join(output_dir, f"{site_info['VirtualizationSiteName']}_vms_{timestamp}.csv")
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['VM Name', 'VM ID'])
        
        for vm in local_vms:
            writer.writerow([
                vm.get('VmName'),
                vm.get('VmIdentifier')
            ])
    
    logger.info(f"Exported {len(local_vms)} VMs to {filename}")

def export_hosts(client: ZVMLClient, site_info: Dict, output_dir: str) -> None:
    """Export hosts information to CSV."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Get peer site hosts
    peer_hosts = client.virtualization_sites.get_virtualization_site_hosts(
        site_identifier=site_info['SiteIdentifier']
    )
    logger.info(f"export_hosts: peer_hosts: {json.dumps(peer_hosts, indent=4)}")
    
    # Create filename using VirtualizationSiteName
    filename = os.path.join(output_dir, f"{site_info['VirtualizationSiteName']}_hosts_{timestamp}.csv")
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Host Name', 'Host ID'])
        
        for host in peer_hosts:
            writer.writerow([
                host.get('VirtualizationHostName'),
                host.get('HostIdentifier')
            ])
    
    logger.info(f"Exported {len(peer_hosts)} hosts to {filename}")

def export_folders(client: ZVMLClient, site_info: Dict, output_dir: str) -> None:
    """Export folders information to CSV."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Get peer site folders
    peer_folders = client.virtualization_sites.get_virtualization_site_folders(
        site_identifier=site_info['SiteIdentifier']
    )
    logger.info(f"export_folders: peer_folders: {json.dumps(peer_folders, indent=4)}")
    
    # Create filename using VirtualizationSiteName
    filename = os.path.join(output_dir, f"{site_info['VirtualizationSiteName']}_folders_{timestamp}.csv")
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Folder Name', 'Folder ID'])
        
        for folder in peer_folders:
            writer.writerow([
                folder.get('FolderName'),
                folder.get('FolderIdentifier')
            ])
    
    logger.info(f"Exported {len(peer_folders)} folders to {filename}")

def export_sites(client: ZVMLClient, site_info: Dict, output_dir: str) -> None:
    """Export sites information to CSV."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create filename for sites
    filename = os.path.join(output_dir, f"zerto_sites_{timestamp}.csv")
    
    # Get detailed peer site information
    peer_sites_details = client.peersites.get_peer_sites()
    # Convert to dict for easier lookup by site identifier
    peer_sites_dict = {site['SiteIdentifier']: site for site in peer_sites_details} if isinstance(peer_sites_details, list) else {}
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Site Name',
            'Site ID',
            'Location',
            'Version',
            'Site Type',
            'IP Address',
            'Is Local Site',
            'Host Name',
            'Region Name'
        ])
        
        # Write local site
        local_site = site_info['local']
        writer.writerow([
            local_site.get('SiteName'),
            local_site.get('SiteIdentifier'),
            local_site.get('Location'),
            local_site.get('Version'),
            local_site.get('SiteType'),
            local_site.get('IpAddress'),
            'Yes',
            'N/A',  # Local site doesn't have host name
            local_site.get('RegionName', '')
        ])
        
        # Write peer sites with detailed information
        for peer in site_info['peers']:
            peer_id = peer.get('SiteIdentifier')
            peer_details = peer_sites_dict.get(peer_id, {})
            
            writer.writerow([
                peer_details.get('PeerSiteName', ''),
                peer_id,
                peer_details.get('Location', ''),
                peer_details.get('Version', ''),
                peer_details.get('SiteType', ''),
                peer_details.get('HostName', ''),  # Using HostName as IP Address
                'No',
                peer_details.get('HostName', ''),
                peer_details.get('RegionName', '')
            ])
    
    logger.info(f"Exported {len(site_info['peers']) + 1} sites to {filename}")
    logger.info(f"Peer sites details: {json.dumps(peer_sites_details, indent=4)}")

def main():
    """Main function to execute the script."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    try:
        # Ensure output directory exists
        ensure_output_dir(args.output_dir)
        
        # Initialize ZVM client
        client = ZVMLClient(
            zvm_address=args.zvm_address,
            client_id=args.client_id,
            client_secret=args.client_secret,
            verify_certificate=not args.ignore_ssl
        )
        
        # Get site information
        logger.info("Retrieving site information...")
        site_info = get_site_info(client)
        logger.info(f"Site info: {json.dumps(site_info, indent=4)}")
        
        # Log site information
        logger.info(f"Local site: {site_info['local'].get('VirtualizationSiteName')}")
        for peer in site_info['peers']:
            logger.info(f"Peer site: {peer.get('VirtualizationSiteName')}")
        
        # Export sites to CSV
        logger.info("\nExporting sites information...")
        export_sites(client, site_info, args.output_dir)
        
        # Export resources to CSV files
        for peer in site_info['peers']:
            logger.info(f"Exporting resources for peer site: {peer.get('VirtualizationSiteName')}")
            export_datastores(client, peer, args.output_dir)
            export_networks(client, peer, args.output_dir)
            export_hosts(client, peer, args.output_dir)
            export_folders(client, peer, args.output_dir)
        
        logger.info(f"Exporting VMs for local site: {site_info['local'].get('VirtualizationSiteName')}")
        export_vms(client, site_info['local'], args.output_dir)
        
        logger.info(f"Export completed successfully. Files saved to: {args.output_dir}")
        
    except Exception as e:
        logger.exception("Error occurred:")  # This will log the full stack trace
        sys.exit(1)

if __name__ == '__main__':
    main() 