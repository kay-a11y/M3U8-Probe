# 🎥 M3U8-Probe

A tiny yet handy toolkit to **scan, download, and merge** `.ts` video segments from m3u8 file(without KEY) or direct segment links - without needing a full m3u8 file.
It comes with two scripts:

* `m3u8_dl.py`: Extracts `.ts` segment links from an `.m3u8` playlist and downloads them all.
* `link_dl.py`: Probes numbered `.ts` files directly from a known base URL without using `.m3u8`.

You can use it to:

* Smartly extract `.ts` segment links (even if they end in `.jpg`!)
* Batch download segments with retries and merge them into a final `.ts` video
* Probe unknown URLs (like guessing 000.ts \~ 999.ts) with async download for speed

Perfect for automating content collection when a site is using `.m3u8`-based streaming.

## ✨ Features

* **Segment-Aware Parsing** - Automatically filters out ads or irrelevant `.ts` chunks based on path patterns
* **Smart Headers Support** - Customize `User-Agent`, `Referer`, and `Origin` to bypass anti-leech protections
* **Clean Merge** - Merge all chunks into one `.ts` file (ready for ffmpeg)
* **Resumable Design** - Safe to retry if the download breaks midway (within the same run)
* **Two Modes of Operation**

  * `m3u8_dl.py`: Parse and fetch segments from remote `.m3u8`
  * `link_dl.py`: Guess segments based on base URL + index (great when `.m3u8` is hidden)

### 📋 Sample Output

When you run `m3u8_dl.py` on a valid `.m3u8` URL:

```
2025-06-17 18:36:02,307 - INFO - base_url = https://play.modujx12.com/20240701/1rIWCjMw/2000kb/hls/
2025-06-17 18:36:08,707 - INFO - m3u8_file = /home/z3phyr/repos/GazeKit/hub-generalM3u8/data/wrecked_s01e01/playlist.m3u8
2025-06-17 18:36:08,710 - INFO - segs length = 623
💘 Downloading: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 623/623 [00:36<00:00,  7.15seg/s]
```

Or when using `link_dl.py` with index-based guessing:

```
🔍 Scanning segments: 148seg [01:39,  1.49seg/s]
💘 Downloading:  99%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████▍ | 146/148 [00:14<00:00, 16.33seg/s] 
2025-06-12 18:11:49,064 - WARNING - 💥 020.png.ts error:  (try 1/3)
💘 Downloading: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 148/148 [00:17<00:00,  8.41seg/s]
```

> All output gets saved under ./data/ by default.

## 🚀 Usage

Clone the repo and install dependencies:

```bash
git clone https://github.com/kay-a11y/M3U8-Probe.git
cd M3U8-Probe
pip install -r requirements.txt
```

### 🧩 Option 1: Download with `m3u8_dl.py`

Used when you have a **full `.m3u8` URL** (e.g. ends in `index.m3u8`).

```bash
python src/m3u8_dl.py
```

Before running, open `src/m3u8_dl.py` and manually edit:

* `remote_m3u8_url`: the full link to the playlist
* `output_file`: where to save the final merged video
* `headers`: custom `headers` to bypass referer/origin restrictions

### 🔍 Option 2: Download with `link_dl.py`

Used when `.m3u8` is not available, but you **know the base URL pattern** and want to guess numbered segments.

```bash
python src/link_dl.py
```

Before running, edit:

* `base_url`: e.g. `https://somehost.com/path/to/segments/`
* `seg_name`: segment range (e.g. 0 to 999)
* `output_file`: final merged video name
* `headers`: custom `headers` to bypass referer/origin restrictions

## 📖 Full Guide

I'm writing a detailed blog post including:

* How to find real segment URLs
* How to scan from DevTools
* How to adjust segment logic
* Convert `.ts` to `.mp4` with `ffmpeg`

> 🔗 <a href="https://kay-a11y.github.io/posts/m3u8-probe/" target="_blank">Read the full tutorial on my blog</a>.

## 🚧 TODO

* [ ] Add CLI support with `argparse`
* [x] Auto-parse m3u8 link and base url
* [ ] Auto-detect segment range
* [ ] Convert to `.mp4` automatically
* [ ] More error-handling / verbose logs

## 🧑‍💻 Author

> 🐾 Blog: [kay-a11y.github.io](https://kay-a11y.github.io)

## 📘 License

The project uses AGPLv3. For details, please refer to [LICENSE](LICENSE).