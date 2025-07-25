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
Zerto VPG Settings Export/Import Example Script

This script demonstrates how to export and import Virtual Protection Group (VPG) settings
using the Zerto Virtual Manager (ZVM) API. It allows for backup and restoration of VPG
configurations, which is useful for disaster recovery planning and VPG replication.

Key Features:
1. VPG Settings Export:
   - Export settings for specific VPGs or all VPGs
   - Save exported settings to a JSON file
   - Include all VPG configuration parameters
   - Capture recovery site mappings

2. Settings Verification:
   - List all available exported settings
   - Read and display detailed settings
   - Show summary of exported VPG configurations
   - Verify export timestamp and status

3. VPG Settings Import:
   - Import settings back to create new VPGs
   - Restore original VPG configurations
   - Support for multiple VPGs in single operation
   - Validate import results

Required Arguments:
    --zvm_address: Protected site ZVM address
    --client_id: Protected site Keycloak client ID
    --client_secret: Protected site Keycloak client secret
    --ignore_ssl: Ignore SSL certificate verification (optional)
    --vpg_names: Comma-separated list of VPG names to export (optional)
    --output_file: File path to save exported settings (optional)

Example Usage:
    python examples/vpg_setting_export_example.py \
        --zvm_address "192.168.111.20" \
        --client_id "zerto-api" \
        --client_secret "your-secret-here" \
        --vpg_names "VpgTest1,VpgTest2" \
        --output_file "vpg_settings.json" \
        --ignore_ssl

Script Flow:
1. Connects to protected site ZVM
2. Exports VPG settings:
   - For specified VPGs if vpg_names provided
   - For all VPGs if no vpg_names specified
3. Saves settings to file if output_file specified
4. Verifies export by reading settings
5. Displays VPG configuration summaries:
   - VPG names
   - Source and target sites
   - RPO and journal history
6. Pauses for manual VPG deletion
7. Imports settings to recreate VPGs
8. Verifies import success

Note: This script requires only protected site credentials. It's designed for VPG
configuration backup and restore scenarios, allowing you to quickly recreate VPGs
with identical settings after changes or in disaster recovery situations.
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
from zvml import ZVMLClient

# Disable SSL warningss
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

def main():
    parser = argparse.ArgumentParser(description="Export and Import VPG settings example")
    parser.add_argument("--zvm_address", required=True, help="Site 1 ZVM address")
    parser.add_argument('--client_id', required=True, help='Site 1 Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Site 1 Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    parser.add_argument("--vpg_names", help="Comma-separated list of VPG names to export settings for")
    parser.add_argument("--output_file", help="Optional file to save the exported settings")
    args = parser.parse_args()

    try:
        # Setup client
        client = setup_client(args)
        
        # If no VPG names provided, get all VPGs
        if not args.vpg_names:
            vpgs = client.vpgs.list_vpgs()
            vpg_names = [vpg['VpgName'] for vpg in vpgs]
            logging.info(f"No VPG names provided, exporting all {len(vpg_names)} VPGs")
        else:
            # Split the comma-separated string and strip whitespace
            vpg_names = [name.strip() for name in args.vpg_names.split(',')]
            logging.info(f"Exporting settings for VPGs: {vpg_names}")

        # Step 1: Export VPG settings
        print("\nStep 1: Exporting VPG settings...")
        result = client.vpgs.export_vpg_settings(vpg_names)
        
        print("Export Result:")
        print(f"Timestamp: {result.get('TimeStamp')}")
        print(f"Result: {result.get('ExportResult', {}).get('Result')}")
        print(f"Message: {result.get('ExportResult', {}).get('Message')}")

        # Save to file if specified
        if args.output_file:
            with open(args.output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nExported settings saved to: {args.output_file}")

        # Step 2: Verify export and read settings
        print("\nStep 2: Reading exported settings...")
        exported_settings = client.vpgs.list_exported_vpg_settings()
        export_timestamp = result.get('TimeStamp', '').split('.')[0] + '.000Z'
        
        if any(setting.get('TimeStamp') == export_timestamp for setting in exported_settings):
            print(f"Found export with timestamp {export_timestamp}")
            settings = client.vpgs.read_exported_vpg_settings(export_timestamp)
            
            # Display summary of exported VPG settings
            vpg_settings = settings.get('ExportedVpgSettingsApi', [])
            print(f"\nFound settings for {len(vpg_settings)} VPGs:")
            for vpg in vpg_settings:
                basic = vpg.get('Basic', {})
                print(f"\nVPG Name: {basic.get('Name')}")
                print(f"Source Site: {vpg.get('SourceSiteName')}")
                print(f"Target Site: {vpg.get('TargetSiteName')}")
                print(f"RPO (seconds): {basic.get('RpoInSeconds')}")
                print(f"Journal History (hours): {basic.get('JournalHistoryInHours')}")

            #pause
            input("Delte VPG manually  and Press Enter to continue...")

            # Step 3: Import the settings back
            print("\nStep 3: Importing VPG settings...")
            import_result = client.vpgs.import_vpg_settings(settings)
            print("\nImport Result:")
            print(f"Result: {import_result.get('Result')}")
            print(f"Message: {import_result.get('Message')}")
            if import_result.get('VpgSettingsIds'):
                print(f"Created VPG Settings IDs: {', '.join(import_result.get('VpgSettingsIds'))}")
            
            #pause
            input("Look at the VPG and verify whether the manual channges are reverted back to the original settings. Press Enter to continue...")
        else:
            print(f"\nWarning: Export with timestamp {export_timestamp} not found in exported settings list")

    except Exception as e:
        logging.exception("Error occurred:")
        sys.exit(1)

if __name__ == "__main__":
    main() 