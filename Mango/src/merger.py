import os
import time 
import shutil 
import logging

def get_sorted_segment_files(target_folder, video_name_base):
    """Finds and sorts segment files (.m4s) in the target folder.

    Args:
        target_folder (str): The folder containing the segment files.
        video_name_base (str): The base name used for segment files (e.g., 'my_movie').

    Returns:
        list: A sorted list of segment filenames, or None if error/not found.
    """
    logging.info(f"Searching for segments in: {target_folder}")
    segment_files = []
    try:
        all_files = os.listdir(target_folder)
        prefix = f"{video_name_base}_seg_"
        suffix = ".m4s"
        for filename in all_files:
            if filename.startswith(prefix) and filename.endswith(suffix):
                segment_files.append(filename)

        if not segment_files:
            logging.warning("No segment files (.m4s) found.")
            return None

        
        segment_files.sort()
        logging.debug(f"Found and sorted {len(segment_files)} segment files.")
        return segment_files

    except FileNotFoundError:
        logging.error(f"Target folder not found: {target_folder}")
        return None
    except Exception as e:
        logging.error(f"Error finding segment files: {e}")
        return None

def merge_video(target_folder, video_name_base, delete_source_files=True):
    """
    Merges video segments using Python's file I/O for binary concatenation.
    This avoids command line length limits.

    Args:
        target_folder (str): Folder containing init file and segments.
        video_name_base (str): Base name for input/output files.
        delete_source_files (bool): Whether to delete source files after merging. Defaults to True.
    """
    logging.info("Starting merge process using Python binary concatenation...")

    
    segment_files = get_sorted_segment_files(target_folder, video_name_base)
    if not segment_files:
        logging.error("Cannot proceed with merging: No segment files found or error occurred.")
        return

    
    init_file = f"{video_name_base}_init.mp4"
    
    output_file = f"{video_name_base}_merged_py.mp4"

    full_init_path = os.path.join(target_folder, init_file)
    full_output_path = os.path.join(target_folder, output_file)

    
    if not os.path.exists(full_init_path):
        logging.critical(f"Merge failed: Initialization file '{init_file}' not found in {target_folder}.")
        return

    
    logging.debug(f"Output file will be: {full_output_path}")
    try:
        with open(full_output_path, 'wb') as outfile: 
            
            logging.debug(f"Appending: {init_file}")
            with open(full_init_path, 'rb') as infile: 
                
                shutil.copyfileobj(infile, outfile)

            
            total_segments = len(segment_files)
            for i, seg_file in enumerate(segment_files, 1):
                full_seg_path = os.path.join(target_folder, seg_file)
                
                if i % 50 == 0 or i == 1 or i == total_segments: 
                    logging.info(f"Appending segment {i}/{total_segments}: {seg_file}")
                else:
                    logging.debug(f"Appending segment {i}/{total_segments}: {seg_file}")

                if not os.path.exists(full_seg_path):
                    logging.warning(f"Segment file not found, skipping: {seg_file}")
                    continue 

                with open(full_seg_path, 'rb') as infile:
                    shutil.copyfileobj(infile, outfile)

        logging.info(f"Binary concatenation successful: {output_file}")


        
        if delete_source_files:
            logging.info("Cleaning up source files...")
            time.sleep(1) 

            try:
                
                deleted_count = 0
                for seg_file in segment_files:
                    try:
                        os.remove(os.path.join(target_folder, seg_file))
                        deleted_count += 1
                    except OSError as e:
                        logging.warning(f"Could not delete segment {seg_file}: {e}")
                logging.debug(f"Deleted {deleted_count} segment files.")

                
                try:
                    os.remove(full_init_path)
                    logging.debug(f"Deleted init file: {init_file}")
                except OSError as e:
                    logging.warning(f"Could not delete init file {init_file}: {e}")

                logging.info("Cleanup complete.")
            except Exception as e:
                logging.error(f"Error during cleanup: {e}")

    except IOError as e:
        logging.critical(f"Merge failed due to file I/O error: {e}")
        
        if os.path.exists(full_output_path):
            try:
                os.remove(full_output_path)
                logging.warning(f"Deleted incomplete output file: {output_file}")
            except OSError as remove_error:
                logging.error(f"Could not delete incomplete output file {output_file}: {remove_error}")
    except Exception as e:
        logging.critical(f"An unexpected error occurred during Python binary merging: {e}")
        if os.path.exists(full_output_path):
            try:
                os.remove(full_output_path)
                logging.warning(f"Deleted potentially corrupt output file: {output_file}")
            except OSError as remove_error:
                 logging.error(f"Could not delete potentially corrupt output file {output_file}: {remove_error}")