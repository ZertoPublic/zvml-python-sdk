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
from .common import ZertoTaskStates

class Tasks:
    def __init__(self, client):
        self.client = client

    def wait_for_task_completion(self, task_identifier, timeout=600, interval=5, expected_task_state: ZertoTaskStates = ZertoTaskStates.Completed):
        logging.debug(f'wait_for_task_completion(zvm_address={self.client.zvm_address}, task_identifier={task_identifier}, timeout={timeout}, interval={interval})')
        start_time = time.time()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.client.token}'
        }

        while True:
            # Check if we've exceeded the timeout
            if time.time() - start_time > timeout:
                logging.error(f'Task ID={task_identifier} timed out after {timeout} seconds')
                raise TimeoutError(f"Task did not complete within {timeout} seconds")

            url = f"https://{self.client.zvm_address}/v1/tasks/{task_identifier}"
            try:
                response = requests.get(url, headers=headers, verify=self.client.verify_certificate)
                response.raise_for_status()
                task_info = response.json()

                state = task_info.get("Status", {}).get("State", -1)
                progress = task_info.get("Status", {}).get("Progress", 0)
                logging.debug(f'Task response: status={ZertoTaskStates.get_name_by_value(state)}, progress={progress}')

                if state == expected_task_state.value and progress == 100:
                    logging.info("Task completed successfully.")
                    time.sleep(interval)
                    return task_info
                elif state == ZertoTaskStates.InProgress.value:
                    time.sleep(interval)
                    continue
                else:
                    logging.error(f'Task ID={task_identifier} failed. task state={ZertoTaskStates.get_name_by_value(state)}')
                    raise Exception(f"Task failed: {task_info.get('CompleteReason', 'No reason provided')}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}")
                raise