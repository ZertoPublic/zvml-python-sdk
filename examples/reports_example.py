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

"""
Zerto Reports Example

Note: The reports functionality is demonstrated in vpg_failover_example.py, which includes:

1. Recovery Reports:
   - Getting recovery reports for VPGs
   - Filtering reports by date range
   - Getting specific recovery operation details
   - Getting latest failover test reports

2. Resource Reports:
   - Getting resource reports with various filters
   - Filtering by site, cluster, and organization
   - Getting detailed resource information

Please refer to vpg_failover_example.py for practical examples of using the reports functionality.

You can run vpg_failover_example.py with:
    python vpg_failover_example.py \
        --zvm_address <zvm_ip> \
        --client_id <client_id> \
        --client_secret <client_secret> \
        --ignore_ssl

For more information about the reports API, see the RecoveryReports class in zvml/recovery_reports.py
"""

if __name__ == "__main__":
    print(__doc__) 