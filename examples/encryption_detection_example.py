#!/usr/bin/env python3

# Legal Disclaimer
# This script is an example script and is not supported under any Zerto support program or service. 
# The author and Zerto further disclaim all implied warranties including, without limitation, 
# any implied warranties of merchantability or of fitness for a particular purpose.

# Configure logging BEFORE any imports
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

import argparse
import sys
import os
import time
import paramiko
import urllib3
from zvml.client import Client
from zvml.encryptiondetection import EncryptionDetection

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def setup_client(args):
    """Initialize and return Zerto client"""
    client = Client(
        zvm_address=args.zvm_address,
        client_id=args.client_id,
        client_secret=args.client_secret,
        verify_certificate=not args.ignore_ssl
    )
    return client

def setup_encrypted_volume(ssh_host: str, ssh_user: str, ssh_password: str):
    """Create and encrypt a volume on the Linux VM."""
    try:
        # Connect to the Linux VM
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_host, username=ssh_user, password=ssh_password)
        logging.info(f"Successfully connected to {ssh_host}")

        # Create a test file system
        commands = [
            "sudo dd if=/dev/zero of=/root/container.img bs=1M count=100",  # Create 100MB file
            "sudo losetup /dev/loop0 /root/container.img",  # Set up loop device
            "sudo cryptsetup -y luksFormat /dev/loop0",  # Encrypt with LUKS
            "echo 'YES' | sudo cryptsetup luksOpen /dev/loop0 encrypted_volume",  # Open encrypted volume
            "sudo mkfs.ext4 /dev/mapper/encrypted_volume",  # Create filesystem
            "sudo mkdir -p /mnt/encrypted",  # Create mount point
            "sudo mount /dev/mapper/encrypted_volume /mnt/encrypted",  # Mount encrypted volume
            "sudo dd if=/dev/urandom of=/mnt/encrypted/testfile bs=1M count=50"  # Create test file with random data
        ]

        for cmd in commands:
            logging.info(f"Executing: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                error = stderr.read().decode()
                logging.error(f"Command failed with status {exit_status}: {error}")
                raise Exception(f"Command failed: {cmd}")
            
        logging.info("Successfully created and encrypted test volume")

    except Exception as e:
        logging.error(f"Failed to setup encrypted volume: {str(e)}")
        raise
    finally:
        ssh.close()

def main():
    parser = argparse.ArgumentParser(description="Encryption Detection Example")
    parser.add_argument("--zvm_address", required=True, help="ZVM address")
    parser.add_argument('--client_id', required=True, help='Keycloak client ID')
    parser.add_argument('--client_secret', required=True, help='Keycloak client secret')
    parser.add_argument("--ignore_ssl", action="store_true", help="Ignore SSL certificate verification")
    parser.add_argument("--vm_address", required=True, help="Linux VM address")
    parser.add_argument("--vm_user", required=True, help="Linux VM username")
    parser.add_argument("--vm_password", required=True, help="Linux VM password")
    args = parser.parse_args()

    try:
        # Setup client
        client = setup_client(args)
        encryption_detection = EncryptionDetection(client)
        logging.info("Successfully connected to ZVM")

        # Setup encrypted volume on Linux VM
        setup_encrypted_volume(args.vm_address, args.vm_user, args.vm_password)
        
        # Wait for encryption detection to process
        logging.info("Waiting for encryption detection to process (30 seconds)...")
        time.sleep(30)

        # Check for suspected encrypted volumes
        detections = encryption_detection.list_suspected_volumes()
        
        if detections:
            logging.info("Suspected encrypted volumes detected:")
            for detection in detections:
                logging.info(f"Volume: {detection.get('VolumeName', 'Unknown')}")
                logging.info(f"Detection Type: {detection.get('DetectionType', 'Unknown')}")
                logging.info(f"Confidence Level: {detection.get('ConfidenceLevel', 'Unknown')}")
                logging.info("---")
        else:
            logging.info("No suspected encrypted volumes detected")

    except Exception as e:
        logging.exception("Error occurred:")
        sys.exit(1)

if __name__ == "__main__":
    main() 