"""
Script to download a large English wordlist for `data/words.txt`.

This script attempts to download the popular words list from the dwyl repo:
https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt

Run locally to populate `data/words.txt`:

    python scripts/fetch_wordlist.py

If you prefer a different source, edit the URL below.
"""

import os
import sys
import urllib.request

URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "data")
OUT_FILE = os.path.join(OUT_DIR, "words.txt")

os.makedirs(OUT_DIR, exist_ok=True)

print("Downloading wordlist from", URL)
try:
    with urllib.request.urlopen(URL) as resp:
        data = resp.read().decode("utf-8")
    with open(OUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(data)
    print(f"Wrote {len(data.splitlines())} words to {OUT_FILE}")
except Exception as e:
    print("Failed to download wordlist:", e)
    sys.exit(1)
