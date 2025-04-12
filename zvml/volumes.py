import requests
import logging
import json

class Volumes:
    def __init__(self, client):
        self.client = client

    def list_volumes(self, volume_type=None, vpg_identifier=None, datastore_identifier=None, 
                    protected_vm_identifier=None, owning_vm_identifier=None):
        """
        Get a list of volumes info in the current site. For ZSSP users, the information 
        retrieved is for Protected entities only. (Auth)
        
        Args:
            volume_type (str, optional): The volume type
            vpg_identifier (str, optional): The identifier of the VPG
            datastore_identifier (str, optional): The identifier of the datastore
            protected_vm_identifier (str, optional): The identifier of the protected virtual machine
            owning_vm_identifier (str, optional): The identifier of the owning virtual machine
        
        Returns:
            list: Array of volume information objects
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/volumes"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        params = {
            'volumeType': volume_type,
            'vpgIdentifier': vpg_identifier,
            'datastoreIdentifier': datastore_identifier,
            'protectedVmIdentifier': protected_vm_identifier,
            'owningVmIdentifier': owning_vm_identifier
        }
        # Remove None values from params
        params = {k: v for k, v in params.items() if v is not None}
        
        logging.info("Volumes.list_volumes: Fetching volumes information")
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