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
Zerto Events Example Script

This script demonstrates how to retrieve and manage events in a Zerto environment.

The script performs the following steps:
1. Connects to Zerto Virtual Manager (ZVM)
2. Lists available event types
3. Lists available event entities
4. Lists available event categories
5. Retrieves events from the last hour
6. Demonstrates filtered event queries
7. Gets detailed information about specific events

Required Arguments:
    --zvm_address: ZVM address
    --client_id: Keycloak client ID
    --client_secret: Keycloak client secret

Optional Arguments:
    --ignore_ssl: Ignore SSL certificate verification

Example Usage:
    python examples/events_example.py \
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
from datetime import datetime, timedelta

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser(description="Zerto Events Example")
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

        # Get event types
        logging.info("\nFetching event types...")
        event_types = client.events.list_event_types()
        logging.info(f"Found {len(event_types)} event types:")
        logging.info(json.dumps(event_types[:3], indent=2))  # Show first 3 for brevity

        # Get event entities
        logging.info("\nFetching event entities...")
        event_entities = client.events.list_event_entities()
        logging.info(f"Found {len(event_entities)} event entities:")
        logging.info(json.dumps(event_entities[:3], indent=2))  # Show first 3 for brevity

        # Get event categories
        logging.info("\nFetching event categories...")
        event_categories = client.events.list_event_categories()
        logging.info(f"Found {len(event_categories)} event categories:")
        logging.info(json.dumps(event_categories[:3], indent=2))  # Show first 3 for brevity

        # Get events from the last 1 hour
        start_date = (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z'
        end_date = datetime.utcnow().isoformat() + 'Z'
        
        logging.info(f"\nFetching events from {start_date} to {end_date}...")
        events = client.events.list_events(
            start_date=start_date,
            end_date=end_date
        )
        logging.info(f"Found {len(events)} events in the last 24 hours:")
        if events:
            logging.info(json.dumps(events[:3], indent=2))  # Show first 3 for brevity

        # Get events with filters
        logging.info("\nFetching filtered events...")
        filtered_events = client.events.list_events(
            start_date=start_date,
            end_date=end_date,
            event_type=18,  # Using numeric event type
            category="Events"  # Using correct category from list_event_categories
        )
        logging.info(f"Found {len(filtered_events)} filtered events:")
        if filtered_events:
            logging.info(json.dumps(filtered_events[:3], indent=2))  # Show first 3 for brevity

        # If we have any events, get details for a specific event
        if events:
            event_id = events[0].get('EventIdentifier')
            logging.info(f"\nFetching details for event {event_id}...")
            event_details = client.events.list_events(event_identifier=event_id)
            logging.info("Event details:")
            logging.info(json.dumps(event_details, indent=2))

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 