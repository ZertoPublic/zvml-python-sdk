
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

# Zerto VPG Management Scripts

This collection of scripts helps manage Virtual Protection Groups (VPGs) in Zerto, including resource discovery, VPG creation, and NIC configuration management using csv files. All scripts are located in the `examples/bulk_vpg_actions` directory.

## Prerequisites

- Python 3.x
- Zerto Python SDK installed
- Access to ZVM with API credentials
- Required Python packages (install via pip):
  ```bash
  pip install urllib3
  ```

## Step 1: Export Site Resources

First, export all available resources from your Zerto sites to understand what can be used in VPG creation.

```bash
cd examples/bulk_vpg_actions
python export_site_resources_to_csv.py \
    --zvm_address "192.168.111.20" \
    --client_id "zerto-api" \
    --client_secret "your-secret-here" \
    --ignore_ssl  \
    --output_dir
```

This will create several CSV files in the output_dir directory:
- `zerto_sites_[timestamp].csv` - Contains site information
- `[SiteName]_datastores_[timestamp].csv` - Available datastores at a target site
- `[SiteName]_networks_[timestamp].csv` - Available networks at a targer site
- `[SiteName]_hosts_[timestamp].csv` - Available hosts at a target site
- `[SiteName]_folders_[timestamp].csv` - Available folders at a target site
- `[SiteName]_vms_[timestamp].csv` - Available VMs at the local site to be protected at a target site

## Step 2: Update VPG Template

1. In the `examples/bulk_vpg_actions` directory, open `vpg_template.csv` and update it with the information from the exported resource files:
   - Use site names and IDs from `zerto_sites_[timestamp].csv`
   - Use datastore names and IDs from `[SiteName]_datastores_[timestamp].csv`
   - Use network names and IDs from `[SiteName]_networks_[timestamp].csv`
   - Use host/host cluster names and IDs from `[SiteName]_hosts_[timestamp].csv`
   - Use folder names and IDs from `[SiteName]_folders_[timestamp].csv`
   - Use VM names and IDs from `[SiteName]_vms_[timestamp].csv`
   * RECOMMENDATION: Create an excel file that references the resources above as "Data Validation with a List from a Table" feature.

2. The template includes fields for both host and host cluster configuration:
   - If using a specific host, fill in "Recovery Host Name" and "Recovery Host ID"
   - If using a host cluster, fill in "Recovery Host Cluster Name" and "Recovery Host Cluster ID"

## Step 3: Export Current VPG NIC Settings into a csv file

Export the current NIC settings of your VPGs to review and modify them:

```bash
cd examples/bulk_vpg_actions
python export_vpg_settings_nics_to_csv.py \
    --zvm_address "192.168.111.20" \
    --client_id "zerto-api" \
    --client_secret "your-secret-here" \
    --vpg_names "VpgTest1,VpgTest2" \
    --ignore_ssl \
    --output_dir "output_dir name/path"
```

This creates two files in the output_dir directory:
- `ExportedSettings_[timestamp].json` - Full VPG settings in JSON format
- `ExportedSettings_[timestamp].csv` - NIC settings in CSV format

## Step 4: Modify NIC Settings

1. In the `examples/bulk_vpg_actions` directory, open the exported CSV file (`ExportedSettings_[timestamp].csv`)
2. Modify the NIC settings as needed:
   - Set "Failover ShouldReplaceIpConfiguration" to "True" to modify IP settings
   - For DHCP:
     - Set "Failover DHCP" to "True"
     - Leave IP, Subnet, Gateway, and DNS fields empty
   - For Static IP:
     - Set "Failover DHCP" to "False"
     - Fill in IP, Subnet, Gateway, and DNS fields
   - Repeat for "Failover Test" settings if needed

Important Notes:
- You cannot have both DHCP and static IP settings enabled
- Must set "ShouldReplaceIpConfiguration" to "True" to modify IP settings
- Changes will be validated before applying

## Step 5: Import Updated NIC Settings

Apply the modified NIC settings to your VPGs:

```bash
cd examples/bulk_vpg_actions
python import_vpg_settings_nics_from_csv.py \
    --zvm_address "192.168.111.20" \
    --client_id "zerto-api" \
    --client_secret "your-secret-here" \
    --csv_file "output_dir/ExportedSettings_[timestamp].csv" \
    --vpg_names "VpgTest1,VpgTest2" \
    --ignore_ssl
```

The script will:
1. Validate all settings
2. Show proposed changes
3. Ask for confirmation before applying
4. Apply changes if confirmed

## File Structure

All scripts and templates are located in the `examples/bulk_vpg_actions` directory:
```
examples/bulk_vpg_actions/
├── README.md
├── export_site_resources_to_csv.py
├── export_vpg_settings_nics_to_csv.py
├── import_vpg_settings_nics_from_csv.py
├── vpg_template.csv
```

## Troubleshooting

1. SSL Certificate Issues:
   - Use `--ignore_ssl` flag if you have SSL certificate validation issues

2. API Authentication:
   - Refer to main README file in order to create your client_id and client_secret
   - Ensure your client_id and client_secret are correct
   - Verify you have proper permissions in Zerto

3. CSV Format Issues:
   - Ensure CSV files are saved with UTF-8 encoding
   - Don't modify the column headers
   - Use proper boolean values ("True"/"False")

4. Common Errors:
   - "VPG not found" - Check VPG names in the CSV
   - "Invalid configuration" - Review DHCP and IP settings
   - "Permission denied" - Check API credentials and permissions

## Security Notes

- Never commit API credentials to version control
- Use secure methods to store and transmit credentials
- Consider using environment variables for sensitive data
- Review and validate all changes before applying them

## Support

These scripts are provided as examples and are not supported under any Zerto support program or service. Use at your own risk. 