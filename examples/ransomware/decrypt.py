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

def decrypt_file(file_path: str, key: bytes) -> bool:
    """Decrypt a single file using AES."""
    try:
        # Read the encrypted file
        with open(file_path, 'rb') as file:
            # Read IV (first 16 bytes) and encrypted data
            iv = file.read(16)
            encrypted_data = file.read()
        
        # Create AES cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt the data
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_data = unpadder.update(padded_data) + unpadder.finalize()
        
        # Write the decrypted data to a new file (remove .encrypted suffix)
        decrypted_path = file_path.rsplit('.encrypted', 1)[0]
        with open(decrypted_path, 'wb') as file:
            file.write(decrypted_data)
        
        # Remove the encrypted file
        os.remove(file_path)
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to decrypt {file_path}: {str(e)}")
        return False

def decrypt_directory(base_dir: str, password: str):
    """Decrypt all encrypted files in the specified directory."""
    try:
        # Generate decryption key
        key = generate_key(password)
        
        # Get list of encrypted files
        files = []
        for root, _, filenames in os.walk(base_dir):
            for filename in filenames:
                if filename.endswith('.encrypted'):
                    files.append(os.path.join(root, filename))
        
        total_files = len(files)
        
        if total_files == 0:
            logging.info("No encrypted files found")
            return
        
        logging.info(f"Found {total_files} encrypted files")
        
        # Track progress
        successful = 0
        failed = 0
        
        # Process each file
        for i, file_path in enumerate(files, 1):
            logging.info(f"Decrypting {file_path}")
            
            if decrypt_file(file_path, key):
                successful += 1
            else:
                failed += 1
            
            # Log progress every 100 files or at the end
            if i % 100 == 0 or i == total_files:
                logging.info(f"Processed {i}/{total_files} files...")
        
        # Log final results
        logging.info("Decryption complete!")
        logging.info(f"Successfully decrypted: {successful} files")
        if failed > 0:
            logging.warning(f"Failed to decrypt: {failed} files")
            
    except Exception as e:
        logging.error(f"Decryption failed: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Decrypt files in directory")
    parser.add_argument("--base_dir", default="~/encryption_test", 
                       help="Base directory containing files to decrypt (default: ~/encryption_test)")
    parser.add_argument("--password", required=True,
                       help="Password for decryption (must match encryption password)")
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
    
    decrypt_directory(base_dir, args.password)

if __name__ == "__main__":
    main() 