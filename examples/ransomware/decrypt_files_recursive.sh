#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <directory> <encryption_key> <file_extension>"
  exit 1
fi

folder="$1"
password="$2"
extension="$3"

# Ensure the directory exists
if [ ! -d "$folder" ]; then
  echo "Directory $folder does not exist."
  exit 1
fi

# Find all files with the specified encrypted extension in the directory and subdirectories
find "$folder" -type f -name "*.$extension" | while read -r file; do
  # Skip if the file does not exist or is unreadable
  if [ ! -r "$file" ]; then
    echo "Skipping unreadable file: $file"
    continue
  fi

  # Extract the original filename by removing the .encrypted extension
  dirpath=$(dirname "$file")
  filename=$(basename "$file" ".$extension")
  original_file="$dirpath/$filename"

  # Decrypt the file
  echo "Decrypting $file to $original_file"
  if openssl enc -d -aes-256-cbc -in "$file" -out "$original_file" -k "$password" -pbkdf2; then
    # If decryption is successful, remove the encrypted file
    rm "$file"
    echo "Decrypted and removed $file."
  else
    # If decryption fails, print an error message
    echo "Failed to decrypt $file."
  fi
done

