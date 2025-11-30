import os
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()  # loads .env → os.environ

BASE_URL = "https://archive.org/download/jesus-og-josefine/Jesus%20Og%20Josefine%202003/S01/E{ep:02d}.mkv"
START_EPISODE = 2
END_EPISODE = 24
OUT_DIR = "episodes"
TRANSLATOR_DIR = "/Users/simonpacis/Downloads/srt-llm-translator"

os.makedirs(OUT_DIR, exist_ok=True)

def download_file(url, dest_path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

for ep in range(START_EPISODE, END_EPISODE + 1):
    ep_name = f"E{ep:02d}"
    mkv_name = f"{ep_name}.mkv"
    mkv_path = os.path.join(OUT_DIR, mkv_name)

    print(f"\n=== Episode {ep_name} ===")

# 1) Download MKV
    url = BASE_URL.format(ep=ep)
    if not os.path.exists(mkv_path):
        print("Downloading:", url)
        download_file(url, mkv_path)
    else:
        print("MKV exists, skipping download")

# 2) Extract VobSub
    sub_path = os.path.join(OUT_DIR, f"{ep_name}.sub")
    idx_path = os.path.join(OUT_DIR, f"{ep_name}.idx")
    if not (os.path.exists(sub_path) and os.path.exists(idx_path)):
        print("Extracting VobSub...")
        subprocess.run(
            ["mkvextract", "tracks", mkv_path, f"2:{sub_path}"],
            check=True
        )
    else:
        print("SUB/IDX exist, skipping extraction")

# 3) Convert vobsub → srt
    srt_path = os.path.join(OUT_DIR, f"{ep_name}.srt")
    if not os.path.exists(srt_path):
        print("Running vobsub2srt...")
        subprocess.run(
            ["vobsub2srt", os.path.join(OUT_DIR, ep_name)],
            check=True
        )
    else:
        print("SRT exists, skipping vobsub2srt")


    # 4) Translate SRT using env from .env
    movie_srt_path = os.path.abspath(os.path.join(OUT_DIR, f"{ep_name}.srt"))


    subprocess.run(
        [
            "python",
            "srt_llm_translator.py",
            "--source-lang", "da",
            "--target-lang", "en",
            "--file", movie_srt_path
        ],
        cwd=TRANSLATOR_DIR,
        env=os.environ,   # passes the dotenv-loaded vars
        check=True
    )

    print(f"Done with {ep_name}")

