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
import json

class RecoveryReports:
    def __init__(self, client):
        self.client = client

    def get_recovery_reports(self, recovery_operation_identifier=None, page_number=1, page_size=1000, 
                         vpg_name=None, recovery_type=None, state=None, start_time=None, end_time=None):
        """
        Generate a recovery report and view information about recovery operations.

        Args:
            recovery_operation_identifier (str): The identifier of a specific recovery operation. If provided, no other parameters are used.
            start_time (str): The filtering interval start date-time.
            end_time (str): The filtering interval end date-time.
            page_number (int): The page number to retrieve. Default is 1.
            page_size (int): The number of reports to display in a single page. Max 1000. Default is 1000.
            vpg_name (str): The name of the VPG(s) to filter by. Separate multiple VPGs with commas.
            recovery_type (str): The type of recovery operation. Possible values: Failover, FailoverTest, Move.
            state (str): The recovery operation state. Possible values: Success, Fail.

        Returns:
            dict: The response from the ZVM API containing recovery report details.
        """

        logging.info(f'RecoveryReports.get_recovery_reports recovery_operation_identifier: {recovery_operation_identifier}, \
                     start_time: {start_time}, end_time: {end_time}, page_number: {page_number}, \
                     page_size: {page_size}, vpg_name: {vpg_name}, recovery_type: {recovery_type}, state: {state}')

        # Determine the URL based on whether recoveryOperationIdentifier is provided
        if recovery_operation_identifier:
            base_url = f"https://{self.client.zvm_address}/v1/reports/recovery/{recovery_operation_identifier}"
            params = None  # No query parameters for this endpoint
        else:
            base_url = f"https://{self.client.zvm_address}/v1/reports/recovery"
            # Parameters for the request
            params = {
                "startTime": start_time,
                "endTime": end_time,
                "pageNumber": page_number,
                "pageSize": page_size,
            }

            # Optional parameters
            if vpg_name:
                params["vpgName"] = vpg_name
            if recovery_type:
                params["recoveryType"] = recovery_type
            if state:
                params["state"] = state

        # Headers for the request
        headers = {
            "Authorization": f"Bearer {self.client.token}",
            "Accept": "application/json",
        }

        try:
            response = requests.get(base_url, headers=headers, params=params, verify=self.client.verify_certificate)

            if response.status_code == 200:
                # logging.info(f"Successfully retrieved recovery reports = {json.dumps(response.json(), indent=4)}")
                return response.json()
            else:
                logging.error(f"Failed to fetch recovery reports. Status Code: {response.status_code}, Response: {response.text}")
                response.raise_for_status()

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

    def list_resource_reports(self, start_time=None, end_time=None, page_number=None, page_size=None, 
                            zorg_name=None, vpg_name=None, vm_name=None, protected_site_name=None, 
                            protected_cluster_name=None, protected_host_name=None, protected_org_vdc=None, 
                            protected_vcd_org=None, recovery_site_name=None, recovery_cluster_name=None, 
                            recovery_host_name=None, recovery_org_vdc=None, recovery_vcd_org=None):
        """
        Fetch resource reports with optional filters.

        Args:
            start_time (str): The filtering interval start date-time.
            end_time (str): The filtering interval end date-time.
            page_number (int): The page number to retrieve.
            page_size (int): The number of reports per page (max 1000).
            zorg_name (str): The name of the ZORG in the Zerto Cloud Manager.
            vpg_name (str): The name of the VPG.
            vm_name (str): The name of the virtual machine.
            protected_site_name (str): The name of the protected site.
            protected_cluster_name (str): The name of the protected cluster.
            protected_host_name (str): The name of the protected host.
            protected_org_vdc (str): The name of the protected VDC organization.
            protected_vcd_org (str): The name of the protected VCD organization.
            recovery_site_name (str): The name of the recovery site.
            recovery_cluster_name (str): The name of the recovery cluster.
            recovery_host_name (str): The name of the recovery host.
            recovery_org_vdc (str): The name of the recovery VDC organization.
            recovery_vcd_org (str): The name of the recovery VCD organization.

        Returns:
            list: A list of resource reports based on the provided filters.
        """
        logging.info(f"list_resource_reports(start_time={start_time}, end_time={end_time}, page_number={page_number}, "
                    f"page_size={page_size}, zorg_name={zorg_name}, vpg_name={vpg_name}, vm_name={vm_name}, "
                    f"protected_site_name={protected_site_name}, protected_cluster_name={protected_cluster_name}, "
                    f"protected_host_name={protected_host_name}, protected_org_vdc={protected_org_vdc}, "
                    f"protected_vcd_org={protected_vcd_org}, recovery_site_name={recovery_site_name}, "
                    f"recovery_cluster_name={recovery_cluster_name}, recovery_host_name={recovery_host_name}, "
                    f"recovery_org_vdc={recovery_org_vdc}, recovery_vcd_org={recovery_vcd_org})")

        uri = f"https://{self.client.zvm_address}/v1/reports/resources"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        # Building query parameters
        params = {}
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        if page_number is not None:
            params['pageNumber'] = page_number
        if page_size is not None:
            params['pageSize'] = page_size
        if zorg_name:
            params['zorgName'] = zorg_name
        if vpg_name:
            params['vpgName'] = vpg_name
        if vm_name:
            params['vmName'] = vm_name
        if protected_site_name:
            params['protectedSiteName'] = protected_site_name
        if protected_cluster_name:
            params['protectedClusterName'] = protected_cluster_name
        if protected_host_name:
            params['protectedHostName'] = protected_host_name
        if protected_org_vdc:
            params['protectedOrgVdc'] = protected_org_vdc
        if protected_vcd_org:
            params['protectedVcdOrg'] = protected_vcd_org
        if recovery_site_name:
            params['recoverySiteName'] = recovery_site_name
        if recovery_cluster_name:
            params['recoveryClusterName'] = recovery_cluster_name
        if recovery_host_name:
            params['recoveryHostName'] = recovery_host_name
        if recovery_org_vdc:
            params['recoveryOrgVdc'] = recovery_org_vdc
        if recovery_vcd_org:
            params['recoveryVcdOrg'] = recovery_vcd_org

        try:
            response = requests.get(uri, headers=headers, params=params, verify=self.client.verify_certificate)
            response.raise_for_status()
            reports = response.json()

            if not reports:
                logging.warning("No resource reports found.")
                return []

            return reports

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

    def get_latest_failover_test_report(self, vpg_name):
        """
        Get the most recent failover test report for a specific VPG.

        Args:
            vpg_name (str): The name of the VPG to get the report for.

        Returns:
            dict: The most recent failover test report for the VPG, or None if no reports found.
        """
        logging.info(f"RecoveryReports.get_latest_failover_test_report VPG: {vpg_name}")
        
        try:
            # Get all failover test reports for this VPG
            reports = self.get_recovery_reports(
                vpg_name=vpg_name,
                recovery_type="FailoverTest",
                page_size=1000  # Adjust if you need more reports
            )
            
            if not reports:
                logging.warning(f"No failover test reports found for VPG: {vpg_name}")
                return None
            
            # Sort reports by StartTime in descending order and get the first one
            sorted_reports = sorted(
                reports,
                key=lambda x: x["General"].get("EndTime", ""),
                reverse=True
            )
            
            if sorted_reports:
                return sorted_reports[0]
            
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
