import requests
from urllib.parse import urljoin, urlparse
import os
import logging
import time

def get_m3u8(m3u8_url, save_path):
    """download and save m3u8 file 

    Args:
        m3u8_url (str): m3u8 url extracted from network request
        save_path (str): m3u8 saving path
    Return:
        save_path (str): m3u8 saving path
    """
    headers = {
        "Referer": "https://www.mgtv.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", 
    }
    try:
        response = requests.get(m3u8_url, headers=headers, timeout=30)
        response.raise_for_status() 
        with open(save_path, 'wb') as f:
            f.write(response.content) 
        logging.info(f'M3U8 downloaded successfully ✅: {save_path}')
        return save_path
    except requests.exceptions.RequestException as e:
        logging.error(f'M3U8 download failed ❌: {m3u8_url} - {e}')
        return None
    except IOError as e:
        logging.error(f'Failed to save M3U8 file ❌: {save_path} - {e}')
        return None

def get_url(m3u8_url, m3u8_path):
    """extract initial urls and segment urls for video from m3u8 file

    Args:
        m3u8_url (str): m3u8 url extracted from network request
        m3u8_path (str): saving path of m3u8 filename, returned from `get_m3u8`

    Returns:
        init_urls, segs (tuple): initial url & segment urls list
    """
    parsed_m3u8_url = urlparse(m3u8_url)
    base_url = urljoin(m3u8_url, ".") 
    logging.debug(f"Base URL for segments determined as: {base_url}")

    init_url = None
    segs_uris = []

    try: 
        with open(m3u8_path, 'r', encoding='utf-8') as f: 
            lines = f.readlines() 

        for line in lines:
            line = line.strip() 

            if line.startswith('#EXT-X-MAP:URI=\"'):
                try:
                    init_uri = line.split('URI="')[1].rsplit('"', 1)[0]
                    init_url = urljoin(base_url, init_uri) 
                    logging.debug(f"Found EXT-X-MAP URI: {init_uri}, Full URL: {init_url}")
                except IndexError:
                    logging.warning(f"Could not parse EXT-X-MAP line: {line}")

            elif not line.startswith('#') and line:
                segs_uris.append(line) 

        logging.info(f"Found Initialization URL: {init_url is not None}")
        logging.info(f"Found {len(segs_uris)} segment URIs")

        full_seg_urls = [urljoin(base_url, uri) for uri in segs_uris]
        logging.debug(f"First few full segment URLs: {full_seg_urls[:5]}")

        return init_url, full_seg_urls 

    except FileNotFoundError:
        logging.error(f"M3U8 file not found at: {m3u8_path}")
        return None, []
    except Exception as e:
        logging.error(f"Error parsing M3U8 file: {e}")
        return None, []

def download_video(video_subfolder, video_name_base, request_url, suffix, segment_index=None):
    """download initial url and segment urls

    Args:
        video_subfolder (str): video subfolder
        video_name_base (str): video name
        request_url (str): initial url and segment urls
        suffix (str): should be ".mp4" for initial url or "m4s" for segments
        segment_index: index for segment, defaults to None
    """
    if not request_url: 
        logging.warning("Download skipped: No URL provided.")
        return False

    headers = {
        "Referer": "https://www.mgtv.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }
    try:
        response = requests.get(request_url, headers=headers, stream=True, timeout=60) 
        response.raise_for_status()

        os.makedirs(video_subfolder, exist_ok=True)

        if segment_index is not None:
            segment_filename = f"{video_name_base}_seg_{segment_index:04d}{suffix}"
        else: 
            segment_filename = f"{video_name_base}_init{suffix}"
        saving_path = os.path.join(video_subfolder, segment_filename)
        logging.debug(f"Attempting to save to: {saving_path}")

        with open(saving_path, 'wb') as f:
            downloaded_size = 0
            for chunk in response.iter_content(chunk_size=8192 * 10): 
                if chunk: 
                    f.write(chunk)
                    downloaded_size += len(chunk)
        logging.info(f'Download successful ✅: {saving_path} ({downloaded_size / 1024 / 1024:.2f} MB)')
        return True 

    except requests.exceptions.Timeout:
        logging.error(f'Download timed out ⏳: {request_url}')
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f'Download failed ❌: {request_url} - {e}')
        return False
    except IOError as e:
        logging.error(f'Failed to write file ❌: {saving_path} - {e}')
        return False
