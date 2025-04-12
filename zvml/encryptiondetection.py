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
from typing import List, Dict

class EncryptionDetection:
    def __init__(self, client):
        self.client = client

    def get_encryption_detections(self):
        url = f"https://{self.client.zvm_address}/v1/encryptiondetection"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        logging.info(f"EncryptionDetection.get_encryption_detections(zvm_address={self.client.zvm_address})")
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
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

    def get_encryption_detection(self, detection_identifier):
        url = f"https://{self.client.zvm_address}/v1/encryptiondetection/{detection_identifier}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        logging.info(f"EncryptionDetection.get_encryption_detection(zvm_address={self.client.zvm_address}, detection_identifier={detection_identifier})")
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
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

    def get_encryption_detection_types(self):
        url = f"https://{self.client.zvm_address}/v1/encryptiondetection/types"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        logging.info(f"EncryptionDetection.get_encryption_detection_types(zvm_address={self.client.zvm_address})")
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
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

    def list_suspected_volumes(self) -> List[Dict]:
        """List all suspected encrypted volumes.
        
        Returns:
            List[Dict]: List of suspected encrypted volumes with their details
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"EncryptionDetection.list_suspected_volumes(zvm_address={self.client.zvm_address})")
        url = f"https://{self.client.zvm_address}/v1/encryptiondetection/suspected/volumes"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            logging.info(f"Successfully retrieved {len(result)} suspected encrypted volumes")
            logging.debug(f"EncryptionDetection.list_suspected_volumes result: {json.dumps(result, indent=4)}")
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