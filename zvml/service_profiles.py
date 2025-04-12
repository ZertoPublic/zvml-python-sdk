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

class ServiceProfiles:
    def __init__(self, client):
        self.client = client

    def get_service_profiles(self, site_identifier=None):
        """
        Get the list of all service profiles for the site.

        Args:
            site_identifier (str, optional): The identifier of the site for which service profiles 
                                           should be returned.

        Returns:
            list: List of service profiles with their details including:
                - serviceProfileName: Name of the service profile
                - rpo: Recovery Point Objective
                - history: Journal history length
                - maxJournalSizeInPercent: Maximum journal size as percentage
                - testInterval: Test interval period
                - description: Service profile description
        """
        logging.info(f"ServiceProfiles.get_service_profiles: Fetching service profiles...")
        
        url = f"https://{self.client.zvm_address}/v1/serviceprofiles"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        params = {}
        if site_identifier:
            params['siteIdentifier'] = site_identifier
            logging.info(f"Filtering service profiles for site: {site_identifier}")

        try:
            response = requests.get(url, headers=headers, params=params, verify=self.client.verify_certificate)
            response.raise_for_status()
            profiles = response.json()
            logging.info(f"Successfully retrieved {len(profiles)} service profiles")
            return profiles

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get service profiles: {e}")
            if hasattr(e.response, 'text'):
                logging.error(f"Error response: {e.response.text}")
            raise 