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

class Zorgs:
    def __init__(self, client):
        self.client = client

    def get_zorgs(self, zorg_identifier=None):
        """
        Get ZORG information. If zorg_identifier is provided, returns details for that specific ZORG.
        
        Args:
            zorg_identifier (str, optional): The identifier of a specific ZORG
            
        Returns:
            dict/list: ZORG information. Returns a list of all ZORGs if no identifier is provided,
                      or details of a specific ZORG if identifier is provided.
        """
        url = f"https://{self.client.zvm_address}/v1/zorgs"
        if zorg_identifier:
            url = f"{url}/{zorg_identifier}"
            logging.info(f"Zorgs.get_zorgs: Fetching ZORG {zorg_identifier}...")
        else:
            logging.info("Zorgs.get_zorgs: Fetching all ZORGs...")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
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
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise 