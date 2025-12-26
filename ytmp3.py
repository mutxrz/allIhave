import yt_dlp
import sys

if len(sys.argv) < 2:
    print("Cara pakai:")
    print("  python3 fastest_ydlp_keyword_mp3_extreme.py \"keyword lagu\"")
    sys.exit()

keyword = sys.argv[1]
search_query = f"ytsearch1:{keyword}"

ydl_opts = {
    # === MODE ANTI-LELET PALING EKSTRIM ===
    "forceip": "0.0.0.0",
    "socket_timeout": 3,
    "retries": 0,
    "fragment_retries": 0,
    "concurrent_fragment_downloads": 10,
    "fragment_size": 20 * 1024 * 1024,  # 20MB per fragment
    "nocheckcertificate": True,         # bypass SSL throttle
    "cachedir": False,                  # skip cache
    "http_headers": {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123 Safari/537.36"
        )
    },

    # === DOWNLOAD FORMAT PALING CEPAT ===
    "format": "bestaudio[ext=webm]/bestaudio/best",

    # === CEPATKAN FFmpeg ===
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
    "postprocessor_args": [
        "-threads", "4",  # percepat konversi
        "-ar", "44100"
    ],

    # === FILE OUTPUT ===
    "outtmpl": "%(title)s.%(ext)s",
}

print(f"🚀 Ultra Boost Download untuk: {keyword}")
print("⚡ Mode EKSTRIM anti-lemot diaktifkan...\n")

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([search_query])
