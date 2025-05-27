#!/bin/bash

# Usage: ./generate_random_files.sh <file_size> <number_of_copies> <target_directory>

set -e

# Validate arguments
if [ $# -ne 3 ]; then
  echo "Usage: $0 <file_size> <number_of_copies> <target_directory>"
  echo "Example: $0 1G 5 /tmp/output"
  exit 1
fi

FILE_SIZE=$1
COPY_COUNT=$2
TARGET_DIR=$3
SOURCE_FILE="${TARGET_DIR}/random_file_${FILE_SIZE}.txt"

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Create base file with random characters
echo "Creating random file of size $FILE_SIZE at $SOURCE_FILE..."
< /dev/urandom tr -dc 'A-Za-z0-9!@#$%^&*()_+=-[]{}|:;<>,.?/~' | head -c "$FILE_SIZE" > "$SOURCE_FILE"

# Copy file specified number of times
echo "Copying file $COPY_COUNT times to $TARGET_DIR..."

for i in $(seq 1 "$COPY_COUNT"); do
  cp "$SOURCE_FILE" "${TARGET_DIR}/copy_${i}.txt"
  echo "Created copy_${i}.txt"
done

echo "✅ Done: $COPY_COUNT files of size $FILE_SIZE each in $TARGET_DIR."
