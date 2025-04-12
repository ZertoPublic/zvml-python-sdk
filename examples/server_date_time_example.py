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
Zerto Server Date-Time Example Script

This script demonstrates how to retrieve server time information in different formats from a Zerto Virtual Manager (ZVM).

The script performs the following steps:
1. Connects to Zerto Virtual Manager (ZVM)
2. Retrieves server time in three different formats:
   - Local time
   - UTC time
   - Argument format (used for API parameters)
3. Displays the time information for each format

Required Arguments:
    --zvm_address: ZVM address
    --client_id: Keycloak client ID
    --client_secret: Keycloak client secret

Optional Arguments:
    --ignore_ssl: Ignore SSL certificate verification

Example Usage:
    python examples/server_date_time_example.py \
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
from zvml import ZVMLClient
from zvml.server_date_time import DateTimeFormat

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser(description="Zerto Server Date-Time Example")
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

        # Test all three date-time formats
        logging.info("\nTesting all server date-time formats:")

        # Get local time
        local_time = client.server_date_time.get_server_date_time(DateTimeFormat.LOCAL)
        logging.info(f"\nLocal Time: {local_time}")

        # Get UTC time
        utc_time = client.server_date_time.get_server_date_time(DateTimeFormat.UTC)
        logging.info(f"UTC Time: {utc_time}")

        # Get argument format
        arg_format = client.server_date_time.get_server_date_time(DateTimeFormat.ARGUMENT)
        logging.info(f"Argument Format: {arg_format}")

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 