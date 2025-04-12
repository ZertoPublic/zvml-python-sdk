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
Zerto Alert Management Example Script

This script demonstrates basic alert management using the Zerto Virtual Manager (ZVM) API.
It shows how to list alerts and perform basic alert operations (dismiss/undismiss).

Key Features:
1. Alert Monitoring:
   - List all current alerts
   - Display alert details
   - Manage alert states (dismiss/undismiss)

Required Arguments:
    --zvm_address: ZVM server address
    --client_id: Keycloak client ID
    --client_secret: Keycloak client secret
    --ignore_ssl: Ignore SSL certificate verification (optional)

Example Usage:
    python examples/alerts_example.py \
        --zvm_address "192.168.111.20" \
        --client_id "zerto-api" \
        --client_secret "your-secret-here" \
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
    parser = argparse.ArgumentParser(description="Zerto Alerts Example")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument('--client_id', required=True, help='Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    try:
        # Connect to ZVM
        client = ZVMLClient(
            zvm_address=args.zvm_address,
            client_id=args.client_id,
            client_secret=args.client_secret,
            verify_certificate=not args.ignore_ssl
        )

        # Get current alerts
        alerts = client.alerts.get_alerts()
        if not alerts:
            logging.info("No alerts found in the system")
            return

        # Display alerts
        logging.info(f"Found {len(alerts)} alerts:")
        for alert in alerts:
            logging.info(f"\nAlert Details:")
            logging.info(f"  Description: {alert.get('Description')}")
            logging.info(f"  Status: {alert.get('Status')}")
            logging.info(f"  Level: {alert.get('Level')}")
            logging.info(f"  Turn off Time: {alert.get('TurnedOffTime')}")
            logging.info(f"  Entity: {alert.get('Entity')}")
            logging.info(f"  Help Identifier: {alert.get('HelpIdentifier')}")

            # Get alert identifier
            alert_id = alert.get('Link', {}).get('identifier')
            if alert_id:
                # Dismiss alert
                input(f"\nPress Enter to dismiss alert {alert_id}...")
                client.alerts.dismiss_alert(alert_identifier=alert_id)
                logging.info(f"Alert {alert_id} dismissed")

                # Undismiss alert
                input(f"Press Enter to undismiss alert {alert_id}...")
                client.alerts.undismiss_alert(alert_identifier=alert_id)
                logging.info(f"Alert {alert_id} undismissed")

    except Exception as e:
        logging.exception("Error:")
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()