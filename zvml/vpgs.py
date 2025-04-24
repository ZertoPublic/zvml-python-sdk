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
import time
import json
from .tasks import Tasks
from .common import ZertoVPGStatus, ZertoVPGSubstatus, ZertoProtectedSiteType, ZertoRecoverySiteType, ZertoVPGPriority
from typing import Optional, Union, Dict, List

class VPGs:
    def __init__(self, client):
        self.client = client
        self.tasks = Tasks(client)

    def list_vpgs(self, 
                  vpg_name: str = None,
                  vpg_identifier: str = None,
                  status: ZertoVPGStatus = None,
                  sub_status: ZertoVPGSubstatus = None,
                  protected_site_type: ZertoProtectedSiteType = None,
                  recovery_site_type: ZertoRecoverySiteType = None,
                  protected_site_identifier: str = None,
                  recovery_site_identifier: str = None,
                  organization_name: str = None,
                  zorg_identifier: str = None,
                  priority: ZertoVPGPriority = None,
                  service_profile_identifier: str = None,
                  backup_enabled: bool = None) -> Dict | List[Dict]:
        """
        Get information about VPGs. If vpg_identifier or vpg_name is provided, returns a single VPG.
        Otherwise, returns a list of VPGs that match the filter criteria.

        Args:
            vpg_name: Get a specific VPG by name
            vpg_identifier: Get a specific VPG by identifier
            status: Filter by VPG status
            sub_status: Filter by VPG sub-status
            protected_site_type: The protected site type
            recovery_site_type: The recovery site type
            protected_site_identifier: The identifier of the protected site
            recovery_site_identifier: The identifier of the recovery site
            organization_name: Filter by ZORG name
            zorg_identifier: Filter by ZORG identifier
            priority: Filter by VPG priority
            service_profile_identifier: Filter by service profile ID
            backup_enabled: Deprecated parameter

        Returns:
            Dict: When vpg_identifier or vpg_name is provided
            List[Dict]: When filtering VPGs without specific identifier
        """
        # Construct the base URL
        if vpg_identifier:
            url = f"https://{self.client.zvm_address}/v1/vpgs/{vpg_identifier}"
        else:
            url = f"https://{self.client.zvm_address}/v1/vpgs"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        # Only include query parameters if we're not getting a specific VPG
        params = {}
        if not vpg_identifier:
            params = {
                'name': vpg_name,
                'status': status.get_name_by_value(status.value) if status else None,
                'subStatus': sub_status.get_name_by_value(sub_status.value) if sub_status else None,
                'protectedSiteType': protected_site_type.get_name_by_value(protected_site_type.value) if protected_site_type else None,
                'recoverySiteType': recovery_site_type.get_name_by_value(recovery_site_type.value) if recovery_site_type else None,
                'protectedSiteIdentifier': protected_site_identifier,
                'recoverySiteIdentifier': recovery_site_identifier,
                'organizationName': organization_name,
                'zorgIdentifier': zorg_identifier,
                'priority': priority.get_name_by_value(priority.value) if priority else None,
                'serviceProfileIdentifier': service_profile_identifier,
                'backupEnabled': backup_enabled
            }
            # Remove None values from params
            params = {k: v for k, v in params.items() if v is not None}

        logging.info(f"VPGs.list_vpgs: Fetching VPGs with parameters:")
        if vpg_identifier:
            logging.info(f"  vpg_identifier: {vpg_identifier}")
        for key, value in params.items():
            logging.info(f"  {key}: {value}")

        try:
            response = requests.get(
                url, 
                headers=headers, 
                params=params, 
                verify=self.client.verify_certificate,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # If we're querying by name, return the first matching VPG
            if vpg_name and isinstance(result, list):
                matching_vpg = next((vpg for vpg in result if vpg.get("VpgName") == vpg_name), None)
                if matching_vpg:
                    logging.info(f"Successfully retrieved VPG details for {vpg_name}")
                    return matching_vpg
                logging.warning(f"No VPG found with name {vpg_name}")
                return {}
            
            if vpg_identifier:
                logging.info(f"Successfully retrieved VPG details for {vpg_identifier}")
            else:
                logging.info(f"Successfully retrieved {len(result)} VPGs")
            
            return result

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

    def commit_vpg(self, vpg_settings_id, vpg_name, sync=False, expected_status=ZertoVPGStatus.Initializing, timeout=30, interval=5):
        logging.info(f'VPGs.commit_vpg(zvm_address={self.client.zvm_address}, vpg_settings_id={vpg_settings_id}, vpg_name={vpg_name}, sync={sync})')
        commit_uri = f"https://{self.client.zvm_address}/v1/vpgSettings/{vpg_settings_id}/commit"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            response = requests.post(commit_uri, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            task_id = response.json()
            logging.info(f"VPGSettings {vpg_settings_id} successfully committed, {vpg_name} is created, task_id={task_id}")

            if sync:
                # Wait for task completion
                self.tasks.wait_for_task_completion(task_id, timeout=timeout, interval=interval)
                logging.debug('sleeping 5 seconds ...')
                self.wait_for_vpg_ready(vpg_name=vpg_name, timeout=30, interval=5, expected_status=expected_status)
                return task_id
            return task_id

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

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    def create_vpg(self, basic, journal, recovery, networks, sync=True, status: ZertoVPGStatus = ZertoVPGStatus.Initializing, timeout=30, interval=5):
        vpg_name = basic.get("Name")
        logging.info(f'VPGs.create_vpg(zvm_address={self.client.zvm_address}, vpg_name={vpg_name}, sync={sync})')
        vpg_settings_id = self.create_vpg_settings(basic, journal, recovery, networks, vpg_identifier=None)
        return self.commit_vpg(vpg_settings_id, vpg_name, sync, expected_status=status, timeout=timeout, interval=interval)

    def wait_for_vpg_ready(self, vpg_name, timeout=180, interval=5, expected_status=ZertoVPGStatus.Initializing):
        logging.debug(f'VPGs.wait_for_vpg_ready(zvm_address={self.client.zvm_address}, vpg_name={vpg_name}, timeout={timeout}, interval={interval}, expected_status={ZertoVPGStatus.get_name_by_value(expected_status.value)})')
        start_time = time.time()

        while True:
            time.sleep(interval)
            vpg_info = self.list_vpgs(vpg_name=vpg_name)
            # get status and convert string into enum
            logging.debug(f"VPG status: {vpg_info.get('Status')}")
            vpg_status: ZertoVPGStatus = ZertoVPGStatus(vpg_info.get("Status"))
            logging.debug(f"Checking VPG status for {vpg_name}: Expected status = {ZertoVPGStatus.get_name_by_value(expected_status.value)}, Current status = {ZertoVPGStatus.get_name_by_value(vpg_status.value)}")

            # If VPG is in the expected status or passed the Initializing status too quickly and is in another status
            if vpg_status == expected_status or (expected_status == ZertoVPGStatus.Initializing and vpg_status.value > ZertoVPGStatus.Initializing.value):
                logging.info(f"VPG {vpg_name} is now in the expected state: {ZertoVPGStatus.get_name_by_value(vpg_status.value)}")
                return vpg_info

            # Check if the timeout has been reached
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                raise TimeoutError(f"VPG {vpg_name} did not reach the {ZertoVPGStatus.get_name_by_value(expected_status.value)} state within the allotted time. Current status: {ZertoVPGStatus.get_name_by_value(vpg_status.value)}")

    def add_vm_to_vpg(self, vpg_name, vm_list_payload):
        logging.info(f'VPGs.add_vm_to_vpg(zvm_address={self.client.zvm_address}, vpg_name={vpg_name})')
        vpg = self.list_vpgs(vpg_name=vpg_name)
        
        if not vpg:
            logging.error(f"VPG with name '{vpg_name}' not found.")
            return

        vpg_identifier = vpg['VpgIdentifier']
        logging.info(f"Found VPG '{vpg_name}' with Identifier: {vpg_identifier}")

        new_vpg_settings_id = self.create_vpg_settings(basic=None, journal=None, recovery=None, networks=None, vpg_identifier=vpg_identifier)

        logging.info(f"Adding VMs to VPGSettings ID: {new_vpg_settings_id}")
        logging.debug(f"VM List Payload: {json.dumps(vm_list_payload, indent=4)}")
        vms_uri = f"https://{self.client.zvm_address}/v1/vpgSettings/{new_vpg_settings_id}/vms"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            response = requests.post(vms_uri, headers=headers, json=vm_list_payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            logging.info(f"Successfully added VMs to VPG {new_vpg_settings_id}.")
            self.commit_vpg(new_vpg_settings_id, vpg_name, sync=True, expected_status=ZertoVPGStatus.Initializing)
            return 

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

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    def remove_vm_from_vpg(self, vpg_name, vm_identifier):
        logging.info(f'VPGs.remove_vm_from_vpg(zvm_address={self.client.zvm_address}, vpg_name={vpg_name}, vm_identifier={vm_identifier})')
        vpg = self.list_vpgs(vpg_name=vpg_name)

        if not vpg:
            logging.error(f"VPG with name '{vpg_name}' not found.")
            return

        vpg_id = vpg['VpgIdentifier']
        logging.info(f"Found VPG '{vpg_name}' with Identifier: {vpg_id}")

        new_vpg_settings_id = self.create_vpg_settings(basic=None, journal=None, recovery=None, networks=None, vpg_identifier=vpg_id)
        remove_vm_uri = f"https://{self.client.zvm_address}/v1/vpgSettings/{new_vpg_settings_id}/vms/{vm_identifier}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            response = requests.delete(remove_vm_uri, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            logging.info(f"VM {vm_identifier} successfully removed from VPG '{vpg_name}' (ID: {new_vpg_settings_id}).")
            self.commit_vpg(new_vpg_settings_id, vpg_name, sync=True, expected_status=ZertoVPGStatus.Initializing)

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

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    def failover_test(self, vpg_name, checkpoint_identifier=None, vm_name_list=None, sync=True):
        """
        Initiate a failover test for a given VPG by its name.

        :param vpg_name: The name of the VPG.
        :param checkpoint_identifier: checkpoint_identifier can be recived by list_checkpoint, if not provided uses the latest checkpoint.
        :param vm_name_list: List of 
        :param options: Optional parameters for the failover test.
        :return: Response from the Zerto API.
        """
        logging.info(f'VPGs.failover_test(zvm_address={self.client.zvm_address}, vpg_name={vpg_name}, checkpoint_identifier={checkpoint_identifier}, vm_name_list={vm_name_list}, sync={sync})')

        # Retrieve the VPG identifier using the VPG name
        vpg_info = self.list_vpgs(vpg_name=vpg_name)
        vpg_identifier = vpg_info['VpgIdentifier']
        logging.debug(f"Found VPG '{vpg_name}' with Identifier: {vpg_identifier}")

        url = f"https://{self.client.zvm_address}/v1/vpgs/{vpg_identifier}/FailoverTest"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        payload = {}
        if checkpoint_identifier: payload['CheckpointIdentifier'] = checkpoint_identifier

        vm_identifier_list = []
        if vm_name_list:
            
            for vm in vm_name_list:
                vm_info = self.list_vms(vm_name=vm)
                if not vm_info:
                    logging.error (f'failover_test vm={vm} not found')
                    return
                vm_identifier_list.append(vm_info[0]['VmIdentifier'])
        
        payload['VmIdentifiers'] = vm_identifier_list

        try:
            logging.info(f"Initiating failover test for VPG '{vpg_name}', payload={payload}")
            response = requests.post(url, headers=headers, json=payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            task_id = response.json()

            logging.info(f"Failover test initiated for VPG {vpg_name}, task_id = {task_id}")

            if sync:
                # Wait for task completion
                self.tasks.wait_for_task_completion(task_id, timeout=30, interval=5)
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

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    def stop_failover_test(self, vpg_name, failoverTestSuccess=True, failoverTestSummary=None, sync=True):
        """
        Stop a failover test for a given VPG by its name.

        :param vpg_name: The name of the VPG.
        :param sync: wait until task is completed.

        """
        logging.info(f'VPGs.stop_failover_test(zvm_address={self.client.zvm_address}, vpg_name={vpg_name}, sync={sync})')

        # Retrieve the VPG identifier using the VPG name
        vpg_info = self.list_vpgs(vpg_name=vpg_name)
        vpg_identifier = vpg_info['VpgIdentifier']
        logging.info(f"Found VPG '{vpg_name}' with Identifier: {vpg_identifier}")

        url = f"https://{self.client.zvm_address}/v1/vpgs/{vpg_identifier}/FailoverTestStop"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        body = {
            "FailoverTestSuccess": failoverTestSuccess,
            "FailoverTestSummary": failoverTestSummary
        }

        try:
            logging.info(f"Stopping failover test for VPG '{vpg_name}'...")
            response = requests.post(url, headers=headers, json=body, verify=self.client.verify_certificate)
            response.raise_for_status()
            task_id = response.json()

            logging.info(f"Failover test stopping for VPG {vpg_name}, task_id = {task_id}")

            if sync:
                # Wait for task completion
                self.tasks.wait_for_task_completion(task_id, timeout=30, interval=5)
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

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    def rollback_failover(self, vpg_name, sync=True):
        """
        Rollback failover for a given VPG by its name.

        :param vpg_name: The name of the VPG.
        :param sync: wait until task is completed.

        """
        logging.info(f'VPGs.rollback_failover(zvm_address={self.client.zvm_address}, vpg_name={vpg_name}, sync={sync})')

        # Retrieve the VPG identifier using the VPG name
        vpg_info = self.list_vpgs(vpg_name=vpg_name)
        vpg_identifier = vpg_info['VpgIdentifier']
        logging.info(f"Found VPG '{vpg_name}' with Identifier: {vpg_identifier}")

        url = f"https://{self.client.zvm_address}/v1/vpgs/{vpg_identifier}/FailoverRollback"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            logging.info(f"Rollback failover for VPG '{vpg_name}'...")
            response = requests.post(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            task_id = response.json()

            logging.info(f"Rollback faolover for VPG {vpg_name}, task_id = {task_id}")

            if sync:
                # Wait for task completion
                self.tasks.wait_for_task_completion(task_id, timeout=30, interval=5)
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

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    def delete_vpg(self, vpg_name, force=False, keep_recovery_volumes=True):
        """
        Deletes a VPG by its name.

        :param vpg_name: The name of the VPG to delete.
        :return: Success message if deleted, else an error message.
        """
        logging.info(f"VPGs.delete_vpg(zvm_address={self.client.zvm_address}, vpg_name={vpg_name}, force={force}, keep_recovery_volumes={keep_recovery_volumes})")

        # Step 1: Retrieve the VPG details using the VPG name
        vpg = self.list_vpgs(vpg_name=vpg_name)

        if not vpg:
            logging.error(f"No VPG found with the name '{vpg_name}'.")
            return

        # Get the VPG Identifier
        vpg_identifier = vpg.get("VpgIdentifier")
        if not vpg_identifier:
            logging.error(f"Could not retrieve Identifier for VPG '{vpg_name}'.")
            return

        # Step 2: Construct the DELETE request URL
        delete_vpg_uri = f"https://{self.client.zvm_address}/v1/vpgs/{vpg_identifier}"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        payload = {
            "keepRecoveryVolumes": force,
            "force": keep_recovery_volumes
        }

        try:
            # Step 3: Send DELETE request
            response = requests.delete(delete_vpg_uri, headers=headers, json=payload, verify=self.client.verify_certificate)

            response.raise_for_status()  # Ensure the request was successful
            logging.info(f"Successfully deleted VPG '{vpg_name}' (ID: {vpg_identifier}).")
            return f"VPG '{vpg_name}' deleted successfully."

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

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    # Added methods from VPGSettings
    def list_vpg_settings(self):
        url = f"https://{self.client.zvm_address}/v1/vpgs/settings"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to list VPG settings: {e}")
            raise

    def get_vpg_settings_by_id(self, vpg_settings_id):
        url = f"https://{self.client.zvm_address}/v1/vpgSettings/{vpg_settings_id}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get VPG settings by ID: {e}")
            raise

    def update_vpg_settings(self, vpg_settings_id, payload):
        url = f"https://{self.client.zvm_address}/v1/vpgSettings/{vpg_settings_id}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        logging.info(f"VPGs.update_vpg_settings: Updating VPG settings for ID: {vpg_settings_id}")
        logging.debug(f"VPGs.update_vpg_settings: Payload: {json.dumps(payload, indent=4)}")
        try:
            response = requests.put(url, json=payload, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            return response
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

    def delete_vpg_settings(self, vpg_settings_id):
        url = f"https://{self.client.zvm_address}/v1/vpgs/settings/{vpg_settings_id}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.delete(url, headers=headers, verify=self.client.verify_certificate)
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

    def create_vpg_settings(self, basic=None, journal=None, recovery=None, networks=None, vpg_identifier=None):
        logging.info(f'VPGs.create_vpg_settings(zvm_address={self.client.zvm_address}, vpg_identifier={vpg_identifier})')
        vpg_settings_uri = f"https://{self.client.zvm_address}/v1/vpgSettings"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        payload = {}
        if vpg_identifier:
            payload["vpgIdentifier"] = vpg_identifier
        if basic: 
            payload["Basic"] = basic
        if journal:
            payload["Journal"] = journal
        if recovery:
            payload["Recovery"] = recovery
        if networks:
            payload["Networks"] = networks

        logging.debug(f"VPGs.create_vpg_settings: Payload: {json.dumps(payload, indent=4)}")
        try:
            response = requests.post(vpg_settings_uri, headers=headers, json=payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            vpg_settings_id = response.json()
            logging.info(f"VPG Settings ID: {vpg_settings_id} created")
            return vpg_settings_id
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
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    def list_checkpoints(self, vpg_name, start_date=None, endd_date=None, checkpoint_date_str=None, latest=None):
        """
        Fetches a list of checkpoints for a specified Virtual Protection Group (VPG).
        
        Parameters:
            vpg_name (str): The name of the Virtual Protection Group (VPG) to fetch checkpoints for.
            start_date (str): The start date for filtering checkpoints, in ISO 8601 format (e.g., '2024-11-13T00:00:00Z').
            endd_date (str): The end date for filtering checkpoints, in ISO 8601 format (e.g., '2024-11-14T00:00:00Z').
            checkpoint_date_str (str): A specific date string in the format 'Month Day, Year HH:MM:SS AM/PM'
                                    (e.g., 'November 13, 2024 1:43:02 PM') to search for an exact checkpoint.
            latest (bool): If True, returns the checkpoint with the most recent timestamp.

        Returns:
            dict: A single checkpoint that matches `checkpoint_date_str` or the latest checkpoint if `latest=True`.
            list: The full list of checkpoints if neither `checkpoint_date_str` nor `latest` is specified.
            None: If no matching checkpoint is found or an error occurs.
        
        Raises:
            SystemExit: If a request exception occurs during the API call.
        """        
        logging.info(f'VPGs.list_checkpoints(vpg_name={vpg_name}, start_date={start_date}, endd_date={endd_date}, checkpoint_date_str={checkpoint_date_str}, latest={latest})')
        vpgid = (self.list_vpgs(vpg_name=vpg_name))['VpgIdentifier']
        vpgs_uri = f"https://{self.client.zvm_address}/v1/vpgs/{vpgid}/checkpoints"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        params = {
            "startDate": start_date,
            "endDate": endd_date
        }
        try:
            response = requests.get(vpgs_uri, headers=headers, params=params, verify=self.client.verify_certificate)
            response.raise_for_status()
            checkpoints = response.json()

            if not checkpoints:
                logging.warning("No checkpoints found.")
                return []

            if checkpoint_date_str:
                check_point_timestamp = self.__convert_datetime_to_timestamp(date_str = checkpoint_date_str)
                matching_checkpoints = next((checkpoint for checkpoint in checkpoints if checkpoint.get("TimeStamp") == check_point_timestamp), None)
                if not check_point_timestamp:
                    logging.warning(f"No checkpoint {checkpoint_date_str} found")
                    return {}
                return matching_checkpoints
            
            if latest:
                # Find the checkpoint with the most recent timestamp
                latest_checkpoint = max(checkpoints, key=lambda x: x.get("TimeStamp"))
                logging.debug(f"Latest checkpoint found: {latest_checkpoint}")
                return latest_checkpoint  

            return checkpoints

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

    def create_checkpoint(self, checkpoint_name: str, vpg_identifier: str = None, vpg_name: str = None) -> str:
        """
        Create a tagged checkpoint for the VPG.

        Args:
            checkpoint_name: The name/tag to assign to the checkpoint
            vpg_identifier: The identifier of the VPG
            vpg_name: The name of the VPG (alternative to vpg_identifier)

        Returns:
            str: The task identifier that can be used to monitor the operation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If neither vpg_identifier nor vpg_name is provided, or if VPG name is not found
        """
        if not vpg_identifier and not vpg_name:
            raise ValueError("Either vpg_identifier or vpg_name must be provided")

        # If vpg_name is provided, get the vpg_identifier
        if vpg_name and not vpg_identifier:
            vpg = self.list_vpgs(vpg_name=vpg_name)
            if not vpg:
                raise ValueError(f"VPG with name '{vpg_name}' not found")
            vpg_identifier = vpg.get('VpgIdentifier')
            logging.info(f"Found VPG identifier '{vpg_identifier}' for VPG name '{vpg_name}'")

        url = f"https://{self.client.zvm_address}/v1/vpgs/{vpg_identifier}/checkpoints"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        data = {
            "CheckpointName": checkpoint_name
        }

        logging.info(f"VPGs.create_checkpoint: Creating checkpoint '{checkpoint_name}' for VPG {vpg_identifier}")

        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                verify=self.client.verify_certificate,
                timeout=30
            )
            response.raise_for_status()
            task_id = response.json()
            logging.info(f"Successfully initiated checkpoint creation, task_id={task_id}")
            return task_id

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

    def export_vpg_settings(self, vpg_names: List[str]) -> dict:
        """
        Export settings for specified VPGs.

        Args:
            vpg_names: List of VPG names to export settings for

        Returns:
            dict: The exported VPG settings in the format:
                {
                    "timeStamp": "2025-02-08T21:50:46.574Z",
                    "exportResult": {
                        "result": str,
                        "message": str
                    }
                }

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/vpgSettings/exportSettings"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        payload = {
            "vpgNames": vpg_names
        }

        logging.info(f"VPGs.export_vpg_settings: Exporting settings for VPGs: {vpg_names}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Successfully exported settings for {len(vpg_names)} VPGs at {result.get('timeStamp')}")
            logging.debug(f"Export result: {json.dumps(result, indent=2)}")
            return result
        
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

    def list_exported_vpg_settings(self) -> List[Dict]:
        """
        Get all available exported settings files.

        Returns:
            List[Dict]: List of exported settings files in the format:
                [
                    {
                        "timeStamp": "2025-02-08T22:02:18.685Z"
                    }
                ]

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/vpgSettings/exportedSettings"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        logging.debug("Fetching list of exported VPG settings")
        
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Found {len(result)} exported settings files")
            logging.debug(f"Exported settings list: {json.dumps(result, indent=2)}")
            return result
        
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

    def read_exported_vpg_settings(self, timestamp: str, vpg_names: List[str] = None) -> dict:
        """
        Read exported settings from a file of given timestamp.

        Args:
            timestamp: The timestamp of the exported settings file (format: YYYY-MM-DDThh:mm:ss.SSSZ)
            vpg_names: Optional list of VPG names to filter the exported settings

        Returns:
            dict: The exported VPG settings containing:
                - ExportedVpgSettingsApi: List[dict] - List of VPG settings
                - ErrorMessage: str - Error message if any

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/vpgSettings/exportedSettings/{timestamp}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        payload = {}
        if vpg_names:
            payload['vpgNames'] = vpg_names

        logging.info(f"VPGs.read_exported_vpg_settings: Reading exported VPG settings for timestamp: {timestamp}")
        if vpg_names:
            logging.debug(f"Filtering for VPGs: {vpg_names}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.debug(f"VPGs.read_exported_vpg_settings: result: {json.dumps(result, indent=4)}")
            
            return result
            
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

    def import_vpg_settings(self, settings: Dict) -> dict:

    
        """
        Import VPG settings.

        Args:
            settings: Dictionary containing the VPG settings to import. Must include:
                - ExportedVpgSettingsApi: List of VPG settings with detailed configuration

        Returns:
            dict: The import result containing:
                - validationFailedResults: List[dict] - VPGs that failed validation
                    - vpgName: str - Name of the VPG
                    - errorMessages: List[str] - List of validation error messages
                - importFailedResults: List[dict] - VPGs that failed to import
                    - vpgName: str - Name of the VPG
                    - errorMessage: str - Import error message
                - importTaskIdentifiers: List[dict] - Successfully initiated imports
                    - vpgName: str - Name of the VPG
                    - taskIdentifier: str - Task ID for tracking the import

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If settings dictionary is missing required fields
        """
        url = f"https://{self.client.zvm_address}/v1/vpgSettings/import"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        # Validate input settings
        if not isinstance(settings, dict):
            raise ValueError("Settings must be a dictionary")
        if 'ExportedVpgSettingsApi' not in settings:
            raise ValueError("Settings must contain 'ExportedVpgSettingsApi' key")

        # Prepare payload
        payload = {
            "ExportedVpgSettingsApi": settings['ExportedVpgSettingsApi']
        }

        logging.info(f"VPGs.import_vpg_settings: Importing settings for {len(settings['ExportedVpgSettingsApi'])} VPGs")
        
        try:
            response = requests.post(url, headers=headers, json=payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.debug(f"VPGs.import_vpg_settings: result: {json.dumps(result, indent=4)}")
            
            # Log validation failures
            if result.get('validationFailedResults'):
                for failure in result['validationFailedResults']:
                    logging.error(f"Validation failed for VPG '{failure['vpgName']}': {', '.join(failure['errorMessages'])}")
            
            # Log import failures
            if result.get('importFailedResults'):
                for failure in result['importFailedResults']:
                    logging.error(f"Import failed for VPG '{failure['vpgName']}': {failure['errorMessage']}")
            
            # Log successful imports
            if result.get('importTaskIdentifiers'):
                for task in result['importTaskIdentifiers']:
                    logging.info(f"Import initiated for VPG '{task['vpgName']}' with task ID: {task['taskIdentifier']}")
            
            logging.debug(f"Import result: {json.dumps(result, indent=2)}")
            
            return result
            
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

    def list_vpgs_from_exported_settings(self, time_stamp: str) -> List[Dict]:
        """List VPGs from exported settings.
        
        Args:
            time_stamp: Timestamp of the exported settings
            
        Returns:
            List[Dict]: List of VPGs in the format:
                [
                    {
                        "VpgName": "test",
                        "SourceSiteName": "Production",
                        "TargetSiteName": "DR"
                    }
                ]
        """
        url = f"https://{self.client.zvm_address}/v1/vpgSettings/exportedSettings/{time_stamp}/vpgsinfo"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        logging.info(f"VPGs.list_vpgs_from_exported_settings: Fetching VPGs from export {time_stamp}")
        
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Successfully retrieved {len(result)} VPGs from export {time_stamp}")
            logging.debug(f"VPGs from export: {json.dumps(result, indent=2)}")
            return result
            
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

  