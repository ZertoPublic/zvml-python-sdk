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

# Configure logging BEFORE any imports
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
import json
import argparse
import sys
from typing import Dict, Any, List, Tuple

def modify_vpg_settings(json_data: Dict[str, Any], modifications: List[Tuple[str, str, str]]) -> None:
    """
    Modify VPG settings based on the list of modifications
    Each modification is a tuple of (field_path, new_value, level)
    """
    for vpg in json_data['ExportedVpgSettingsApi']:
        # Check and modify VPG name
        if 'Basic' in vpg and 'Name' in vpg['Basic']:
            name = vpg['Basic']['Name']
            if not name.startswith('dr-'):
                print(f"Warning: VPG name '{name}' does not start with 'dr-'")
            else:
                vpg['Basic']['Name'] = 'adr-' + name[3:]  # Replace 'dr-' with 'adr-'

        # Handle VPG level modifications
        for field_path, new_value, level in modifications:
            if level == 'vpg':
                if field_path == 'Basic.RecoverySiteIdentifier':
                    vpg['Basic']['RecoverySiteIdentifier'] = new_value
                elif field_path == 'Recovery.DefaultHostIdentifier':
                    vpg['Recovery']['DefaultHostIdentifier'] = new_value
                elif field_path == 'Networks.Failover.PublicCloud.SubnetIdentifier':
                    vpg['Networks']['Failover']['PublicCloud']['SubnetIdentifier'] = new_value
                elif field_path == 'Networks.FailoverTest.PublicCloud.SubnetIdentifier':
                    vpg['Networks']['FailoverTest']['PublicCloud']['SubnetIdentifier'] = new_value
                elif field_path == 'Recovery.DefaultDatastoreIdentifier':
                    vpg['Recovery']['DefaultDatastoreIdentifier'] = new_value

        # Handle VM level modifications
        if 'Vms' in vpg:
            for vm in vpg['Vms']:
                for field_path, new_value, level in modifications:
                    if level == 'vm':
                        if field_path == 'Vms[].Recovery.PublicCloud.Failover.VirtualNetworkIdentifier':
                            vm['Recovery']['PublicCloud']['Failover']['VirtualNetworkIdentifier'] = new_value
                        elif field_path == 'Vms[].Recovery.PublicCloud.FailoverTest.VirtualNetworkIdentifier':
                            vm['Recovery']['PublicCloud']['FailoverTest']['VirtualNetworkIdentifier'] = new_value
                
                # Update NIC level SubnetIdentifier
                if 'Nics' in vm:
                    for nic in vm['Nics']:
                        for field_path, new_value, level in modifications:
                            if level == 'vpg':
                                if field_path == 'Networks.Failover.PublicCloud.SubnetIdentifier':
                                    nic['Failover']['PublicCloud']['SubnetIdentifier'] = new_value
                                elif field_path == 'Networks.FailoverTest.PublicCloud.SubnetIdentifier':
                                    nic['FailoverTest']['PublicCloud']['SubnetIdentifier'] = new_value
                
                # Remove Preseed field from volumes if it exists
                if 'Volumes' in vm:
                    for volume in vm['Volumes']:
                        if 'Preseed' in volume:
                            del volume['Preseed']

def main():
    parser = argparse.ArgumentParser(description='Modify VPG settings in JSON file')
    parser.add_argument('input_file', help='Input JSON file path')
    parser.add_argument('output_file', help='Output JSON file path')
    parser.add_argument('--modifications', nargs='+', required=True,
                      help='List of modifications in format: "field_path:new_value:level"')
    
    args = parser.parse_args()
    
    # Parse modifications
    modifications = []
    for mod in args.modifications:
        try:
            field_path, new_value, level = mod.split(':')
            if level not in ['vpg', 'vm']:
                raise ValueError(f"Invalid level: {level}")
            modifications.append((field_path, new_value, level))
        except ValueError as e:
            print(f"Error parsing modification '{mod}': {str(e)}")
            sys.exit(1)
    
    try:
        # Read input JSON file
        with open(args.input_file, 'r') as f:
            json_data = json.load(f)
        
        # Modify the JSON data
        modify_vpg_settings(json_data, modifications)
        
        # Write output JSON file
        with open(args.output_file, 'w') as f:
            json.dump(json_data, f, indent=2)
            
        print(f"Successfully modified {len(modifications)} fields in {args.input_file}")
        print(f"Output written to {args.output_file}")
        
    except FileNotFoundError:
        print(f"Error: File {args.input_file} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: {args.input_file} is not a valid JSON file")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 