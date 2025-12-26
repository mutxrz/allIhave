import sys
import os
import re
import requests
import threading
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if len(sys.argv) < 2:
    print("Cara pakai:")
    print('  python3 fast_deviantart_image_downloader.py "keyword"')
    sys.exit(1)

keyword = sys.argv[1]
LIMIT = int(input("Input limit gambarnya dong puh:"))            # jumlah gambar ##edit ntar --Zakraa
THREADS = 5           # paralel download
TIMEOUT = 5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
}

SAVE_DIR = keyword
os.makedirs(SAVE_DIR, exist_ok=True)

# STEP 1 — Cari artwork (safe search)
def search_deviantart(keyword):
    url = "https://www.deviantart.com/search"
    params = {
        "q": keyword,
        "order": "popular",
        "content_type": "visual",
    }

    r = requests.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=TIMEOUT,
        verify=False,   # anti SSL error
    )
    r.raise_for_status()

    links = re.findall(r'href="(https://www.deviantart.com/[^"]+/art/[^"]+)"', r.text)
    seen = []
    for l in links:
        if l not in seen:
            seen.append(l)
    return seen[:LIMIT]

# STEP 2 — Ambil direct image
def extract_image_url(art_url):
    r = requests.get(
        art_url,
        headers=HEADERS,
        timeout=TIMEOUT,
        verify=False,
    )
    r.raise_for_status()

    # meta property paling stabil
    match = re.search(r'<meta property="og:image" content="([^"]+)"', r.text)
    return match.group(1) if match else None

# STEP 3 — Download gambar
def download_image(url, idx):
    try:
        ext = url.split("?")[0].split(".")[-1]
        path = os.path.join(SAVE_DIR, f"img_{idx}.{ext}")
        with requests.get(url, headers=HEADERS, stream=True, timeout=TIMEOUT, verify=False) as r:
            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)
        print(f"[✓] Downloaded: {path}")
    except Exception as e:
        print(f"[✗] Gagal download {url}")

print(f"🔍 Mencari DeviantArt: {keyword}")
arts = search_deviantart(keyword)

if not arts:
    print("❌ Tidak ditemukan artwork")
    sys.exit(1)

print(f"⚡ Ditemukan {len(arts)} artwork, mulai download...\n")

threads = []
idx = 1

for art in arts:
    img = extract_image_url(art)
    if img:
        t = threading.Thread(target=download_image, args=(img, idx))
        t.start()
        threads.append(t)
        idx += 1

for t in threads:
    t.join()

print("\n✅ Selesai! Semua gambar tersimpan di folder:", SAVE_DIR)
