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
from typing import Dict, List, Optional, Any
from zvml.common import ZertoTweakType

class Tweaks:
    def __init__(self, client):
        self.client = client

    def list_tweaks(self, tweak_name: Optional[str] = None) -> List[Dict]:
        """List ZVM tweaks.
        
        Args:
            tweak_name: Optional name of specific tweak to retrieve
        
        Returns:
            List[Dict]: List of ZVM tweaks and their current settings, or a single tweak if name provided
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"Tweaks.list_tweaks(zvm_address={self.client.zvm_address}, tweak_name={tweak_name})")
        
        # Build URL based on whether a specific tweak is requested
        base_url = f"https://{self.client.zvm_address}/management/api/tweaks/v1.0/zvmTweaks"
        url = f"{base_url}/{tweak_name}" if tweak_name else base_url
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            result = response.json()
            
            # If a specific tweak was requested, wrap the result in a list for consistent return type
            if tweak_name:
                result = [result]
                
            logging.info(f"Successfully retrieved {len(result)} ZVM tweak(s)")
            logging.debug(f"Tweaks.list_tweaks result: {json.dumps(result, indent=4)}")
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

    def set_tweak(self, tweak_name: str, value: Any, tweak_type: ZertoTweakType = ZertoTweakType.ZVM, comment: str = "Changed from API") -> Dict:
        """Set a ZVM tweak value.
        
        Args:
            tweak_name: Name of the tweak to update
            value: New value for the tweak
            tweak_type: Type of tweak (ZVM, VRA, or Frontend)
            comment: Optional comment for the change
            
        Returns:
            Dict: Updated tweak information
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"Tweaks.set_tweak(zvm_address={self.client.zvm_address}, tweak_name={tweak_name}, value={value}, type={tweak_type.value})")
        
        url = f"https://{self.client.zvm_address}/management/api/tweaks/v1/zvmTweaks"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        payload = {
            "name": tweak_name,
            "type": tweak_type.value,
            "value": str(value),
            "comment": comment
        }
        
        logging.info(f"Tweaks.set_tweak payload: {payload}")
        logging.info(f"Tweaks.set_tweak url: {url}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, verify=self.client.verify_certificate)
            
            # Log the raw response for debugging
            logging.debug(f"Raw response status: {response.status_code}")
            logging.debug(f"Raw response headers: {dict(response.headers)}")
            logging.debug(f"Raw response content: {response.text}")
            
            response.raise_for_status()
            
            try:
                result = response.json()
                logging.info(f"Successfully updated tweak {tweak_name}")
                logging.debug(f"Tweaks.set_tweak result: {json.dumps(result, indent=4)}")
                return result
            except ValueError:
                # If response is not JSON but request was successful
                logging.info(f"Successfully updated tweak {tweak_name} (no JSON response)")
                return {"status": "success", "name": tweak_name}
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error setting tweak {tweak_name}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Status code: {e.response.status_code}")
                logging.error(f"Response text: {e.response.text}")
                try:
                    error_json = e.response.json()
                    logging.error(f"Error details: {json.dumps(error_json, indent=2)}")
                except ValueError:
                    logging.error("Could not parse error response as JSON")
            else:
                logging.error(f"Request failed: {str(e)}")
            raise

    def delete_tweak(self, tweak_name: str) -> None:
        """Delete a ZVM tweak.
        
        Args:
            tweak_name: Name of the tweak to delete
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        logging.info(f"Tweaks.delete_tweak(zvm_address={self.client.zvm_address}, tweak_name={tweak_name})")
        
        url = f"https://{self.client.zvm_address}/management/api/tweaks/v1/zvmTweaks/{tweak_name}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"Tweaks.delete_tweak url: {url}")
        
        try:
            response = requests.delete(url, headers=headers, verify=self.client.verify_certificate)
            
            # Log the raw response for debugging
            logging.debug(f"Raw response status: {response.status_code}")
            logging.debug(f"Raw response headers: {dict(response.headers)}")
            logging.debug(f"Raw response content: {response.text}")
            
            response.raise_for_status()
            logging.info(f"Successfully deleted tweak {tweak_name}")
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error deleting tweak {tweak_name}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Status code: {e.response.status_code}")
                logging.error(f"Response text: {e.response.text}")
                try:
                    error_json = e.response.json()
                    logging.error(f"Error details: {json.dumps(error_json, indent=2)}")
                except ValueError:
                    logging.error("Could not parse error response as JSON")
            else:
                logging.error(f"Request failed: {str(e)}")
            raise