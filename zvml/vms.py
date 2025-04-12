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

import requests
import logging
import json

class VMs:
    def __init__(self, client):
        self.client = client

    def list_vms(self, vm_identifier=None, vpg_name=None, vm_name=None, status=None, sub_status=None, 
                 
                 protected_site_type=None, recovery_site_type=None, protected_site_identifier=None, 
                 recovery_site_identifier=None, organization_name=None, priority=None, 
                 vpg_identifier=None, include_backuped_vms=None, include_mounted_vms=True):
        """
        Get information about protected virtual machines. If vm_identifier is provided,
        returns details about a specific VM, otherwise returns a filtered list of VMs. (Auth)
        
        Args:
            vm_identifier (str, optional): The identifier of a specific VM to get information about
            vpg_name (str, optional): The name of the VPG
            vm_name (str, optional): The name of the VM
            status (str, optional): The status of the VPG
            sub_status (str, optional): The sub-status of the VPG
            protected_site_type (str, optional): The protected site type
            recovery_site_type (str, optional): The recovery site type
            protected_site_identifier (str, optional): The identifier of the protected site
            recovery_site_identifier (str, optional): The identifier of the recovery site
            organization_name (str, optional): The ZORG name
            priority (str, optional): The VPG priority
            vpg_identifier (str, optional): The identifier of the VPG (used with vm_identifier)
            include_backuped_vms (bool, optional): Include VMs in backup targets
            include_mounted_vms (bool, optional): Include mounted VMs in the response
        
        Returns:
            dict or list: Details of a specific VM if vm_identifier is provided,
                         otherwise an array of protected VMs matching the filter criteria
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        # Build the URL based on whether we're getting a specific VM or listing VMs
        base_url = f"https://{self.client.zvm_address}/v1/vms"
        url = f"{base_url}/{vm_identifier}" if vm_identifier else base_url
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        # Build params based on whether we're getting a specific VM or listing VMs
        if vm_identifier:
            params = {
                'vpgIdentifier': vpg_identifier,
                'includeBackupedVms': include_backuped_vms,
                'includeMountedVms': include_mounted_vms
            }
            log_msg = f"VMs.list_vms: Fetching VM {vm_identifier}"
        else:
            params = {
                'vpgName': vpg_name,
                'vmName': vm_name,
                'status': status,
                'subStatus': sub_status,
                'protectedSiteType': protected_site_type,
                'recoverySiteType': recovery_site_type,
                'protectedSiteIdentifier': protected_site_identifier,
                'recoverySiteIdentifier': recovery_site_identifier,
                'organizationName': organization_name,
                'priority': priority,
                'vmIdentifier': vm_identifier,
                'includeBackupedVms': include_backuped_vms,
                'includeMountedVms': include_mounted_vms
            }
            log_msg = "VMs.list_vms: Fetching VMs"
        
        # Remove None values from params
        params = {k: v for k, v in params.items() if v is not None}
        
        logging.info(f"{log_msg} with params: {params}")
        try:
            response = requests.get(url, headers=headers, params=params, verify=self.client.verify_certificate)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                logging.error(f"HTTPError: {e.response.status_code} - {e.response.reason}")
                try:
                    error_details = e.response.json()
                    logging.error(f"Error Message: {error_details.get('Message', 'No detailed error message available')}")
                except ValueError:
                    logging.error(f"Response content: {e.response.text}")
            else:
                logging.error("HTTPError occurred with no response attached.")
            raise

    def restore_vm(self, vm_identifier, vpg_identifier, restored_vm_name, checkpoint_identifier, 
                  journal_vm_restore_settings, commit_policy=0, shutdown_policy=0, 
                  time_to_wait_before_continue_in_seconds=0):
        """
        Restore a VM from a specific checkpoint. (Auth)
        
        Args:
            vm_identifier (str): The identifier of the VM to restore
            vpg_identifier (str): The identifier of the VPG
            restored_vm_name (str): The name for the restored VM
            checkpoint_identifier (str): The identifier of the checkpoint to restore from
            journal_vm_restore_settings (dict): Settings for the restored VM with structure:
                {
                    "datastoreIdentifier": str,
                    "nics": [
                        {
                            "hypervisor": {
                                "dnsSuffix": str,
                                "ipConfig": {
                                    "gateway": str,
                                    "isDhcp": bool,
                                    "primaryDns": str,
                                    "secondaryDns": str,
                                    "staticIp": str,
                                    "subnetMask": str
                                },
                                "networkIdentifier": str,
                                "shouldReplaceMacAddress": bool
                            },
                            "nicIdentifier": str
                        }
                    ],
                    "volumes": [
                        {
                            "datastore": {
                                "datastoreIdentifier": str,
                                "isThin": bool
                            },
                            "volumeIdentifier": str
                        }
                    ]
                }
            commit_policy (int, optional): The commit policy. Defaults to 0
            shutdown_policy (int, optional): The shutdown policy. Defaults to 0
            time_to_wait_before_continue_in_seconds (int, optional): Time to wait before continuing. Defaults to 0
        
        Returns:
            dict: Response from the server
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/vms/{vm_identifier}/Restore"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        data = {
            "vpgIdentifier": vpg_identifier,
            "restoredVmName": restored_vm_name,
            "checkpointIdentifier": checkpoint_identifier,
            "commitPolicy": commit_policy,
            "shutdownPolicy": shutdown_policy,
            "timeToWaitBeforeContinueInSeconds": time_to_wait_before_continue_in_seconds,
            "journalVMRestoreSettings": journal_vm_restore_settings
        }
        logging.info(f"VMs.restore_vm: Restoring VM {vm_identifier} from checkpoint {checkpoint_identifier}")
        logging.info(f"VMs.restore_vm: Data: {json.dumps(data, indent=2)}")
        try:
            response = requests.post(url, headers=headers, json=data, verify=self.client.verify_certificate)
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                logging.error(f"HTTPError: {e.response.status_code} - {e.response.reason}")
                try:
                    error_details = e.response.json()
                    logging.error(f"Error Message: {error_details.get('Message', 'No detailed error message available')}")
                except ValueError:
                    logging.error(f"Response content: {e.response.text}")
            else:
                logging.error("HTTPError occurred with no response attached.")
            raise

    def restore_vm_commit(self, vm_identifier):
        """
        Commit a restored VM. (Auth)
        
        Args:
            vm_identifier (str): The identifier of the VM to commit
        
        Returns:
            dict: Response from the server if any
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/vms/{vm_identifier}/RestoreCommit"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VMs.restore_vm_commit: Committing restored VM {vm_identifier}")
        try:
            response = requests.post(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                logging.error(f"HTTPError: {e.response.status_code} - {e.response.reason}")
                try:
                    error_details = e.response.json()
                    logging.error(f"Error Message: {error_details.get('Message', 'No detailed error message available')}")
                except ValueError:
                    logging.error(f"Response content: {e.response.text}")
            else:
                logging.error("HTTPError occurred with no response attached.")
            raise

    def restore_vm_rollback(self, vm_identifier):
        """
        Rollback a restored VM. (Auth)
        
        Args:
            vm_identifier (str): The identifier of the VM to rollback
        
        Returns:
            dict: Response from the server if any
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/vms/{vm_identifier}/RestoreRollback"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VMs.restore_vm_rollback: Rolling back restored VM {vm_identifier}")
        try:
            response = requests.post(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                logging.error(f"HTTPError: {e.response.status_code} - {e.response.reason}")
                try:
                    error_details = e.response.json()
                    logging.error(f"Error Message: {error_details.get('Message', 'No detailed error message available')}")
                except ValueError:
                    logging.error(f"Response content: {e.response.text}")
            else:
                logging.error("HTTPError occurred with no response attached.")
            raise

    def list_vm_points_in_time(self, vm_identifier, vpg_identifier=None, start_date=None, end_date=None):
        """
        Get points in time for a specific VM. (Auth)
        
        Args:
            vm_identifier (str): The identifier of the VM
            vpg_identifier (str, optional): The identifier of the VPG
            start_date (str, optional): The filter interval start date-time
            end_date (str, optional): The filter interval end date-time
        
        Returns:
            list: Array of points in time for the specified VM
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/vms/{vm_identifier}/pointsInTime"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        params = {
            'vpgIdentifier': vpg_identifier,
            'startDate': start_date,
            'endDate': end_date
        }
        # Remove None values from params
        params = {k: v for k, v in params.items() if v is not None}
        
        logging.info(f"VMs.list_vm_points_in_time: Fetching points in time for VM {vm_identifier}")
        try:
            response = requests.get(url, headers=headers, params=params, verify=self.client.verify_certificate)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                logging.error(f"HTTPError: {e.response.status_code} - {e.response.reason}")
                try:
                    error_details = e.response.json()
                    logging.error(f"Error Message: {error_details.get('Message', 'No detailed error message available')}")
                except ValueError:
                    logging.error(f"Response content: {e.response.text}")
            else:
                logging.error("HTTPError occurred with no response attached.")
            raise

    def list_vm_points_in_time_stats(self, vm_identifier, vpg_identifier=None):
        """
        Get the earliest and latest points in time for the VM. (Auth)
        VpgId may be required if the VM is protected by more than one VPG.
        
        Args:
            vm_identifier (str): The identifier of the VM
            vpg_identifier (str, optional): The identifier of the VPG which protects the VM
        
        Returns:
            dict: Statistics about the earliest and latest points in time for the VM
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/vms/{vm_identifier}/pointsInTime/stats"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        params = {'vpgIdentifier': vpg_identifier} if vpg_identifier else {}
        
        logging.info(f"VMs.list_vm_points_in_time_stats: Fetching points in time stats for VM {vm_identifier}")
        try:
            response = requests.get(url, headers=headers, params=params, verify=self.client.verify_certificate)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                logging.error(f"HTTPError: {e.response.status_code} - {e.response.reason}")
                try:
                    error_details = e.response.json()
                    logging.error(f"Error Message: {error_details.get('Message', 'No detailed error message available')}")
                except ValueError:
                    logging.error(f"Response content: {e.response.text}")
            else:
                logging.error("HTTPError occurred with no response attached.")
            raise