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

class Events:
    def __init__(self, client):
        self.client = client

    def list_events(self, event_identifier=None, start_date=None, end_date=None, vpg_identifier=None,
                    site_name=None, site_identifier=None, zorg_identifier=None, event_type=None,
                    entity_type=None, category=None, user_name=None, alert_identifier=None):
        """
        Fetches a list of events or a specific event from the Zerto API with optional filters.

        :param event_identifier: The identifier of the specific event (if fetching a specific event).
        :param start_date: The filter interval start date-time (string in date-time format).
        :param end_date: The filter interval end date-time (string in date-time format).
        :param vpg_identifier: The identifier of the VPG.
        :param site_name: The name of the site.
        :param site_identifier: The internal ZVM site identifier.
        :param zorg_identifier: The identifier of the ZORG.
        :param event_type: The event type.
        :param entity_type: The entity type to return.
        :param category: The event category to return.
        :param user_name: The username for which the event occurred.
        :param alert_identifier: The alert identifier.
        :return: List of events or a specific event based on provided filters.
        """
        logging.info(f'Events.list_events(event_identifier={event_identifier}, start_date={start_date}, end_date={end_date}, '
                    f'vpg_identifier={vpg_identifier}, site_name={site_name}, site_identifier={site_identifier}, '
                    f'zorg_identifier={zorg_identifier}, event_type={event_type}, entity_type={entity_type}, '
                    f'category={category}, user_name={user_name}, alert_identifier={alert_identifier})')
        
        # Determine endpoint based on whether event_identifier is provided
        if event_identifier:
            events_uri = f"https://{self.client.zvm_address}/v1/events/{event_identifier}"
        else:
            events_uri = f"https://{self.client.zvm_address}/v1/events"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }
        
        # Building query parameters
        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if vpg_identifier:
            params['vpgIdentifier'] = vpg_identifier
        if site_name:
            params['siteName'] = site_name
        if site_identifier:
            params['siteIdentifier'] = site_identifier
        if zorg_identifier:
            params['zorgIdentifier'] = zorg_identifier
        if event_type:
            params['eventType'] = event_type
        if entity_type:
            params['entityType'] = entity_type
        if category:
            params['category'] = category
        if user_name:
            params['userName'] = user_name
        if alert_identifier:
            params['alertIdentifier'] = alert_identifier

        try:
            logging.info("Fetching events with specified filters...")
            response = requests.get(events_uri, headers=headers, params=params, verify=self.client.verify_certificate)
            response.raise_for_status()
            events = response.json()

            if not events:
                logging.warning("No events found.")
                return []

            return events

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

    def list_event_types(self):
        """
        Fetches a list of event types from the Zerto API.

        :return: List of event types.
        """
        logging.info(f'Events.list_event_types(zvm_address={self.client.zvm_address})')
        event_types_uri = f"https://{self.client.zvm_address}/v1/events/types"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            logging.info("Fetching event types...")
            response = requests.get(event_types_uri, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            event_types = response.json()

            if not event_types:
                logging.warning("No event types found.")
                return []

            return event_types

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

    def list_event_entities(self):
        """
        Fetches a list of event entities from the Zerto API.

        :return: List of event entities.
        """
        logging.info(f'Events.list_event_entities(zvm_address={self.client.zvm_address})')
        event_entities_uri = f"https://{self.client.zvm_address}/v1/events/entities"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            logging.info("Fetching event entities...")
            response = requests.get(event_entities_uri, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            event_entities = response.json()

            if not event_entities:
                logging.warning("No event entities found.")
                return []

            return event_entities

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

    def list_event_categories(self):
        """
        Fetches a list of event categories from the Zerto API.

        :return: List of event categories.
        """
        logging.info(f'Events.list_event_categories(zvm_address={self.client.zvm_address})')
        event_categories_uri = f"https://{self.client.zvm_address}/v1/events/categories"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            response = requests.get(event_categories_uri, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            event_categories = response.json()

            if not event_categories:
                logging.warning("No event categories found.")
                return []

            return event_categories

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching event categories: {e}")
            return None

        url = f"https://{self.client.zvm_address}/v1/events/types"
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
