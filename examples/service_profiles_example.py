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
Zerto Service Profiles Example Script

This script demonstrates how to retrieve and display service profile information from a Zerto Virtual Manager (ZVM).

The script performs the following steps:
1. Connects to Zerto Virtual Manager (ZVM)
2. Retrieves service profiles (optionally filtered by site)
3. Displays detailed information for each profile:
   - Profile name
   - RPO settings
   - History configuration
   - Journal size limits
   - Test intervals
   - Profile description

Required Arguments:
    --zvm_address: ZVM address
    --client_id: Keycloak client ID
    --client_secret: Keycloak client secret

Optional Arguments:
    --site_identifier: Site identifier to filter profiles
    --ignore_ssl: Ignore SSL certificate verification

Example Usage:
    python examples/service_profiles_example.py \
        --zvm_address <zvm_address> \
        --client_id <client_id> \
        --client_secret <client_secret> \
        --site_identifier <site_id> \
        --ignore_ssl
"""
# Configure logging BEFORE any imports
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
    parser = argparse.ArgumentParser(description="Zerto Service Profiles Example")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument('--client_id', required=True, help='Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Keycloak client secret')
    parser.add_argument("--site_identifier", help="Optional site identifier to filter profiles")
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    args = parser.parse_args()

    try:
        # Connect to ZVM
        logging.info(f"Connecting to ZVM at {args.zvm_address}")
        client = ZVMLClient(
            zvm_address=args.zvm_address,
            client_id=args.client_id,
            client_secret=args.client_secret,
            verify_certificate=not args.ignore_ssl
        )

        # Get all service profiles
        logging.info("\nFetching service profiles...")
        profiles = client.service_profiles.get_service_profiles(
            site_identifier=args.site_identifier
        )

        # Display service profiles information
        if profiles:
            logging.info(f"\nFound {len(profiles)} service profiles:")
            for profile in profiles:
                logging.info("\nService Profile Details:")
                logging.info(f"Name: {profile.get('serviceProfileName')}")
                logging.info(f"RPO: {profile.get('rpo')}")
                logging.info(f"History: {profile.get('history')}")
                logging.info(f"Max Journal Size: {profile.get('maxJournalSizeInPercent')}%")
                logging.info(f"Test Interval: {profile.get('testInterval')}")
                if profile.get('description'):
                    logging.info(f"Description: {profile.get('description')}")
                logging.info("-" * 50)
        else:
            logging.warning("No service profiles found")

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 