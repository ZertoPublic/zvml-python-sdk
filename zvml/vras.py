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
from typing import Dict, List, Optional

class VRA:
    def __init__(self, client):
        self.client = client

    def list_vras(self) -> List[Dict]:
        """List all VRAs."""
        logging.info(f"VRA.list_vras(zvm_address={self.client.zvm_address})")
        url = f"https://{self.client.zvm_address}/v1/vras"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Successfully retrieved {len(result)} VRAs")
            logging.debug(f"VRA.list_vras result: {json.dumps(result, indent=4)}")
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

    def create_vra(self, payload: Dict, sync: bool = True) -> Dict:
        """Create a new VRA.
        
        Args:
            payload: The VRA configuration
            sync: If True, wait for task completion (default: True)
        
        Returns:
            Dict: The creation result
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.create_vra(zvm_address={self.client.zvm_address}, sync={sync})")
        logging.debug(f"VRA.create_vra payload: {json.dumps(payload, indent=4)}")
        url = f"https://{self.client.zvm_address}/v1/vras"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.post(url, headers=headers, json=payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            task_id = response.json()
            logging.info("Successfully initiated VRA creation")
            logging.debug(f"VRA.create_vra task_id: {task_id}")

            if sync:
                # Wait for task completion
                self.client.tasks.wait_for_task_completion(task_id, timeout=300, interval=5)
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

    def get_vra(self, vra_identifier: str) -> Dict:
        """
        Get information about a specific VRA.

        Args:
            vra_identifier: The identifier of the VRA to retrieve

        Returns:
            Dict: The VRA information

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.get_vra(zvm_address={self.client.zvm_address}, vra_identifier={vra_identifier})")
        url = f"https://{self.client.zvm_address}/v1/vras/{vra_identifier}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Successfully retrieved VRA information for identifier: {vra_identifier}")
            logging.debug(f"VRA.get_vra result: {json.dumps(result, indent=4)}")
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

    def delete_vra(self, vra_identifier: str, sync: bool = True) -> Dict:
        """
        Delete a specific VRA.

        Args:
            vra_identifier: The identifier of the VRA to delete
            sync: If True, wait for task completion (default: True)

        Returns:
            Dict: The deletion result

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.delete_vra(zvm_address={self.client.zvm_address}, vra_identifier={vra_identifier})")
        url = f"https://{self.client.zvm_address}/v1/vras/{vra_identifier}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.delete(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            task_id = response.json()
            logging.info(f"Successfully initiated deletion of VRA with identifier: {vra_identifier}")
            logging.debug(f"VRA.delete_vra task_id: {task_id}")

            if sync:
                # Wait for task completion
                self.client.tasks.wait_for_task_completion(task_id, timeout=300, interval=5)
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

    def update_vra(self, vra_identifier: str, payload: Dict, sync: bool = True) -> Dict:
        """
        Update a specific VRA's configuration.

        Args:
            vra_identifier: The identifier of the VRA to update
            payload: The update configuration
            sync: If True, wait for task completion (default: True)

        Returns:
            Dict: The update result

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.update_vra(zvm_address={self.client.zvm_address}, vra_identifier={vra_identifier})")
        logging.debug(f"VRA.update_vra payload: {json.dumps(payload, indent=4)}")
        url = f"https://{self.client.zvm_address}/v1/vras/{vra_identifier}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.put(url, headers=headers, json=payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            task_id = response.json()
            logging.info(f"Successfully initiated update for VRA with identifier: {vra_identifier}")
            logging.debug(f"VRA.update_vra task_id: {task_id}")

            if sync:
                # Wait for task completion
                self.client.tasks.wait_for_task_completion(task_id, timeout=300, interval=5)
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

    def create_vra_cluster(self, payload: Dict, sync: bool = True) -> Dict:
        """
        Create a new VRA cluster.

        Args:
            payload: The cluster configuration
            sync: If True, wait for task completion (default: True)

        Returns:
            Dict: The creation result

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.create_vra_cluster(zvm_address={self.client.zvm_address})")
        logging.debug(f"VRA.create_vra_cluster payload: {json.dumps(payload, indent=4)}")
        url = f"https://{self.client.zvm_address}/v1/vras/clusters"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.post(url, headers=headers, json=payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            task_id = response.json()
            logging.info("Successfully initiated VRA cluster creation")
            logging.debug(f"VRA.create_vra_cluster task_id: {task_id}")

            if sync:
                # Wait for task completion
                self.client.tasks.wait_for_task_completion(task_id, timeout=300, interval=5)
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

    def delete_vra_cluster(self, cluster_identifier: str) -> Dict:
        """
        Delete a VRA cluster.

        Args:
            cluster_identifier: The identifier of the cluster to delete

        Returns:
            Dict: The deletion result

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.delete_vra_cluster(zvm_address={self.client.zvm_address}, cluster_identifier={cluster_identifier})")
        url = f"https://{self.client.zvm_address}/v1/vras/clusters/{cluster_identifier}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.delete(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Successfully deleted VRA cluster with identifier: {cluster_identifier}")
            logging.debug(f"VRA.delete_vra_cluster result: {json.dumps(result, indent=4)}")
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

    def update_vra_cluster(self, cluster_identifier: str, payload: Dict) -> Dict:
        """
        Update a VRA cluster configuration.

        Args:
            cluster_identifier: The identifier of the cluster to update
            payload: The update configuration

        Returns:
            Dict: The update result

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.update_vra_cluster(zvm_address={self.client.zvm_address}, cluster_identifier={cluster_identifier})")
        logging.debug(f"VRA.update_vra_cluster payload: {json.dumps(payload, indent=4)}")
        url = f"https://{self.client.zvm_address}/v1/vras/clusters/{cluster_identifier}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.put(url, headers=headers, json=payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Successfully updated VRA cluster with identifier: {cluster_identifier}")
            logging.debug(f"VRA.update_vra_cluster result: {json.dumps(result, indent=4)}")
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

    def cleanup_vras(self) -> Dict:
        """
        Clean up VRAs.

        Returns:
            Dict: The cleanup result

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.cleanup_vras(zvm_address={self.client.zvm_address})")
        url = f"https://{self.client.zvm_address}/v1/vras/cleanup"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.delete(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info("Successfully cleaned up VRAs")
            logging.debug(f"VRA.cleanup_vras result: {json.dumps(result, indent=4)}")
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

    def upgrade_vra(self, vra_identifier: str) -> Dict:
        """
        Upgrade a specific VRA.

        Args:
            vra_identifier: The identifier of the VRA to upgrade

        Returns:
            Dict: The upgrade result

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.upgrade_vra(zvm_address={self.client.zvm_address}, vra_identifier={vra_identifier})")
        url = f"https://{self.client.zvm_address}/v1/vras/{vra_identifier}/upgrade"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.post(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Successfully initiated upgrade for VRA with identifier: {vra_identifier}")
            logging.debug(f"VRA.upgrade_vra result: {json.dumps(result, indent=4)}")
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

    def get_vra_cluster_settings(self, cluster_identifier: str) -> Dict:
        """
        Get settings for a specific VRA cluster.

        Args:
            cluster_identifier: The identifier of the cluster to get settings for

        Returns:
            Dict: The cluster settings

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.get_vra_cluster_settings(zvm_address={self.client.zvm_address}, cluster_identifier={cluster_identifier})")
        url = f"https://{self.client.zvm_address}/v1/vras/clusters/{cluster_identifier}/settings"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Successfully retrieved VRA cluster settings for identifier: {cluster_identifier}")
            logging.debug(f"VRA.get_vra_cluster_settings result: {json.dumps(result, indent=4)}")
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

    def create_vra_cluster_settings(self, cluster_identifier: str, payload: Dict) -> Dict:
        """
        Create settings for a VRA cluster.

        Args:
            cluster_identifier: The identifier of the cluster to create settings for
            payload: The cluster settings configuration

        Returns:
            Dict: The creation result

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.create_vra_cluster_settings(zvm_address={self.client.zvm_address}, cluster_identifier={cluster_identifier})")
        logging.debug(f"VRA.create_vra_cluster_settings payload: {json.dumps(payload, indent=4)}")
        url = f"https://{self.client.zvm_address}/v1/vras/clusters/{cluster_identifier}/settings"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.post(url, headers=headers, json=payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Successfully created VRA cluster settings for identifier: {cluster_identifier}")
            logging.debug(f"VRA.create_vra_cluster_settings result: {json.dumps(result, indent=4)}")
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

    def list_vra_statuses(self) -> List[Dict]:
        """
        List all VRA statuses.

        Returns:
            List[Dict]: List of VRA statuses

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.list_vra_statuses(zvm_address={self.client.zvm_address})")
        url = f"https://{self.client.zvm_address}/v1/vras/statuses"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Successfully retrieved VRA statuses")
            logging.debug(f"VRA.list_vra_statuses result: {json.dumps(result, indent=4)}")
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

    def list_ip_configuration_types(self) -> List[Dict]:
        """
        List all IP configuration types.

        Returns:
            List[Dict]: List of IP configuration types

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.list_ip_configuration_types(zvm_address={self.client.zvm_address})")
        url = f"https://{self.client.zvm_address}/v1/vras/ipconfigurationtypes"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info("Successfully retrieved IP configuration types")
            logging.debug(f"VRA.list_ip_configuration_types result: {json.dumps(result, indent=4)}")
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

    def list_potential_recovery_vras(self, vra_identifier: str) -> List[Dict]:
        """
        List potential recovery VRAs for a specific VRA.

        Args:
            vra_identifier: The identifier of the VRA to get potential recovery VRAs for

        Returns:
            List[Dict]: List of potential recovery VRAs

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.list_potential_recovery_vras(zvm_address={self.client.zvm_address}, vra_identifier={vra_identifier})")
        url = f"https://{self.client.zvm_address}/v1/vras/{vra_identifier}/changerecoveryvra/potentials"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Successfully retrieved potential recovery VRAs for identifier: {vra_identifier}")
            logging.debug(f"VRA.list_potential_recovery_vras result: {json.dumps(result, indent=4)}")
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

    def execute_recovery_vra_change(self, vra_identifier: str, payload: Dict) -> Dict:
        """
        Execute a recovery VRA change for a specific VRA.

        Args:
            vra_identifier: The identifier of the VRA to change recovery VRA for
            payload: The change configuration

        Returns:
            Dict: The execution result

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"VRA.execute_recovery_vra_change(zvm_address={self.client.zvm_address}, vra_identifier={vra_identifier})")
        logging.debug(f"VRA.execute_recovery_vra_change payload: {json.dumps(payload, indent=4)}")
        url = f"https://{self.client.zvm_address}/v1/vras/{vra_identifier}/changerecoveryvra/execute"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.post(url, headers=headers, json=payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Successfully executed recovery VRA change for identifier: {vra_identifier}")
            logging.debug(f"VRA.execute_recovery_vra_change result: {json.dumps(result, indent=4)}")
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

    def validate_recovery_vra_change(self, vra_identifier, payload):
        logging.info(f"VRA.validate_recovery_vra_change: Validating recovery VRA change for identifier: {vra_identifier}...")
        url = f"https://{self.client.zvm_address}/v1/vras/{vra_identifier}/changerecoveryvra/validate"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.post(url, headers=headers, json=payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            logging.info(f"VRA.validate_recovery_vra_change: Successfully validated recovery VRA change for identifier: {vra_identifier}.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"VRA.validate_recovery_vra_change: Failed to validate recovery VRA change for identifier {vra_identifier}: {e}")
            raise

    def recommend_recovery_vra_change(self, vra_identifier, payload):
        logging.info(f"VRA.recommend_recovery_vra_change: Recommending recovery VRA change for identifier: {vra_identifier}...")
        url = f"https://{self.client.zvm_address}/v1/vras/{vra_identifier}/changerecoveryvra/recommendation"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.post(url, headers=headers, json=payload, verify=self.client.verify_certificate)
            response.raise_for_status()
            logging.info(f"VRA.recommend_recovery_vra_change: Successfully recommended recovery VRA change for identifier: {vra_identifier}.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"VRA.recommend_recovery_vra_change: Failed to recommend recovery VRA change for identifier {vra_identifier}: {e}")
            raise