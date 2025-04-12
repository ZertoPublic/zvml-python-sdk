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

class Alerts:
    def __init__(self, client):
        self.client = client

    #      Manage ZVM Alerts
    def get_alerts(self, start_date=None, end_date=None, vpg_name=None, zorg_identifier=None,
                   site_identifier=None, level=None, entity=None, help_identifier=None, is_dismissed=None,
                   alert_identifier=None):
        """
        Fetches alerts from the Zerto API with optional filters or a specific alert if `alert_identifier` is provided.

        :param start_date: The filter interval start date-time (string in date-time format).
        :param end_date: The filter interval end date-time (string in date-time format).
        :param vpg_name: The name of the VPG to filter alerts for.
        :param zorg_identifier: The identifier of the ZORG.
        :param site_identifier: The internal ZVM site identifier.
        :param level: The alert level.
        :param entity: The alert entity type.
        :param help_identifier: The alert help identifier associated with the alert.
        :param is_dismissed: True if alert was dismissed.
        :param alert_identifier: The specific alert identifier to retrieve a single alert.
        :return: List of alerts or a specific alert based on the provided filters.
        """
        if alert_identifier:
            alerts_uri = f"https://{self.client.zvm_address}/v1/alerts/{alert_identifier}"
        else:
            alerts_uri = f"https://{self.client.zvm_address}/v1/alerts"

        logging.info(f'Alerts.get_alerts(alert_identifier={alert_identifier}, start_date={start_date}, end_date={end_date}, '
                      f'vpg_name={vpg_name}, zorg_identifier={zorg_identifier}, site_identifier={site_identifier}, '
                      f'level={level}, entity={entity}, help_identifier={help_identifier}, is_dismissed={is_dismissed})')
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        # Building query parameters for general alerts retrieval
        params = {}
        if not alert_identifier:
            if start_date:
                params['startDate'] = start_date
            if end_date:
                params['endDate'] = end_date
            if vpg_name:
                # Get VPG identifier from name
                vpg = self.client.vpgs.get_vpg_by_name(vpg_name)
                if vpg:
                    params['vpgIdentifier'] = vpg.get('VpgIdentifier')
                    logging.info(f"Found VPG identifier {params['vpgIdentifier']} for VPG name {vpg_name}")
                else:
                    logging.warning(f"VPG with name {vpg_name} not found")
                    return []
            if zorg_identifier:
                params['zorgIdentifier'] = zorg_identifier
            if site_identifier:
                params['siteIdentifier'] = site_identifier
            if level:
                params['level'] = level
            if entity:
                params['entity'] = entity
            if help_identifier:
                params['helpIdentifier'] = help_identifier
            if is_dismissed is not None:
                params['isDismissed'] = str(is_dismissed).lower()

        try:
            logging.info("Fetching alerts...")
            response = requests.get(alerts_uri, headers=headers, params=params, verify=self.client.verify_certificate)
            response.raise_for_status()
            alerts = response.json()

            if not alerts:
                logging.warning("No alerts found.")
                return []

            return alerts

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

    def dismiss_alert(self, alert_identifier):
        """
        Dismisses a specific alert by its identifier.

        :param alert_identifier: The identifier of the alert to be dismissed.
        :return: Success message if the alert was dismissed, else an error message.
        """
        logging.info(f'Alerts.dismiss_alert(alert_identifier={alert_identifier})')
        
        # Construct the URL for dismissing the alert
        dismiss_uri = f"https://{self.client.zvm_address}/v1/alerts/{alert_identifier}/dismiss"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            logging.info(f"Attempting to dismiss alert with ID: {alert_identifier}")
            response = requests.post(dismiss_uri, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()

            if response.status_code == 200:
                logging.info(f"Alert {alert_identifier} successfully dismissed.")
                return f"Alert {alert_identifier} dismissed successfully."
            else:
                logging.warning(f"Unexpected response code: {response.status_code}")
                return f"Alert {alert_identifier} dismissal returned an unexpected status."

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

    def undismiss_alert(self, alert_identifier):
        """
        Undismisses a specific alert by its identifier.

        :param alert_identifier: The identifier of the alert to be dismissed.
        :return: Success message if the alert was dismissed, else an error message.
        """
        logging.info(f'Alerts.undismiss_alert(alert_identifier={alert_identifier})')
        
        # Construct the URL for dismissing the alert
        undismiss_uri = f"https://{self.client.zvm_address}/v1/alerts/{alert_identifier}/undismiss"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            logging.info(f"Attempting to undismiss alert with ID: {alert_identifier}")
            response = requests.post(undismiss_uri, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()

            if response.status_code == 200:
                logging.info(f"Alert {alert_identifier} successfully undismissed.")
                return f"Alert {alert_identifier} undismissed successfully."
            else:
                logging.warning(f"Unexpected response code: {response.status_code}")
                return f"Alert {alert_identifier} undismissal returned an unexpected status."

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

    def get_alert_levels(self):
        """
        Fetches the available alert levels from the Zerto API.

        :return: List of alert levels or an error message if the request fails.
        """
        logging.info('Alerts.get_alert_levels()')
        
        # Construct the URL for fetching alert levels
        alert_levels_uri = f"https://{self.client.zvm_address}/v1/alerts/levels"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            logging.info("Fetching available alert levels...")
            response = requests.get(alert_levels_uri, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            alert_levels = response.json()

            if not alert_levels:
                logging.warning("No alert levels found.")
                return []

            return alert_levels

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

    def get_alert_entities(self):
        """
        Fetches the available alert entities from the Zerto API.

        :return: List of alert entities or an error message if the request fails.
        """
        logging.info('Alerts.get_alert_entities()')
        
        # Construct the URL for fetching alert entities
        alert_entities_uri = f"https://{self.client.zvm_address}/v1/alerts/entities"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            logging.info("Fetching available alert entities...")
            response = requests.get(alert_entities_uri, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            alert_entities = response.json()

            if not alert_entities:
                logging.warning("No alert entities found.")
                return []

            return alert_entities

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

    def get_alert_help_identifiers(self):
        """
        Fetches the available alert help identifiers from the Zerto API.

        :return: List of alert help identifiers or an error message if the request fails.
        """
        logging.info('Alerts.get_alert_help_identifiers()')
        
        # Construct the URL for fetching alert help identifiers
        help_identifiers_uri = f"https://{self.client.zvm_address}/v1/alerts/helpidentifiers"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            logging.info("Fetching available alert help identifiers...")
            response = requests.get(help_identifiers_uri, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            help_identifiers = response.json()

            if not help_identifiers:
                logging.warning("No alert help identifiers found.")
                return []

            return help_identifiers

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
