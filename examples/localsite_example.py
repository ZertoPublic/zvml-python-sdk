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
Zerto Local Site Management Example Script

This script demonstrates how to manage and retrieve information about the local Zerto site.

The script performs the following steps:
1. Connects to Zerto Virtual Manager (ZVM)
2. Retrieves local site information
3. Gets site pairing statuses
4. Sends usage data to Zerto
5. Manages login banner settings:
   - Gets current banner configuration
   - Sets a new test banner
   - Verifies the updated settings
   - Disables the banner

Required Arguments:
    --zvm_address: ZVM address
    --client_id: Keycloak client ID
    --client_secret: Keycloak client secret

Optional Arguments:
    --ignore_ssl: Ignore SSL certificate verification

Example Usage:
    python examples/localsite_example.py \
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

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import urllib3
import json
from zvml import ZVMLClient

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser(description="Zerto Local Site Example")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument('--client_id', required=True, help='Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Keycloak client secret')
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

        # Get local site information
        logging.info("\nFetching local site information...")
        local_site = client.localsite.get_local_site()
        logging.info("Local site details:")
        logging.info(json.dumps(local_site, indent=2))

        # Get pairing statuses
        logging.info("\nFetching pairing statuses...")
        pairing_statuses = client.localsite.get_pairing_statuses()
        logging.info("Pairing statuses:")
        logging.info(json.dumps(pairing_statuses, indent=2))

        # Send usage data
        logging.info("\nSending usage data...")
        usage_result = client.localsite.send_usage()
        if usage_result:
            logging.info("Usage data result:")
            logging.info(json.dumps(usage_result, indent=2))
        else:
            logging.info("Usage data sent successfully (no content returned)")

        # Get current login banner settings
        logging.info("\nFetching current login banner settings...")
        current_banner = client.localsite.get_login_banner()
        logging.info("Current login banner settings:")
        logging.info(json.dumps(current_banner, indent=2))

        # Set new login banner
        test_banner = "This is a test login banner.\nAccess restricted to authorized users only."
        logging.info("\nSetting new login banner...")
        banner_result = client.localsite.set_login_banner(
            is_enabled=True,
            banner_text=test_banner
        )
        logging.info("Login banner update result:")
        logging.info(banner_result)

        # Verify the new banner settings
        logging.info("\nVerifying updated login banner settings...")
        updated_banner = client.localsite.get_login_banner()
        logging.info("Updated login banner settings:")
        logging.info(json.dumps(updated_banner, indent=2))

        # Disable the login banner
        logging.info("\nDisabling login banner...")
        disable_result = client.localsite.set_login_banner(
            is_enabled=False,
            banner_text=""
        )
        logging.info("Login banner disable result:")
        logging.info(disable_result)

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 