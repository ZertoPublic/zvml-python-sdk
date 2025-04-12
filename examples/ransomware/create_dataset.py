#!/usr/bin/env python3

import os
import argparse
import logging
import shutil

def create_dataset(base_dir: str, number_of_files: int):
    """Create test files filled with specific content."""
    try:
        # Validate input
        if number_of_files <= 0:
            raise ValueError("Number of files must be positive")
            
        # Create directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)
        
        # Calculate required disk space (approximate)
        required_space = number_of_files * 1024 * 1024  # 1MB per file
        free_space = shutil.disk_usage(base_dir).free
        
        if free_space < required_space:
            raise ValueError(
                f"Not enough disk space. Need {required_space / (1024**3):.2f} GB, "
                f"but only {free_space / (1024**3):.2f} GB available"
            )
        
        # Calculate how many lines we need for ~1MB file
        # Each line is about 6 bytes (5 chars + newline)
        # 1MB = 1048576 bytes
        # Actual calculation: 1048576 / 6 = 174762.67
        lines_per_file = 174763
        
        # Create files
        for i in range(number_of_files):
            file_path = os.path.join(base_dir, f"file{i:04d}.txt")
            with open(file_path, 'w') as f:
                for _ in range(lines_per_file):
                    f.write(f'file{i:04d}\n')
            
            # Log every 100 files
            if (i + 1) % 100 == 0:
                logging.info(f"Created {i + 1} files...")
                
        logging.info(f"Created dataset in {base_dir}")
        logging.info(f"Total files created: {number_of_files}")
        
        # Log total size of the dataset
        total_size = sum(os.path.getsize(os.path.join(base_dir, f)) 
                        for f in os.listdir(base_dir))
        logging.info(f"Total dataset size: {total_size / (1024*1024):.2f} MB")
        logging.info(f"Average file size: {total_size / (number_of_files * 1024*1024):.2f} MB")
        
    except Exception as e:
        logging.error(f"Failed to create dataset: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Create test dataset")
    parser.add_argument("--base_dir", default="~/encryption_test", 
                       help="Base directory for test files (default: ~/encryption_test)")
    parser.add_argument("--number_of_files", type=int, required=True,
                       help="Number of files to create")
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Expand user path (~/...)
    base_dir = os.path.expanduser(args.base_dir)
    
    create_dataset(base_dir, args.number_of_files)

if __name__ == "__main__":
    main() 
