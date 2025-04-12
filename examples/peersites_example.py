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
Zerto Peer Sites Management Example Script

This script demonstrates how to manage peer site relationships between Zerto Virtual Managers (ZVMs).

The script performs the following steps:
1. Connects to two Zerto Virtual Managers (ZVMs)
2. Lists existing peer sites from site 1
3. Checks for and removes any existing pairing with site 2
4. Generates a pairing token at site 2
5. Pairs site 1 with site 2 using the token
6. Verifies the pairing by checking the updated peer sites list

Required Arguments:
    --site1_zvm_address: Site 1 ZVM address
    --site1_client_id: Site 1 Keycloak client ID
    --site1_client_secret: Site 1 Keycloak client secret
    --site2_zvm_address: Site 2 ZVM address
    --site2_client_id: Site 2 Keycloak client ID
    --site2_client_secret: Site 2 Keycloak client secret

Optional Arguments:
    --ignore_ssl: Ignore SSL certificate verification

Example Usage:
    python examples/peersites_example.py \
        --site1_zvm_address <zvm1_address> \
        --site1_client_id <client_id1> \
        --site1_client_secret <secret1> \
        --site2_zvm_address <zvm2_address> \
        --site2_client_id <client_id2> \
        --site2_client_secret <secret2> \
        --ignore_ssl
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import logging
import urllib3
import json
import time
from zvml import ZVMLClient

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser(description="Zerto Peer Sites Example")
    parser.add_argument("--site1_zvm_address", required=True, help="site 1 ZVM address")
    parser.add_argument('--site1_client_id', required=True, help='site 1 Keycloak client ID')
    parser.add_argument('--site1_client_secret', required=True, help='site 1 Keycloak client secret')
    parser.add_argument("--site2_zvm_address", required=True, help="site 2 ZVM address")
    parser.add_argument('--site2_client_id', required=True, help='site 2 Keycloak client ID')
    parser.add_argument('--site2_client_secret', required=True, help='site 2 Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        # Initialize the site 1 client
        site1_client = ZVMLClient(
            zvm_address=args.site1_zvm_address,
            client_id=args.site1_client_id,
            client_secret=args.site1_client_secret,
            verify_certificate=not args.ignore_ssl
        )

        # Initialize the site 2 client
        site2_client = ZVMLClient(
            zvm_address=args.site2_zvm_address,
            client_id=args.site2_client_id,
            client_secret=args.site2_client_secret,
            verify_certificate=not args.ignore_ssl
        )

        # Example 1: Get all peer sites from site 1
        logging.info("\nExample 1: Getting all peer sites from site 1")
        peer_sites = site1_client.peersites.get_peer_sites()
        logging.info(f"Found {len(peer_sites)} peer sites:")
        logging.info(json.dumps(peer_sites, indent=2))

        # Check if site2 is already paired and delete if necessary
        site2_already_paired = False
        site2_identifier = None
        for site in peer_sites:
            if site['HostName'] == args.site2_zvm_address:
                site2_already_paired = True
                site2_identifier = site['SiteIdentifier']
                break

        if site2_already_paired:
            logging.info(f"\nFound existing pairing with {args.site2_zvm_address}, deleting...")
            site1_client.peersites.delete_peer_site(site2_identifier)
            logging.info("Existing pairing deleted")
            # Wait for deletion to complete
            time.sleep(5)

        # Example 2: Generate pairing token at site 2
        logging.info("\nExample 2: Generating pairing token at site 2")
        token = site2_client.peersites.generate_token()
        logging.info("Generated token:")
        logging.info(json.dumps(token, indent=2))

        # Example 3: Pair site 1 with site 2
        logging.info(f"\nExample 3: Pairing site 1 with site 2 ({args.site2_zvm_address})")
        pair_result = site1_client.peersites.pair_site(
            hostname=args.site2_zvm_address,
            token=token['Token'],
            port=9071
        )
        logging.info("Pairing result:")
        logging.info(json.dumps(pair_result, indent=2))

        # Wait for pairing to complete
        time.sleep(5)

        # Example 4: Verify pairing by getting updated peer sites list
        logging.info("\nExample 4: Verifying pairing by getting updated peer sites list")
        updated_peer_sites = site1_client.peersites.get_peer_sites()
        logging.info(f"Found {len(updated_peer_sites)} peer sites:")
        logging.info(json.dumps(updated_peer_sites, indent=2))

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 