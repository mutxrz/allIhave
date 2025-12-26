#!/usr/bin/env python3
"""
Script untuk santri — otomatis unduh, ekstrak, dan perbaiki Chromium portable.

FITUR:
- Mode Setup (khusus admin, dijalankan sekali untuk konfigurasi awal).
- Mode Admin (untuk mengubah password user dan upload ke GitHub).
- Mode User (untuk mengunduh Chromium setelah setup).
- Mengunci wget dan menggunakan aturan sudo untuk eksekusi yang aman.
"""

import os
import shutil
import subprocess
import zipfile
import getpass
import sys
import time
import http.server
import socketserver
import json

# --- WARNA ---
class C:
    G = '\033[1;32m' # Bold Green
    Y = '\033[1;33m' # Bold Yellow
    R = '\033[1;31m' # Bold Red
    B = '\033[1;34m' # Bold Blue
    C = '\033[1;36m' # Bold Cyan
    END = '\033[0m' # RESET

# --- KONFIGURASI ---
ADMIN_PASSWORD = "s4ntr1"
USER_PASSWORD  = "patek lah"
URL = "https://download-chromium.appspot.com/dl/Linux_x64?type=snapshots"
FILE_NAME = "chrome-linux.zip"
WORK_DIR = "chrome-linux"
SUDOERS_FILE = "/etc/sudoers.d/99-modifan-rule"

# --- KONFIGURASI TAMBAHAN UNTUK SANTRI ---
# Alamat IP server untuk homepage dan halaman blokir
SANTRI_SERVER = "http://192.168.1.5:8082"

