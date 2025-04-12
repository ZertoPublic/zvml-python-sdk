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

class Datastores:
    def __init__(self, client):
        self.client = client

    def list_datastores(self, datastore_identifier=None):
        if datastore_identifier:
            logging.info(f"Datastores.list_datastores: Fetching datastore information for identifier: {datastore_identifier}...")
            url = f"https://{self.client.zvm_address}/v1/datastores/{datastore_identifier}"
        else:
            logging.info("Datastores.list_datastores: Fetching all datastores information...")
            url = f"https://{self.client.zvm_address}/v1/datastores"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            if datastore_identifier:
                logging.info(f"Datastores.list_datastores: Successfully retrieved datastore information for identifier: {datastore_identifier}.")
            else:
                logging.info("Datastores.list_datastores: Successfully retrieved all datastores information.")
            return response.json()
        except requests.exceptions.RequestException as e:
            if datastore_identifier:
                logging.error(f"Datastores.list_datastores: Failed to get datastore information for identifier {datastore_identifier}: {e}")
            else:
                logging.error(f"Datastores.list_datastores: Failed to get all datastores information: {e}")
            raise