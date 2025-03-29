import os
import sys
import logging
import time
from urllib.parse import urlparse
import argparse 

from src.utils import setup_logging
from src.downloader import get_m3u8, get_url, download_video
from src.checker import find_missing_segments
from src.merger import merge_video

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = SCRIPT_DIR 
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LOG_DIR = os.path.join(DATA_DIR, "log")
VIDEO_DIR = os.path.join(DATA_DIR, "video")


def main():
    setup_logging(LOG_DIR, logging.INFO)

    parser = argparse.ArgumentParser(description="Download and merge M3U8 video streams.")
    parser.add_argument("m3u8_url", help="The URL of the master M3U8 file.")
    parser.add_argument("-o", "--output", default=None,
                        help="Base name for the downloaded files and final output (e.g., 'my_movie'). If not provided, attempts to guess from URL.")
    parser.add_argument("--skip-cleanup", action="store_true",
                        help="Do not delete source segment files after merging.")
    parser.add_argument("--skip-check", action="store_true",
                        help="Skip checking for missing segments before merging.")
    parser.add_argument("--debug", action="store_true",
                        help="Enable DEBUG level logging.")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("DEBUG logging enabled.")

    logging.info("--- Script Start ---")
    start_time = time.perf_counter()

    m3u8_url = args.m3u8_url
    video_name_base = args.output

    if not video_name_base:
        try:
            path_parts = urlparse(m3u8_url).path.split('/')
            potential_name = path_parts[-2] if len(path_parts) > 1 else "video"
            video_name_base = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in potential_name) 
            logging.info(f"Output name not provided, guessed '{video_name_base}' from URL.")
        except Exception as e:
            logging.warning(f"Could not guess video name from URL, using 'downloaded_video': {e}")
            video_name_base = "downloaded_video"

    m3u8_save_path = os.path.join(VIDEO_DIR, f"{video_name_base}_master.m3u8.txt") 
    video_subfolder = os.path.join(VIDEO_DIR, video_name_base) 

    logging.info(f"Attempting to download M3U8 from: {m3u8_url}")
    actual_m3u8_path = get_m3u8(m3u8_url, m3u8_save_path)

    if not actual_m3u8_path:
        logging.critical("Failed to download M3U8 index. Aborting.")
        sys.exit(1)

    logging.info(f"Parsing M3U8 file: {actual_m3u8_path}")
    init_url, seg_urls = get_url(m3u8_url, actual_m3u8_path) 

    if not seg_urls and not init_url:
         logging.critical("Failed to parse any media URLs from M3U8. Aborting.")
         sys.exit(1)

    
    logging.info("--- Starting Download Phase ---")
    os.makedirs(video_subfolder, exist_ok=True) 

    download_failures = 0
    
    if init_url:
        
        init_suffix = os.path.splitext(urlparse(init_url).path)[1] or '.mp4'
        logging.info(f"Downloading initialization segment ({init_suffix})...")
        if not download_video(video_subfolder, video_name_base, init_url, init_suffix, segment_index=None):
            download_failures += 1
            logging.warning("Failed to download initialization segment.") 
    else:
        logging.warning("No initialization URL found in M3U8.")

    
    if seg_urls:
        total_segments = len(seg_urls)
        logging.info(f"Downloading {total_segments} media segments...")
        for index, seg_url in enumerate(seg_urls):
            seg_suffix = os.path.splitext(urlparse(seg_url).path)[1] or '.m4s' 
            logging.debug(f"Downloading segment {index + 1}/{total_segments}...") 
            if not download_video(video_subfolder, video_name_base, seg_url, seg_suffix, segment_index=index + 1):
                download_failures += 1
            time.sleep(0.05) 

        logging.info(f"Segment download finished. Failures: {download_failures}/{total_segments}")
    else:
        logging.warning("No segment URLs found in M3U8.")

    if download_failures > total_segments * 0.5: 
        logging.error("High download failure rate. Merging might produce corrupted video.")


    if not args.skip_check:
        logging.info("--- Starting Check Phase ---")
        missing = find_missing_segments(video_subfolder, video_name_base)
        if missing:
            logging.warning(f"Missing segment numbers found: {', '.join(f'{num:04d}' for num in missing)}")
        else:
            logging.info("Segment check passed. No missing segments detected in sequence.")
    else:
        logging.info("Skipping check for missing segments.")


    logging.info("--- Starting Merge Phase ---")
    merge_video(video_subfolder, video_name_base, delete_source_files=not args.skip_cleanup)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    logging.info(f"--- Script End --- Total time: {elapsed_time:.2f} seconds ⏱️ ---")


if __name__ == "__main__":
    main()
