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
from .tasks import Tasks

class PeerSites:
    def __init__(self, client):
        self.client = client
        self.tasks = Tasks(client)

    def get_peer_sites(self, site_identifier=None):
        """
        Get details of peer sites. (Auth)
        
        Args:
            site_identifier (str, optional): The identifier of a specific peer site to retrieve.
                                            If not provided, returns all peer sites.
        
        Returns:
            dict/list: If site_identifier is provided, returns details of the specific peer site.
                      Otherwise, returns a list of all peer sites.
        """
        if site_identifier:
            url = f"https://{self.client.zvm_address}/v1/peersites/{site_identifier}"
            logging.info(f"PeerSites.get_peer_sites: Fetching peer site with identifier: {site_identifier}...")
        else:
            url = f"https://{self.client.zvm_address}/v1/peersites"
            logging.info("PeerSites.get_peer_sites: Fetching all peer sites...")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            if site_identifier:
                logging.info(f"PeerSites.get_peer_sites: Successfully retrieved peer site information for site identifier: {site_identifier}.")
            else:
                logging.info("PeerSites.get_peer_sites: Successfully retrieved all peer sites.")
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

    def pair_site(self, hostname, token, port=9071, sync=True):
        """
        Pairs this site with another site. (Auth)
        
        Args:
            hostname (str): The IP or DNS name for the peer site
            token (str): The pairing token generated from the peer site
            port (int, optional): The port used to access the peer site. Defaults to 9071.
            sync (bool, optional): Wait for the pairing task to complete. Defaults to True.
                
        Returns:
            dict: Pairing result if sync=False, or final task status if sync=True
        """
        url = f"https://{self.client.zvm_address}/v1/peersites"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        pairing_data = {
            "hostName": hostname,
            "port": port,
            "token": token
        }
        
        logging.info(f"PeerSites.pair_site: Pairing with site {hostname} at port {port}...")
        try:
            response = requests.post(url, headers=headers, json=pairing_data, verify=self.client.verify_certificate)
            response.raise_for_status()
            
            if not sync:
                return response.json() if response.content else None

            # Get the task identifier from the response
            task_id = response.json()
            logging.info(f"PeerSites.pair_site pairing submitted, task_id={task_id}")

            if sync:
                # Wait for task completion
                self.tasks.wait_for_task_completion(task_id, timeout=30, interval=5)
                return task_id
            return task_id
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error pairing site: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Response content: {e.response.text}")
            raise

    def delete_peer_site(self, site_identifier, sync=True):
        """
        Unpairs this site with another site. (Auth)
        
        Args:
            site_identifier (str): The identifier of the peer site to delete
            sync (bool, optional): Wait for the pairing task to complete. Defaults to True.
        """
        url = f"https://{self.client.zvm_address}/v1/peersites/{site_identifier}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info(f"PeerSites.delete_peer_site: Deleting peer site {site_identifier}...")
        try:
            response = requests.delete(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()

            if not sync:
                return response.json() if response.content else None

            # Get the task identifier from the response
            task_id = response.json()
            logging.info(f"PeerSites.delete_peer_site unpairing submitted, task_id={task_id}")

            if sync:
                # Wait for task completion
                self.tasks.wait_for_task_completion(task_id, timeout=30, interval=5)
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

    def get_pairing_statuses(self):
        """
        Get the list of possible statuses for peer sites pairing. (Auth)
        
        Returns:
            list: List of possible pairing statuses
        """
        url = f"https://{self.client.zvm_address}/v1/peersites/pairingstatuses"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info("PeerSites.get_pairing_statuses: Fetching pairing statuses...")
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

    def generate_token(self):
        """
        Generate a token to pair with this site. (Auth)
        
        Returns:
            str: Generated pairing token
        """
        url = f"https://{self.client.zvm_address}/v1/peersites/generatetoken"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        logging.info("PeerSites.generate_token: Generating pairing token...")
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

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    def get_peer_site_types(self):
        logging.info("PeerSites.get_peer_site_types: Fetching peer site information for site types...")
        url = f"https://{self.client.zvm_address}/v1/peersites/types"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            logging.info("PeerSites.get_peer_site_types: Successfully retrieved peer site types information.")
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
