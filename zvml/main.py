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

import argparse
import logging
from zvml import ZVMLClient

def main():
    parser = argparse.ArgumentParser(description="zvml Client")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument("--username", required=True, help="Username")
    parser.add_argument("--password", required=True, help="Password")
    args = parser.parse_args()

    try:
        client = ZVMLClient(zvm_address=args.zvm_address, username=args.username, password=args.password)
        # Example usage
        vpgs = client.vpgs.list_vpgs()
        logging.info(f"VPGs: {vpgs}")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()