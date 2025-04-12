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
Zerto Datastores Example Script

This script demonstrates how to retrieve and list datastores from a Zerto environment.

The script performs the following steps:
1. Connects to Zerto Virtual Manager (ZVM)
2. Gets the local site identifier
3. Lists all datastores in the site
4. Gets detailed information about a specific datastore

Required Arguments:
    --zvm_address: ZVM address
    --client_id: Keycloak client ID
    --client_secret: Keycloak client secret

Optional Arguments:
    --ignore_ssl: Ignore SSL certificate verification

Example Usage:
    python examples/datastore_example.py \
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
    parser = argparse.ArgumentParser(description="Zerto Datastores Example")
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

        # Get local site identifier
        local_site = client.localsite.get_local_site()
        site_identifier = local_site.get('SiteIdentifier')
        logging.info(f"Local site identifier: {site_identifier}")

        # Get datastores using VirtualizationSites API
        datastores = client.virtualization_sites.get_virtualization_site_datastores(site_identifier)
        logging.info("\nDatastores in site:")
        logging.info(json.dumps(datastores, indent=2))

        # Get specific datastore details if any exist
        if datastores:
            first_ds_id = datastores[0].get('DatastoreIdentifier')
            logging.info(f"\nGetting details for specific datastore: {first_ds_id}")
            
            ds_details = client.datastores.list_datastores(first_ds_id)
            logging.info("Datastore details:")
            logging.info(json.dumps(ds_details, indent=2))

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 