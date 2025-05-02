import argparse
import logging
import urllib3
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from zvml import ZVMLClient

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def setup_client(args):
    return ZVMLClient(
        zvm_address=args.zvm_address,
        client_id=args.client_id,
        client_secret=args.client_secret,
        verify_certificate=not args.ignore_ssl
    )

def print_journal_settings(vpg_name, vpg_basic):
    print(f"\nVPG: {vpg_name}")
    print("  JournalHistoryInHours:", vpg_basic.get('JournalHistoryInHours'))

def main():
    parser = argparse.ArgumentParser(description="Adjust VPG journal settings interactively or via CLI options")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument('--client_id', required=True, help='Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    parser.add_argument("--journal_days", type=int, help="Set journal history (days) for all VPGs (non-interactive)")
    parser.add_argument("--journal_hours", type=int, default=0, help="Set additional journal history (hours) for all VPGs (non-interactive)")
    args = parser.parse_args()

    client = setup_client(args)
    vpgs = client.vpgs.list_vpgs()
    if not vpgs:
        print("No VPGs found.")
        sys.exit(0)
    if isinstance(vpgs, dict):  # If only one VPG, wrap in list
        vpgs = [vpgs]

    use_cli_journal = args.journal_days is not None

    for vpg in vpgs:
        vpg_name = vpg['VpgName']
        vpg_identifier = vpg['VpgIdentifier']
        print(f"\nProcessing VPG: {vpg_name}")

        # Create VPG settings (get current settings object)
        vpg_settings_id = client.vpgs.create_vpg_settings(vpg_identifier=vpg_identifier)
        vpg_settings = client.vpgs.get_vpg_settings_by_id(vpg_settings_id)

        vpg_basic = vpg_settings.get('Basic', {})

        # Present current settings
        print_journal_settings(vpg_name, vpg_basic)

        if use_cli_journal:
            total_hours = args.journal_days * 24 + args.journal_hours
            print(f"  Applying journal history: {args.journal_days} days + {args.journal_hours} hours = {total_hours} hours")
        else:
            # Ask user if they want to change
            change = input("Do you want to change the journal history for this VPG? (y/n): ")
            if change.lower() != 'y':
                continue

            # Prompt for new values (always store in hours)
            while True:
                try:
                    new_days = int(input("  Enter new journal history (days): "))
                    new_hours = int(input("  Enter additional journal history (hours): "))
                    total_hours = new_days * 24 + new_hours
                    break
                except ValueError:
                    print("  Please enter valid integers.")

        # Adjust VPG-level journal history
        vpg_basic['JournalHistoryInHours'] = total_hours

        # Present new settings
        print("\nNew settings to be applied:")
        print_journal_settings(vpg_name, vpg_basic)

        if use_cli_journal:
            # No confirmation, just apply
            client.vpgs.update_vpg_settings(vpg_settings_id, vpg_settings)
            client.vpgs.commit_vpg(vpg_settings_id, vpg_name, sync=False)
            print("  Changes committed.")
        else:
            confirm = input("Commit these changes? (y/n): ")
            if confirm.lower() == 'y':
                client.vpgs.update_vpg_settings(vpg_settings_id, vpg_settings)
                client.vpgs.commit_vpg(vpg_settings_id, vpg_name, sync=False)
                print("  Changes committed.")
            else:
                print("  Changes not committed.")

if __name__ == "__main__":
    main()