import aiohttp
import asyncio
import os
import requests
from tqdm.asyncio import tqdm_asyncio
from urllib.parse import urljoin
import logging

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

def prepare_output_paths(output_file, subfolder="data"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, subfolder, output_file.split(".")[-2])
    output_path = os.path.join(script_dir, subfolder, output_file)

    os.makedirs(output_dir, exist_ok=True)
    return output_dir, output_path

def get_base_url(remote_m3u8_url):
    from urllib.parse import urlparse
    parsed = urlparse(remote_m3u8_url)
    base_url = remote_m3u8_url.rsplit("/", 1)[0] + "/"
    logging.info(f"base_url = {base_url}")
    return base_url

def get_m3u8(remote_m3u8_url, output_dir):
    m3u8_file = os.path.join(output_dir, "playlist.m3u8")

    try:
        response = requests.get(remote_m3u8_url, timeout=10)
        response.raise_for_status() 

        with open(m3u8_file, "w", encoding="utf-8") as f:
            f.write(response.text)

        logging.info(f"m3u8_file = {m3u8_file}")
        return m3u8_file

    except Exception as e:
        logging.error(f"💥 Failed to download M3U8: {e}")
        return None
    
def get_segs(m3u8_file, base_url):
    segs = []

    if not m3u8_file:
        logging.error("📭 M3U8 file NOT found, please check if the m3u8 link is valid.")
        return []

    legit_prefix = "/" + "/".join(base_url.split("/")[3:])  # e.g. /20240701/xxx/yyy/hls

    with open(m3u8_file, 'r', encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue 

            if line.startswith(legit_prefix):
                segs.append(line)

            elif "/" not in line and line.endswith(".ts"):
            # elif ".ts" in line:
                segs.append(line)

            elif line.startswith("http") and line.endswith(".ts"):
                segs.append(line)

    logging.debug(f"segs = {segs}")
    logging.info(f"segs length = {len(segs)}")
    return segs

async def download_seg(session, sem, base_url, seg, idx, output_dir, max_retries=3):
    url = urljoin(base_url, seg)
    path = os.path.join(output_dir, f"{idx:04d}")

    if os.path.exists(path): 
        logging.debug(f"🔁 Skipped {seg} (already exists)")
        return

    for attempt in range(1, max_retries + 1):
        async with sem:
            try:
                async with session.get(url, headers=headers, timeout=15) as resp:
                    if resp.status in [200, 206]:
                        content = await resp.read()
                        if len(content) < 300:
                            logging.error(f"❌ {seg} too small (try {attempt}/3)")
                            continue
                        else:
                            with open(path, "wb") as f:
                                f.write(content)
                            logging.debug(f"✅ {seg}")
                            return
                    else:
                        logging.error(f"⛔️ {seg} HTTP {resp.status} (try {attempt}/3)")
            except Exception as e:
                logging.error(f"💥 {seg} error: {e} (try {attempt}/3)")

        await asyncio.sleep(1 + attempt) 

    logging.critical(f"❗ Failed after 3 attempts: {seg}")

def merge_ts_chunks(output_dir, output_path):
    with open(output_path, "wb") as final:
        for fname in sorted(os.listdir(output_dir)):
            if not fname.endswith(".m3u8"):
                path = os.path.join(output_dir, fname)
                with open(path, "rb") as part:
                    final.write(part.read())
                os.remove(path)
    print(f"\n🎬 Final merged video saved to: {output_path}")

async def main():
    output_dir, output_path = prepare_output_paths(output_file)
    base_url = get_base_url(remote_m3u8_url)
    m3u8_file = get_m3u8(remote_m3u8_url, output_dir)
    segs = get_segs(m3u8_file, base_url)

    sem = asyncio.Semaphore(10)
    async with aiohttp.ClientSession() as session:
        tasks = [
            download_seg(session, sem, base_url, seg, idx, output_dir)
            for idx, seg in enumerate(segs)
        ]

        for f in tqdm_asyncio.as_completed(tasks, total=len(tasks), desc="💘 Downloading", unit="seg"):
            await f
    merge_ts_chunks(output_dir, output_path)

if __name__ == "__main__":
    # Configuration section
    
    remote_m3u8_url = "https://play.modujx12.com/20240701/1rIWCjMw/2000kb/hls/index.m3u8"
    output_file = "wrecked_s01e01.ts"

    # Headers used for HTTP requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://xiaoyakankan.com",
        "Origin": "https://xiaoyakankan.com"
    }

    asyncio.run(main())
