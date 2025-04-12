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
Zerto License Management Example Script

This script demonstrates how to manage Zerto licenses through the API.

The script performs the following steps:
1. Connects to Zerto Virtual Manager (ZVM)
2. Retrieves current license information
3. Updates the license if a new key is provided
4. Verifies the updated license details
5. Optionally can delete the license (commented out for safety)

Required Arguments:
    --zvm_address: ZVM address
    --client_id: Keycloak client ID
    --client_secret: Keycloak client secret

Optional Arguments:
    --license_key: License key to add/update
    --ignore_ssl: Ignore SSL certificate verification

Example Usage:
    python examples/license_example.py \
        --zvm_address <zvm_address> \
        --client_id <client_id> \
        --client_secret <client_secret> \
        --license_key <license_key> \
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
    parser = argparse.ArgumentParser(description="Zerto License Example")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument('--client_id', required=True, help='Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Keycloak client secret')
    parser.add_argument("--license_key", help="License key to add/update")
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

        # Get current license information
        logging.info("\nFetching current license information...")
        license_info = client.license.get_license()
        if license_info:
            logging.info("Current license details:")
            logging.info(json.dumps(license_info, indent=2))
        else:
            logging.info("No license currently installed")

        # If license key is provided, update the license
        if args.license_key:
            logging.info(f"\nUpdating license with new key...")
            update_result = client.license.put_license(args.license_key)
            if update_result:
                logging.info("License update result:")
                logging.info(json.dumps(update_result, indent=2))
            else:
                logging.info("License updated successfully (no content returned)")

            # Get updated license information
            logging.info("\nFetching updated license information...")
            updated_license = client.license.get_license()
            if updated_license:
                logging.info("Updated license details:")
                logging.info(json.dumps(updated_license, indent=2))

        # Delete license (commented out for safety - uncomment if needed)
        """
        logging.info("\nDeleting license...")
        delete_result = client.license.delete_license()
        if delete_result:
            logging.info("License deletion result:")
            logging.info(json.dumps(delete_result, indent=2))
        else:
            logging.info("License deleted successfully (no content returned)")

        # Verify license is deleted
        final_check = client.license.get_license()
        if not final_check:
            logging.info("License successfully removed")
        """

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 