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

class LocalSite:
    def __init__(self, zvm_address, token):
        self.zvm_address = zvm_address
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_local_site(self):
        logging.info("LocalSite.get_local_site: Fetching local site information...")
        url = f"https://{self.zvm_address}/v1/localsite"
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            logging.info("LocalSite.get_local_site: Successfully retrieved local site information.")
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

    def get_pairing_statuses(self):
        logging.info("LocalSite.get_pairing_statuses: Fetching pairing statuses...")
        url = f"https://{self.zvm_address}/v1/localsite/pairingstatuses"
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            logging.info("LocalSite.get_pairing_statuses: Successfully retrieved pairing statuses.")
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

    def send_usage(self):
        logging.info("LocalSite.send_usage: Sending local site billing usage...")
        url = f"https://{self.zvm_address}/v1/localsite/billing/sendUsage"
        try:
            response = requests.post(url, headers=self.headers, verify=False)
            response.raise_for_status()
            if response.content.strip():
                logging.info("LocalSite.send_usage: Successfully sent billing usage data.")
                return response.json()
            else:
                logging.info("LocalSite.send_usage: Successfully sent billing usage data. No content returned.")
                return None
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

    def get_login_banner(self):
        logging.info("LocalSite.get_login_banner: Fetching login banner settings...")
        url = f"https://{self.zvm_address}/v1/localsite/settings/loginBanner"
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            logging.info("LocalSite.get_login_banner: Successfully retrieved login banner settings.")
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

    def set_login_banner(self, is_enabled, banner_text):
        logging.info("LocalSite.set_login_banner: Setting login banner settings...")
        url = f"https://{self.zvm_address}/v1/localsite/settings/loginBanner"
        payload = {
            "isLoginBannerEnabled": is_enabled,
            "loginBanner": banner_text
        }
        try:
            response = requests.put(url, headers=self.headers, json=payload, verify=False)
            response.raise_for_status()
            logging.info("LocalSite.set_login_banner: Successfully set login banner settings.")
            return response
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
