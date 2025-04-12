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
from enum import Enum

class DateTimeFormat(Enum):
    """Enum for date time format options"""
    DEFAULT = ""  # Returns full server time info
    LOCAL = "serverDateTimeLocal"  # Returns local time
    UTC = "serverDateTimeUtc"  # Returns UTC time
    ARGUMENT = "dateTimeArgument"  # Returns date time argument format

class ServerDateTime:
    def __init__(self, client):
        self.client = client

    def get_server_date_time(self, format=DateTimeFormat.DEFAULT):
        """
        Get the server date and time in the specified format.

        Args:
            format (DateTimeFormat): The format to return the date-time in.
                - DEFAULT: Returns full server time info (timezone, UTC time, local time, offset)
                - LOCAL: Returns local time
                - UTC: Returns UTC time
                - ARGUMENT: Returns date time argument format

        Returns:
            dict/str: Server date-time information. Format depends on the format parameter:
                - DEFAULT: {
                    'TimeZone': str,
                    'ServerTimeUtc': str,
                    'LocalTime': str,
                    'TimeOffset': str
                  }
                - LOCAL: Local time string
                - UTC: UTC time string
                - ARGUMENT: Date time argument format string
        """
        logging.info(f"ServerDateTime.get_server_date_time: Fetching server date and time in {format.name} format...")
        
        # Build the URL based on the format
        base_url = f"https://{self.client.zvm_address}/v1/serverDateTime"
        url = base_url if format == DateTimeFormat.DEFAULT else f"{base_url}/{format.value}"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        try:
            response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
            response.raise_for_status()
            server_time = response.json()
            logging.info(f"Successfully retrieved server date and time in {format.name} format")
            return server_time

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get server date and time: {e}")
            if hasattr(e.response, 'text'):
                logging.error(f"Error response: {e.response.text}")
            raise 