# --- FUNGSI HELPERS ---
def slow_print(text, speed=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def try_chmod_exec(path):
    try:
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return True
    except Exception: return False

# --- FUNGSI SETUP (KHUSUS ADMIN) ---
def initial_setup(username, script_path):
    slow_print(f"{C.Y}[ INFO ] Memulai proses setup awal untuk keamanan skrip...{C.END}")
    if os.geteuid() != 0:
        print(f"{C.R}[ ERROR ] Error: Mode setup harus dijalankan sebagai root. Gunakan: sudo python3 {script_path} --setup <nama_user>{C.END}")
        sys.exit(1)
    wget_path = shutil.which("wget")
    if not wget_path:
        print(f"{C.R}[ ERROR ] Error: 'wget' tidak ditemukan. Mohon install wget terlebih dahulu.{C.END}")
        sys.exit(1)
    print(f"{C.Y}[ INFO ] Mengunci {wget_path} agar hanya bisa diakses root...{C.END}")
    try:
        subprocess.run(['chown', 'root:root', wget_path], check=True)
        subprocess.run(['chmod', '700', wget_path], check=True)
        print(f"  {C.G}[ SUKSES ] Izin {wget_path} diubah menjadi 700.{C.END}")
    except Exception as e:
        print(f"{C.R}[ ERROR ] Gagal mengunci wget: {e}{C.END}")
        sys.exit(1)
    rule = f"{username} ALL=(root) NOPASSWD: /usr/bin/python3 {script_path}"
    print(f'''
{C.Y}[ INFO ] Membuat aturan sudo di {SUDOERS_FILE}...
    Aturan: {rule}{C.END}''')
    try:
        with open(SUDOERS_FILE, 'w') as f:
            f.write(rule + '\n')
        os.chmod(SUDOERS_FILE, 0o440)
        print(f"  {C.G}[ SUKSES ] Aturan sudo berhasil dibuat.{C.END}")
    except Exception as e:
        print(f"{C.R}[ ERROR ] Gagal membuat file sudoers: {e}{C.END}")
        sys.exit(1)
    slow_print(f"\n{C.G}[ SUKSES ] Setup Selesai! Pengguna '{username}' sekarang bisa menjalankan skrip dengan: sudo python3 {script_path}{C.END}")

# --- FUNGSI ADMIN ---
def change_passwords():
    print(f"{C.Y}[ INFO ] Mengubah Password...{C.END}")
    script_path = os.path.abspath(__file__)
    try:
        with open(script_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"{C.R}[ ERROR ] Gagal membaca file skrip: {e}{C.END}")
        return
    new_lines = []
    pass_changed = False
    choice = input("Password mana yang ingin diubah? (1) Admin, (2) User, (3) Keduanya, (lainnya) Batal: ")
    new_admin_pass = None
    if choice in ['1', '3']:
        new_admin_pass = getpass.getpass("Masukkan password ADMIN baru: ")
    new_user_pass = None
    if choice in ['2', '3']:
        new_user_pass = getpass.getpass("Masukkan password USER baru: ")
    if not new_admin_pass and not new_user_pass:
        print(f"{C.Y}[ INFO ] Aksi dibatalkan.{C.END}")
        return
    for line in lines:
        if new_admin_pass and line.strip().startswith('ADMIN_PASSWORD'):
            new_lines.append(f'ADMIN_PASSWORD = "{new_admin_pass}"\n')
            pass_changed = True
        elif new_user_pass and line.strip().startswith('USER_PASSWORD'):
            new_lines.append(f'USER_PASSWORD  = "{new_user_pass}"\n')
            pass_changed = True
        else:
            new_lines.append(line)
    if pass_changed:
        try:
            with open(script_path, 'w') as f:
                f.writelines(new_lines)
            print(f"{C.G}[ SUKSES ] Password berhasil diubah.{C.END}")
            print(f"{C.Y}[ ERROR ] Perubahan akan aktif setelah skrip dijalankan ulang.{C.END}")
        except Exception as e:
            print(f"{C.R}[ ERROR ] Gagal menulis perubahan ke file: {e}{C.END}")
    else:
        print(f"{C.Y}[ INFO ] Tidak ada password yang diubah.{C.END}")

def admin_actions():
    slow_print(f"{C.G}[ INFO ] Mode ADMIN aktif.{C.END}")
    while True:
        print(f"\n{C.B}--- Menu Admin ---
{C.END}")
        print("1. Ubah Password")
        print(f"2. {C.Y}Keluar{C.END}")
        choice = input("Masukkan pilihan: ")
        if choice == '1':
            change_passwords()
        elif choice == '2':
            print(f"{C.Y}[ INFO ] Keluar dari mode admin.{C.END}")
            break
        else:
            print(f"{C.R}[ ERROR ] Pilihan tidak valid.{C.END}")

# --- FUNGSI UTAMA ---
def secure_permissions(chromium_dir, extension_dir, user):
    print(f"{C.Y}[ INFO ] Menerapkan izin keamanan berlapis...{C.END}")
    try:
        # 1. Seluruh direktori instalasi dimiliki oleh user terlebih dahulu agar chrome bisa menulis cache
        print(f"  {C.Y}[ INFO ] Mengatur kepemilikan awal ke {user}...{C.END}")
        subprocess.run(['chown', '-R', f'{user}:{user}', chromium_dir], check=True)
        print(f"  {C.G}[ SUKSES ] Kepemilikan awal diatur ke {user}.{C.END}")

        # 2. Kunci folder ekstensi, hanya bisa dibaca oleh user
        print(f"  {C.Y}[ INFO ] Mengunci folder ekstensi...{C.END}")
        subprocess.run(['chown', '-R', 'root:root', extension_dir], check=True)
        subprocess.run(['chmod', '755', extension_dir], check=True) # rwxr-xr-x for dir
        for root, dirs, files in os.walk(extension_dir):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o755)
            for f in files:
                os.chmod(os.path.join(root, f), 0o644) # rw-r--r-- for files
        print(f"  {C.G}[ SUKSES ] Folder ekstensi dikunci (read-only untuk user).{C.END}")

        # 3. Kunci skrip pembungkus dan executable asli
        print(f"  {C.Y}[ INFO ] Mengunci file executable chrome...{C.END}")
        chrome_wrapper_path = os.path.join(chromium_dir, "chrome")
        chrome_real_path = os.path.join(chromium_dir, ".chrome")
        if os.path.exists(chrome_wrapper_path):
            os.chown(chrome_wrapper_path, 0, 0)
            os.chmod(chrome_wrapper_path, 0o755) # rwxr-xr-x
        if os.path.exists(chrome_real_path):
            os.chown(chrome_real_path, 0, 0)
            os.chmod(chrome_real_path, 0o755) # rwxr-xr-x
        print(f"  {C.G}[ SUKSES ] File executable chrome dikunci.{C.END}")
        
    except Exception as e:
        print(f"{C.R}[ ERROR ] Gagal menerapkan izin keamanan: {e}{C.END}")
        sys.exit(1)

def fix_chrome_permissions():
    print(f"{C.Y}[ INFO ] Memperbaiki izin file chrome agar executable...{C.END}")
    target_dir = "/home/santri/chrom/chrome-linux/chrome-linux"
    # Daftar file penting yang harus bisa dieksekusi
    executables_to_fix = [
        "chrome",
        "chrome_crashpad_handler",
        "chrome-sandbox",
        "nacl_helper",
        "xdg-settings"
    ]
    try:
        for root, _, files in os.walk(target_dir):
            for f in files:
                # Cek apakah file ada dalam daftar yang harus diperbaiki
                # atau jika namanya diawali 'chrome' (untuk jaga-jaga)
    except Exception as e:
        print(f"{C.R}[ ERROR ] Gagal memperbaiki izin: {e}{C.END}")
