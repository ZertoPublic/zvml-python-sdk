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

class VirtualizationSites:
    def __init__(self, client):
        self.client = client

    def get_virtualization_sites(self, site_identifier=None):
        """
        Get virtualization sites information. (Auth)
        
        Args:
            site_identifier (str, optional): The identifier of the site to get details for.
                                          If not provided, returns all sites.
        
        Endpoints: 
            - /v1/virtualizationsites (when site_identifier is None)
            - /v1/virtualizationsites/{siteIdentifier} (when site_identifier is provided)
        
        Returns:
            dict or list: Site details if site_identifier is provided, otherwise array of all sites
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites"
        if site_identifier:
            url = f"{url}/{site_identifier}"
            logging.info(f"VirtualizationSites.get_virtualization_sites: Fetching site {site_identifier}...")
        else:
            logging.info("VirtualizationSites.get_virtualization_sites: Fetching all virtualization sites...")

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

    def get_virtualization_site_vms(self, site_identifier):
        """
        Get a list of unprotected VMs from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get VMs from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/vms
        
        Returns:
            list: Array of unprotected VMs in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/vms"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_vms: Fetching VMs for site {site_identifier}...")
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

    def get_virtualization_site_vcd_vapps(self, site_identifier):
        """
        Get a list of unprotected VCD vApps from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get VCD vApps from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/vcdvapps
        
        Returns:
            list: Array of unprotected VCD vApps in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/vcdvapps"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_vcd_vapps: Fetching VCD vApps for site {site_identifier}...")
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

    def get_virtualization_site_datastores(self, site_identifier):
        """
        Get a list of datastores from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get datastores from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/datastores
        
        Returns:
            list: Array of datastores in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/datastores"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_datastores: Fetching datastores for site {site_identifier}...")
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

    def get_virtualization_site_folders(self, site_identifier):
        """
        Get a list of folders from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get folders from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/folders
        
        Returns:
            list: Array of folders in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/folders"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_folders: Fetching folders for site {site_identifier}...")
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

    def get_virtualization_site_datastore_clusters(self, site_identifier):
        """
        Get a list of datastore clusters from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get datastore clusters from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/datastoreclusters
        
        Returns:
            list: Array of datastore clusters in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/datastoreclusters"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_datastore_clusters: Fetching datastore clusters for site {site_identifier}...")
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

    def get_virtualization_site_resource_pools(self, site_identifier):
        """
        Get a list of resource pools from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get resource pools from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/resourcepools
        
        Returns:
            list: Array of resource pools in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/resourcepools"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_resource_pools: Fetching resource pools for site {site_identifier}...")
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

    def get_virtualization_site_org_vdcs(self, site_identifier):
        """
        Get a list of organization VDCs (Virtual Data Centers) from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get org VDCs from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/orgvdcs
        
        Returns:
            list: Array of organization VDCs in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/orgvdcs"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_org_vdcs: Fetching org VDCs for site {site_identifier}...")
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

    def get_virtualization_site_networks(self, site_identifier):
        """
        Get a list of networks from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get networks from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/networks
        
        Returns:
            list: Array of networks in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/networks"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_networks: Fetching networks for site {site_identifier}...")
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

    def get_virtualization_site_hosts(self, site_identifier, host_identifier=None):
        """
        Get hosts information from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get hosts from.
            host_identifier (str, optional): The identifier of a specific host to get details for.
                                          If not provided, returns all hosts.
        
        Endpoints: 
            - /v1/virtualizationsites/{siteIdentifier}/hosts (when host_identifier is None)
            - /v1/virtualizationsites/{siteIdentifier}/hosts/{hostIdentifier} (when host_identifier is provided)
        
        Returns:
            list or dict: Array of hosts if host_identifier is None, otherwise details of specific host
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/hosts"
        if host_identifier:
            url = f"{url}/{host_identifier}"
            logging.info(f"VirtualizationSites.get_virtualization_site_hosts: Fetching host {host_identifier} from site {site_identifier}...")
        else:
            logging.info(f"VirtualizationSites.get_virtualization_site_hosts: Fetching all hosts for site {site_identifier}...")

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

    def get_virtualization_site_repositories(self, site_identifier):
        """
        Get a list of repositories from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get repositories from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/repositories
        
        Returns:
            list: Array of repositories in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/repositories"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_repositories: Fetching repositories for site {site_identifier}...")
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

    def get_virtualization_site_host_clusters(self, site_identifier):
        """
        Get a list of host clusters from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get host clusters from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/hostclusters
        
        Returns:
            list: Array of host clusters in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/hostclusters"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_host_clusters: Fetching host clusters for site {site_identifier}...")
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

    def get_virtualization_site_org_vdc_networks(self, site_identifier, org_vdc_identifier):
        """
        Get a list of networks from the specified organization VDC. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site.
            org_vdc_identifier (str): The identifier of the organization VDC to get networks from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/orgvdcs/{orgVdcIdentifier}/networks
        
        Returns:
            list: Array of networks in the specified organization VDC
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/orgvdcs/{org_vdc_identifier}/networks"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_org_vdc_networks: Fetching networks for org VDC {org_vdc_identifier} in site {site_identifier}...")
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

    def get_virtualization_site_org_vdc_storage_policies(self, site_identifier, org_vdc_identifier):
        """
        Get a list of storage policies from the specified organization VDC. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site.
            org_vdc_identifier (str): The identifier of the organization VDC to get storage policies from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/orgvdcs/{orgVdcIdentifier}/storagepolicies
        
        Returns:
            list: Array of storage policies in the specified organization VDC
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/orgvdcs/{org_vdc_identifier}/storagepolicies"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_org_vdc_storage_policies: Fetching storage policies for org VDC {org_vdc_identifier} in site {site_identifier}...")
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

    def get_virtualization_site_devices(self, site_identifier, host_identifier=None, device_name=None):
        """
        Get a list of devices from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get devices from.
            host_identifier (str, optional): Filter devices by host identifier.
            device_name (str, optional): Filter devices by device name.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/devices
        
        Query Parameters:
            - hostIdentifier (optional)
            - deviceName (optional)
        
        Returns:
            list: Array of devices in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/devices"
        
        # Add query parameters if provided
        params = {}
        if host_identifier:
            params['hostIdentifier'] = host_identifier
        if device_name:
            params['deviceName'] = device_name
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_devices: Fetching devices for site {site_identifier}...")
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

    def get_virtualization_site_public_cloud_networks(self, site_identifier):
        """
        Get a list of public cloud virtual networks from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get public cloud virtual networks from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/publiccloud/virtualNetworks
        
        Returns:
            list: Array of public cloud virtual networks in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/publiccloud/virtualNetworks"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_public_cloud_networks: Fetching public cloud virtual networks for site {site_identifier}...")
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

    def get_virtualization_site_public_cloud_subnets(self, site_identifier):
        """
        Get a list of public cloud subnets from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get public cloud subnets from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/publiccloud/subnets
        
        Returns:
            list: Array of public cloud subnets in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/publiccloud/subnets"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_public_cloud_subnets: Fetching public cloud subnets for site {site_identifier}...")
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

    def get_virtualization_site_public_cloud_security_groups(self, site_identifier):
        """
        Get a list of public cloud security groups from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get public cloud security groups from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/publiccloud/securityGroups
        
        Returns:
            list: Array of public cloud security groups in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/publiccloud/securityGroups"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_public_cloud_security_groups: Fetching public cloud security groups for site {site_identifier}...")
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

    def get_virtualization_site_public_cloud_vm_instance_types(self, site_identifier):
        """
        Get a list of public cloud VM instance types from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get VM instance types from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/publiccloud/vmInstanceTypes
        
        Returns:
            list: Array of public cloud VM instance types in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/publiccloud/vmInstanceTypes"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_public_cloud_vm_instance_types: Fetching VM instance types for site {site_identifier}...")
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

    def get_virtualization_site_public_cloud_resource_groups(self, site_identifier):
        """
        Get a list of public cloud resource groups from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get resource groups from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/publiccloud/resourceGroups
        
        Returns:
            list: Array of public cloud resource groups in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/publiccloud/resourceGroups"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_public_cloud_resource_groups: Fetching resource groups for site {site_identifier}...")
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

    def get_virtualization_site_public_cloud_keys_containers(self, site_identifier):
        """
        Get a list of public cloud keys containers from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get keys containers from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/publiccloud/keyscontainers
        
        Returns:
            list: Array of public cloud keys containers in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/publiccloud/keyscontainers"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_public_cloud_keys_containers: Fetching keys containers for site {site_identifier}...")
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

    def get_virtualization_site_public_cloud_encryption_keys(self, site_identifier, encryption_key_id=None):
        """
        Get public cloud encryption keys from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site.
            encryption_key_id (str, optional): The identifier of a specific encryption key to retrieve.
                                             If not provided, returns all encryption keys.
        
        Endpoints: 
            - /v1/virtualizationsites/{siteIdentifier}/publiccloud/encryptionkeys (when encryption_key_id is None)
            - /v1/virtualizationsites/{siteIdentifier}/publiccloud/encryptionkeys/{encryptionKeyId} (when encryption_key_id is provided)
        
        Returns:
            list or dict: Array of encryption keys if encryption_key_id is None, otherwise details of specific key
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/publiccloud/encryptionkeys"
        if encryption_key_id:
            url = f"{url}/{encryption_key_id}"
            logging.info(f"VirtualizationSites.get_virtualization_site_public_cloud_encryption_keys: Fetching encryption key {encryption_key_id} for site {site_identifier}...")
        else:
            logging.info(f"VirtualizationSites.get_virtualization_site_public_cloud_encryption_keys: Fetching all encryption keys for site {site_identifier}...")

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

    def get_virtualization_site_public_cloud_managed_identities(self, site_identifier):
        """
        Get a list of public cloud managed identities from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get managed identities from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/publiccloud/managedidentities
        
        Returns:
            list: Array of public cloud managed identities in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/publiccloud/managedidentities"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_public_cloud_managed_identities: Fetching managed identities for site {site_identifier}...")
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

    def get_virtualization_site_public_cloud_disk_encryption_keys(self, site_identifier):
        """
        Get a list of public cloud disk encryption keys from the specified site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the site to get disk encryption keys from.
        
        Endpoint: 
            /v1/virtualizationsites/{siteIdentifier}/publiccloud/diskencryptionkeys
        
        Returns:
            list: Array of public cloud disk encryption keys in the specified site
        
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"https://{self.client.zvm_address}/v1/virtualizationsites/{site_identifier}/publiccloud/diskencryptionkeys"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"VirtualizationSites.get_virtualization_site_public_cloud_disk_encryption_keys: Fetching disk encryption keys for site {site_identifier}...")
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