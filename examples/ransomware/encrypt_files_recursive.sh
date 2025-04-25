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

# Generate a unique initialization vector (IV) for each file
generate_iv() {
  openssl rand -hex 16
}

# Find all files in the directory and subdirectories
find "$folder" -type f | while read -r file; do
  # Skip if the file does not exist or is unreadable
  if [ ! -r "$file" ]; then
    echo "Skipping unreadable file: $file"
    continue
  fi

  # Extract filename and extension
  filename=$(basename "$file")
  dirpath=$(dirname "$file")
  base_name="${filename%.*}"
  ext="${filename##*.}"

  # Define the output file path by appending .encrypted to the original extension
  output_file="$dirpath/${base_name}.${ext}.${extension}"

  # Generate a unique IV
  iv=$(generate_iv)

  # Encrypt the file
  echo "Encrypting $file to $output_file with IV $iv"
  if openssl enc -aes-256-cbc -salt -in "$file" -out "$output_file" -k "$password" -iv "$iv" -pbkdf2; then
    # If encryption is successful, remove the original file
    rm "$file"
    echo "Encrypted and removed $file."
  else
    # If encryption fails, print an error message
    echo "Failed to encrypt $file."
  fi
done

