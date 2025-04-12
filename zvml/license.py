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

class License:
    def __init__(self, client):
        self.client = client
    
    def get_license(self):
        """
        Fetch license information from the Zerto server.

        Returns:
            dict: The license information from the Zerto server, or an empty dictionary if no content is returned.
        """
        logging.info(f'License.get_license(zvm_address={self.client.zvm_address})')

        url = f"https://{self.client.zvm_address}/v1/license"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            logging.info("Fetching license information...")
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)

            # Handle 204 No Content
            if response.status_code == 204:
                logging.info("No license information available.")
                return {}

            # Raise an error for other non-successful HTTP status codes
            response.raise_for_status()

            # Parse the response JSON
            license_info = response.json()
            logging.info("Successfully fetched license information.")
            return license_info

        except requests.exceptions.RequestException as e:
            if e.response is not None:
                logging.error(f"HTTPError: {e.response.status_code} - {e.response.reason}")
                try:
                    error_details = e.response.json()
                    logging.error(f"Error details: {json.dumps(error_details, indent=2)}")
                except ValueError:
                    logging.error(f"Response content: {e.response.text}")
            else:
                logging.error("HTTPError occurred with no response attached.")
            raise

        except Exception as e:
            logging.error(f"Unexpected error while fetching license information: {e}")
            raise

    def put_license(self, license_key):
        """
        Add a new license or update an existing one on the Zerto server.

        Args:
            license_key (str): The license key to add or update.

        Returns:
            dict: The response from the Zerto server, or an empty dictionary if no content is returned.
        """
        logging.info(f'License.put_license(zvm_address={self.client.zvm_address}, license_key={license_key})')

        url = f"https://{self.client.zvm_address}/v1/license"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        payload = {
            "licenseKey": license_key
        }

        try:
            logging.info("Adding or updating license...")
            response = requests.put(url, json=payload, headers=headers, verify=self.client.verify_certificate)

            # Handle empty response with 200 status code
            if response.status_code == 200 and not response.content:
                logging.info("License successfully added or updated with no content returned.")
                return {}

            # Raise an error for other non-successful HTTP status codes
            response.raise_for_status()

            # Parse the response JSON
            response_data = response.json()
            logging.info("Successfully added or updated license.")
            return response_data

        except requests.exceptions.RequestException as e:
            if e.response is not None:
                logging.error(f"HTTPError: {e.response.status_code} - {e.response.reason}")
                try:
                    error_details = e.response.json()
                    logging.error(f"Error details: {json.dumps(error_details, indent=2)}")
                except ValueError:
                    logging.error(f"Response content: {e.response.text}")
            else:
                logging.error("HTTPError occurred with no response attached.")
            raise

        except Exception as e:
            logging.error(f"Unexpected error while adding or updating license: {e}")
            raise

    def delete_license(self):
        """
        Delete the current license from the Zerto server.

        Returns:
            dict: The response from the Zerto server.
        """
        logging.info(f'License.delete_license(zvm_address={self.client.zvm_address})')

        url = f"https://{self.client.zvm_address}/v1/license"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            logging.info("Deleting license...")
            response = requests.delete(url, headers=headers, verify=self.client.verify_certificate)

            # Raise an error for non-successful HTTP status codes
            response.raise_for_status()

            # Parse the response JSON if available
            if response.content:
                response_data = response.json()
                logging.info("License successfully deleted.")
                return response_data
            else:
                logging.info("License successfully deleted with no content returned.")
                return {}

        except requests.exceptions.RequestException as e:
            logging.error(f"HTTPError: {e.response.status_code} - {e.response.reason}")
            try:
                error_details = e.response.json()
                logging.error(f"Error details: {json.dumps(error_details, indent=2)}")
            except ValueError:
                logging.error(f"Response content: {e.response.text}")
            raise

        except Exception as e:
            logging.error(f"Unexpected error while deleting license: {e}")
            raise
    