import os
import re
import logging

def find_missing_segments(directory_path, video_name_base):
    """
    Scans a directory for files matching 'my_movie_seg_XXXX.m4s',
    extracts the sequence numbers (XXXX), and finds any missing numbers
    within the detected range.

    Args:
        directory_path (str): The path to the directory to scan.
        video_name_base (str): video base name

    Returns:
        list: A sorted list of missing sequence numbers (as integers).
              Returns an empty list if no matching files are found or
              if no numbers are missing.
    """
    if not os.path.isdir(directory_path):
        logging.error(f"Error: Directory not found: {directory_path}")
        return []

    filename_pattern = re.compile(rf"^{re.escape(video_name_base)}_seg_(\d{{4}})\.m4s$")
    logging.debug(f"Checker using pattern: {filename_pattern.pattern}")

    segment_numbers = []
    try:
        for filename in os.listdir(directory_path):
            match = filename_pattern.match(filename)
            if match:
                segment_numbers.append(int(match.group(1)))
    except Exception as e:
        logging.error(f"Error reading directory {directory_path}: {e}")
        return []

    if not segment_numbers:
        logging.warning(f"No files matching the pattern 'my_movie_seg_XXXX.m4s' found in {directory_path}.")
        return []

    segment_numbers.sort()
    min_num = segment_numbers[0]
    max_num = segment_numbers[-1]

    expected_numbers = set(range(min_num, max_num + 1))
    actual_numbers = set(segment_numbers)
    missing_numbers = sorted(list(expected_numbers - actual_numbers))

    return missing_numbers

