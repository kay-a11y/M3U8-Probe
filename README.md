# 🎥 M3U8-Probe

A tiny yet powerful toolkit to **scan, download, and merge** `.ts` video segments from m3u8 file(without KEY) or direct segment links — without needing a full m3u8 file.

---

## ✨ Features

- Scan segment URLs even when `.m3u8` is missing
- Great for blind or brute-force-style segment discovery under censorship or poorly indexed sources
- Multi-threaded (async) downloading with retry logic
- Merge all chunks into one `.ts` file (ready for ffmpeg)
- Readable script-style — just edit and run

---

## 😺 Quick Start

1. **Clone the project:**

    ```bash
    git clone https://github.com/kay-a11y/M3U8-Probe.git
    ```

2. **Navigate to the project directory:**

    ```bash
    cd M3U8-Probe
    ```

3. **Install the requirements:**

    ```bash
    pip install -r requirements.txt
    ```

---

## 📁 Scripts Overview

| File | Purpose |
|------|--------|
| `m3u8_dl.py` | Async segment scanner + downloader + merger (m3u8 needed) |
| `link_dl.py` | Async downloader for numbered `.ts` segments (no m3u8 needed) |

---

## ⚙️ How to Use

> These are script-based tools. To use, **edit the parameters directly** in the script file, then run.

### 🪄 1. Edit Parameters

At the end of the script, modify things like:

```python
base_url = "https://example.com/video/seg-"
output_file = "episode01.ts"
headers = {
    "User-Agent": "...",
    "Referer": "...",
}
```

Optional:

* max\_tasks
* timeout
* file pattern (`seg-{i:03d}.ts` vs `001.png.ts`)

---

### ▶️ 2. Run It

```bash
python3 m3u8_dl.py
# or
python3 link_dl.py
```

```
segs length = 623
💘 Downloading: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 623/623 [00:36<00:00,  7.15seg/s]

```

```
🔍 Scanning segments: 148seg [01:39,  1.49seg/s]
💘 Downloading:  99%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████▍ | 146/148 [00:14<00:00, 16.33seg/s] 
2025-06-12 18:11:49,064 - WARNING - 💥 020.png.ts error:  (try 1/3)
💘 Downloading: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 148/148 [00:17<00:00,  8.41seg/s]
```

---

## 🐞 Troubleshooting

| Issue                                   | Fix                                                           |
| --------------------------------------- | ------------------------------------------------------------- |
| "Task was destroyed but it is pending!" | Make sure you're not interrupting before scanning is complete |
| Only downloads a few segments           | Try checking if the segment pattern is wrong or URL expired   |
| Output too small                        | Segment might have expired or blocked                         |

---

## 📖 Full Guide

I'm writing a detailed blog post including:

* How to find real segment URLs
* How to scan from DevTools
* How to adjust segment logic
* Convert `.ts` to `.mp4` with `ffmpeg`

> 🔗 [Read the full tutorial on my blog →](https://kay-a11y.github.io)  
(Will update soon...)

---

## 🚧 TODO

* [ ] Add CLI support with `argparse`
* [ ] Auto-detect segment range
* [ ] Convert to `.mp4` automatically
* [ ] More error-handling / verbose logs

---

## 🧑‍💻 Author

> 🐾 Blog: [kay-a11y.github.io](https://kay-a11y.github.io)

---

## 🖤 License

The project uses AGPLv3. For details, please refer to [LICENSE](LICENSE).