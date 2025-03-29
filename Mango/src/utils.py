import logging
import os
import sys
from datetime import datetime

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def setup_logging(log_directory, log_level=logging.DEBUG):
    """configure logging, only log to file with timestamp"""
    try:
        os.makedirs(log_directory, exist_ok=True)
    except OSError as e:
        print(f"FATAL: failed to create log directory {log_directory}: {e}", file=sys.stderr)
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"run_{timestamp}.log" 
    log_file_path = os.path.join(log_directory, log_filename)

    logging.basicConfig(
        filename=log_file_path,
        filemode='a',
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        level=log_level
    )
    logging.info(f"logging start, log file: {log_file_path}")
    return log_file_path 
