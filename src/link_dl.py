import aiohttp
import asyncio
import os
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
import logging

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

# === Async downloader ===
async def download_seg(session, sem, seg_name, output_path, max_retries=3):
    url = base_url + seg_name
    path = os.path.join(output_path, seg_name)

    if os.path.exists(path):
        return

    for attempt in range(1, max_retries + 1):
        async with sem:
            try:
                async with session.get(url, headers=headers, timeout=15) as resp:
                    if resp.status in [200, 206]:
                        content = await resp.read()
                        if len(content) < 300:
                            logging.warning(f"⚠️ {seg_name} too small (try {attempt}/3)")
                        else:
                            with open(path, "wb") as f:
                                f.write(content)
                            return
                    else:
                        logging.warning(f"❌ {seg_name} HTTP {resp.status} (try {attempt}/3)")
            except Exception as e:
                logging.warning(f"💥 {seg_name} error: {e} (try {attempt}/3)")

        await asyncio.sleep(attempt)

    logging.critical(f"❗ Failed after 3 attempts: {seg_name}")

# === Merge all segments ===
def merge_ts_chunks(folder, output_path):
    with open(output_path, "wb") as out:
        for fname in sorted(os.listdir(folder)):
            if fname.endswith(".ts"):
                with open(os.path.join(folder, fname), "rb") as f:
                    out.write(f.read())
                os.remove(os.path.join(folder, fname))
    print(f"\n🎬 Final merged video saved to: {output_path}")

# === Main event loop ===
async def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "data", output_file.split(".")[-2])
    output_path = os.path.join(script_dir, "data", output_file)
    os.makedirs(output_dir, exist_ok=True)

    sem = asyncio.Semaphore(10)
    tasks = []

    async with aiohttp.ClientSession() as session:
        i = 1
        tasks = []
        pbar = tqdm(desc="🔍 Scanning segments", unit="seg")

        while True:
            seg_name = f"{i:03d}.png.ts"
            path = os.path.join(output_dir, seg_name)
            test_url = base_url + seg_name

            # Test first to stop early if 404
            try:
                async with session.get(test_url, headers=headers, timeout=10) as resp:
                    if resp.status != 200 or resp.content_length == 0:
                        break
            except:
                break

            tasks.append(download_seg(session, sem, seg_name, output_dir))
            i += 1
            pbar.update(1)

        pbar.close()

        for f in tqdm_asyncio.as_completed(tasks, total=len(tasks), desc="💘 Downloading", unit="seg"):
            await f

    merge_ts_chunks(output_dir, output_path)

if __name__ == "__main__":
    base_url = "https://play.gotomymv.life/ts/40c26f81749767102/L3R5MzAvbWVpanUv5bCR5bm06LCi5bCU6aG_UzA1RTA4/20763/"
    output_file = "Sheldon_s05e08.ts"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://www.bttwo.me",
        "Origin": "https://www.bttwo.me"
    }

    asyncio.run(main())