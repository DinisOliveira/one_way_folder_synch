# Folder Synchronization Script

This script synchronizes the contents of a source directory with a replica directory. It ensures that all files and subdirectories in the source are replicated in the destination, and any extraneous files in the destination are removed.

## Features

- Synchronizes files from source to replica.
- Removes files from replica that do not exist in the source.
- Supports nested subdirectories.
- Logs all operations to a specified log file.

## Requirements

- Python 3.x


### Command-Line Arguments

- `--source_path`: Path to the source directory.
- `--replica_path`: Path to the replica directory.
- `--log_file_path`: Path to the log file.
- `--synch_interval`: Time interval for synchronization in seconds.

## Usage
python main.py [--source_path SOURCE] [--replica_path REPLICA] [--log_file_path LOG_FILE_PATH] [--synch_interval SYNCH_INTERVAL]
