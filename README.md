# zerto-python-library
A Python library for interacting with the Zerto Virtual Manager (ZVM) API.

## Overview
This library provides a comprehensive Python interface to manage and automate Zerto Virtual Replication operations. It includes functionality for:

- Managing Virtual Protection Groups (VPGs)
- Handling VM protection and recovery
- Managing checkpoints and recovery points
- Monitoring alerts and events
- Managing licenses
- Configuring service profiles
- Handling encryption detection
- Managing datastores and VRAs
- Working with server date/time settings
- Managing ZORGs (Zerto Organizations)

## Installation

git clone https://github.com/your-repo/zerto-python-library.git
cd zerto-python-library
pip install -r requirements.txt

## Dependencies

- requests
- urllib3
- logging
- json
- typing

## Library Structure

The library is organized into several modules:

- `zvml/` - Core library components
  - `alerts.py` - Alert management and monitoring
  - `checkpoints.py` - Checkpoint operations and management
  - `common.py` - Common enums and utilities
  - `encryptiondetection.py` - Encryption detection functionality
  - `license.py` - License management
  - `localsite.py` - Local site operations
  - `recovery_reports.py` - Recovery reporting functionality
  - `server_date_time.py` - Server time operations
  - `service_profiles.py` - Service profile configuration
  - `tasks.py` - Task management and monitoring
  - `virtualization_sites.py` - Site management operations
  - `vpgs.py` - VPG operations and management
  - `vras.py` - VRA deployment and management
  - `zorgs.py` - ZORG operations

## Requirements

- Python 3.6+
- Zerto Virtual Replication environment
- Network access to ZVM server
- Keycloak authentication credentials

## Getting Started

1. Clone the repository
2. Install required dependencies
3. Configure your Zerto environment credentials
4. Run the example scripts to understand basic operations
5. Integrate the library into your automation workflows

## Authentication

The library uses Keycloak authentication. You'll need:
- ZVM server address
- Client ID
- Client Secret (* KeyCloak)
- Optional: SSL verification settings

## KeyCloak
In order to use api client you'll need:
1. Login into ZVML keycloak UI. https:////<ZVML IP>/auth
2. Select zerto realm (Switch from Master to Zerto using left menu drop box)
3. Click on "Clients" using the left menu
4. Click on CreateClient button
5. Fill in client id (will be used for authentication) and client name (logical), click next
6. Enable the following options: "Client authentication", "Authorization", "Standard flow", "Direct access grants", 
   "Implicit flow", "OAuth 2.0 Device Authorization Grant", click next, click save.
7. Select "Service account roles" tab, click on "Assign Role" button, check mark "admin" (or another role), click on "Assign" button
8. Select "Credentials" tab, copy "Client Secret"
9. Use the combination of the created client id and the client secret for authntication in your code

## Error Handling

The library includes comprehensive error handling and logging:
- Input validation
- Error status checking
- Detailed error messages
- Operation status logging

## Examples

Each example script demonstrates specific functionality:

### Alert Management
`alerts_example.py` - Simple alert monitoring and management (list, dismiss, undismiss):

```bash
python examples/alerts_example.py \
--zvm_address "192.168.111.20" \
--client_id "zerto-api" \
--client_secret "your-secret-here" \
--ignore_ssl
```

### VPG Management with VMs
`vpg_vms_example.py` - VPG creation and VM management between VPGs:

```bash
python examples/vpg_vms_example.py \
--zvm_address "192.168.111.20" \
--client_id "zerto-api" \
--client_secret "your-secret-here" \
--ignore_ssl \
--vm1 "vm-name-1" \
--vm2 "vm-name-2"
```

### VPG Failover Testing
`vpg_failover_example.py` - Complete VPG lifecycle including failover testing:

```bash
python examples/vpg_failover_example.py \
--zvm_address "192.168.111.20" \
--client_id "zerto-api" \
--client_secret "your-secret-here" \
--ignore_ssl
```

### VRA Management
`vras_example.py` - Interactive VRA deployment and management:

```bash
python examples/vras_example.py \
--zvm_address "192.168.111.20" \
--client_id "zerto-api" \
--client_secret "your-secret-here" \
--ignore_ssl
```

### ZORG Management
`zorgs_example.py` - ZORG information retrieval and management:

```bash
python examples/zorgs_example.py \
--zvm_address "192.168.111.20" \
--client_id "zerto-api" \
--client_secret "your-secret-here" \
--ignore_ssl
```

### License Management
`license_example.py` - License information and management:

```bash
python examples/license_example.py \
--zvm_address "192.168.111.20" \
--client_id "zerto-api" \
--client_secret "your-secret-here" \
--ignore_ssl
```

### Events Monitoring
`events_example.py` - Monitor and retrieve Zerto events:

```bash
python examples/events_example.py \
--zvm_address "192.168.111.20" \
--client_id "zerto-api" \
--client_secret "your-secret-here" \
--ignore_ssl
```

### Encryption Detection (not operationa yet)
`encryption_detection_example.py` - Manage encryption detection settings:

```bash
python examples/encryption_detection_example.py \
--zvm_address "192.168.111.20" \
--client_id "zerto-api" \
--client_secret "your-secret-here" \
--ignore_ssl
```

### Service Profiles
`service_profiles_example.py` - Manage service profiles:

```bash
python examples/service_profiles_example.py \
--zvm_address "192.168.111.20" \
--client_id "zerto-api" \
--client_secret "your-secret-here" \
--ignore_ssl
```

### Volumes Management
`volumes_example.py` - Manage protected volumes:

```bash
python examples/volumes_example.py \
--zvm_address "192.168.111.20" \
--client_id "zerto-api" \
--client_secret "your-secret-here" \
--ignore_ssl
```

### Server Date and Time example
`server_date_time_example.py` - Manage protected volumes:

```bash
python examples/server_date_time_example.py \
--zvm_address "192.168.111.20" \
--client_id "zerto-api" \
--client_secret "your-secret-here" \
--ignore_ssl
```

### Datastore management example
`datastore_example.py` - Manage protected volumes:

```bash
python examples/datastore_example.py \
--zvm_address "192.168.111.20" \
--client_id "zerto-api" \
--client_secret "your-secret-here" \
--ignore_ssl
```

### Localsite management
`localsite_example.py` - Manage protected volumes:

```bash
python examples/localsite_example.py \
--zvm_address "192.168.111.20" \
--client_id "zerto-api" \
--client_secret "your-secret-here" \
--ignore_ssl
```

```bash
python examples/peersites_example.py \
    --site1_zvm_address <zvm1_address> \
    --site1_client_id <client_id1> \
    --site1_client_secret <secret1> \
    --site2_zvm_address <zvm2_address> \
    --site2_client_id <client_id2> \
    --site2_client_secret <secret2> \
    --ignore_ssl
```

```bash
python examples/tweaks_example.py \
    --zvm_address <zvm_address> \
    --client_id <client_id> \
    --client_secret <client_secret> \
    --ignore_ssl
```

Each example includes detailed comments explaining the functionality and demonstrates proper error handling and best practices for using the ZVML SDK.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project includes a legal disclaimer. See the header of each file for details.

For detailed API documentation and examples, please refer to the individual module files and example scripts.

  