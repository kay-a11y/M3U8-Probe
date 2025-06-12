import aiohttp
import asyncio
import os
from tqdm.asyncio import tqdm_asyncio
import logging

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

# Parse seg list
def get_segs(m3u8_file, prefix):
    with open(m3u8_file, 'r') as f:
        segs = [
            line.strip().split(prefix)[-1]
            for line in f
            if line.startswith(prefix)
        ]
    logging.debug(f"segs = {segs}")
    logging.info(f"segs length = {len(segs)}")
    return segs

# Async download with retry
async def download_seg(session, sem, seg, idx, output_dir, max_retries=3):
    url = base_url + seg
    path = os.path.join(output_dir, f"{idx:04d}_{seg}")

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

# Merge and delete all .ts chunks
def merge_ts_chunks(output_dir, output_path):
    with open(output_path, "wb") as final:
        for fname in sorted(os.listdir(output_dir)):
            path = os.path.join(output_dir, fname)
            with open(path, "rb") as part:
                final.write(part.read())
            os.remove(path)
    print(f"\n🎬 Final merged video saved to: {output_path}")

# Main async task
async def main():
    segs = get_segs(m3u8_file, prefix)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "data", output_file.split(".")[-2])
    output_path = os.path.join(script_dir, "data", output_file)
    os.makedirs(output_dir, exist_ok=True)

    sem = asyncio.Semaphore(10)
    async with aiohttp.ClientSession() as session:
        tasks = [
            download_seg(session, sem, seg, idx, output_dir)
            for idx, seg in enumerate(segs)
        ]

        for f in tqdm_asyncio.as_completed(tasks, total=len(tasks), desc="💘 Downloading", unit="seg"):
            await f
    merge_ts_chunks(output_dir, output_path)

if __name__ == "__main__":
    prefix = "/20240701/1rIWCjMw/2000kb/hls/"
    m3u8_file = "/home/phruit/repos/M3U8-Probe/data/S01E10_index.m3u8"
    base_url = "https://play.modujx12.com/20240701/1rIWCjMw/2000kb/hls/"
    output_file = "wrecked_s01e10.ts"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://xiaoyakankan.com",
        "Origin": "https://xiaoyakankan.com"
    }

    asyncio.run(main())
