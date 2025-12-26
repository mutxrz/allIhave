import subprocess
import sys
import shutil

# Pilih mirror tercepat yang tersedia
fast_mirrors = [
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://mirrors.aliyun.com/pypi/simple/",
    "https://pypi.douban.com/simple/"
]

package= str(input("Module yg mau diinstall?: (perhatikan kapital-nggaknya!) "))
mirror = None

# Cek mirror mana yang tersedia
for m in fast_mirrors:
    if shutil.which("curl"):
        try:
            print(f"🔍 Testing mirror: {m}")
            test = subprocess.run(
                ["curl", "-I", "-m", "2", m],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if test.returncode == 0:
                mirror = m
                break
        except:
            pass

if not mirror:
    mirror = "https://pypi.org/simple"  # fallback jika mirror tidak ada

print(f"\n⚡ Menggunakan mirror tercepat: {mirror}\n")

cmd = [
    "pip3",
    "install",
    package,
    "--break-system-packages",
    "--no-cache-dir",
    "--timeout", "3",
    "--retries", "1",
    "--index-url", mirror,
]

print("🚀 Menjalankan pip ultra cepat...\n")

try:
    subprocess.run(cmd, check=True)
    print("\n✅ Selesai! "+package+" berhasil diinstall ultra cepat.")
except subprocess.CalledProcessError:
    print("\n❌ Gagal install. Mungkin jaringan lagi drop atau mirror down.")
