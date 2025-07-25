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
Zerto Tweaks Management Example Script

This script demonstrates how to manage Zerto system tweaks, which are advanced configuration settings.

The script performs the following steps:
1. Connects to Zerto Virtual Manager (ZVM)
2. Lists all available system tweaks
3. Sets a specific tweak value (t_ransomwareEngCuSumThrsDiff)
4. Displays the updated tweak details
5. Deletes the tweak setting
6. Verifies the deletion by listing tweaks again

Required Arguments:
    --zvm_address: ZVM address
    --client_id: Keycloak client ID
    --client_secret: Keycloak client secret

Optional Arguments:
    --ignore_ssl: Ignore SSL certificate verification

Example Usage:
    python examples/tweaks_example.py \
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
import argparse
import urllib3
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zvml.zvml import ZVMLClient
from zvml.tweaks import Tweaks
from zvml.common import ZertoTweakType

# Disable SSL warnings
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

def format_tweaks_table(result):
    """Format tweaks into a table"""
    # Calculate maximum lengths for formatting
    max_name_len = max(len(str(tweak.get('name', ''))) for tweak in result)
    max_value_len = max(len(str(tweak.get('value', ''))) for tweak in result)
    max_type_len = max(len(str(tweak.get('type', ''))) for tweak in result)
    max_comment_len = max(len(str(tweak.get('comment', ''))) for tweak in result)
    
    # Print header
    header = f"{'Name':<{max_name_len}} | {'Value':<{max_value_len}} | {'Type':<{max_type_len}} | Description | {'Comment':<{max_comment_len}}"
    logging.info(header)
    logging.info("-" * len(header))
    
    # Print tweaks in a formatted table
    for tweak in result:
        name = str(tweak.get('name', 'N/A'))
        value = str(tweak.get('value', 'N/A'))
        tweak_type = str(tweak.get('type', 'N/A'))
        description = str(tweak.get('description', 'No description available'))
        comment = str(tweak.get('comment', ''))
        
        logging.info(f"{name:<{max_name_len}} | {value:<{max_value_len}} | {tweak_type:<{max_type_len}} | {description} | {comment}")
    
    logging.info("-" * 80)

def manage_tweaks(client: ZVMLClient):
    """List and manage ZVM tweaks"""
    tweaks = Tweaks(client)
    
    # Set a specific tweak
    tweak_name = "t_ransomwareEngCuSumThrsDiff"
    logging.info(f"\nSetting tweak {tweak_name}:")
    updated_tweak = tweaks.set_tweak(
        tweak_name=tweak_name,
        value="5",
        tweak_type=ZertoTweakType.ZVM,
        comment="mycomment"
    )
    
    # List all tweaks
    logging.info("\nListing all tweaks:")
    result = tweaks.list_tweaks()
    logging.info(f"Found {len(result)} ZVM tweaks:")
    logging.info("-" * 80)
    format_tweaks_table(result)
    
    # Show the specific tweak
    logging.info("\nShowing specific tweak details:")
    specific_result = tweaks.list_tweaks(tweak_name=tweak_name)
    format_tweaks_table(specific_result)
    
    # Delete the tweak
    logging.info(f"\nDeleting tweak {tweak_name}:")
    tweaks.delete_tweak(tweak_name)
    
    # Verify deletion by listing all tweaks again
    logging.info("\nVerifying deletion - listing all tweaks:")
    result = tweaks.list_tweaks()
    logging.info(f"Found {len(result)} ZVM tweaks:")
    logging.info("-" * 80)
    format_tweaks_table(result)

def main():
    parser = argparse.ArgumentParser(description="ZVM Tweaks Management Example")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument('--client_id', required=True, help='Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    args = parser.parse_args()

    try:
        # Setup client
        client = setup_client(args)
        
        # Manage tweaks
        manage_tweaks(client)

    except Exception as e:
        logging.exception("Error occurred:")
        sys.exit(1)

if __name__ == "__main__":
    main()