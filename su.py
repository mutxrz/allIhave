#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Anjay Root Shell
Sebuah shell interaktif sederhana yang berjalan di dalam Python.
Jika skrip ini dijalankan sebagai root, semua perintah yang diketik di prompt-nya
akan dieksekusi dengan hak akses root.
"""

import os
import sys
import subprocess
import shlex

# --- WARNA ---
class C:
    G = '\033[92m'  # GREEN
    Y = '\033[93m'  # YELLOW
    R = '\033[91m'  # RED
    B = '\033[01;34m'  # BLUE
    END = '\033[0m' # RESET

def run_interactive_root_shell():
    """
    Fungsi utama untuk menjalankan loop shell interaktif.
    """
    # Dapatkan nama host untuk ditampilkan di prompt
    hostname = os.uname().nodename
    
    # Dapatkan nama pengguna yang menjalankan skrip (bukan 'root')
    try:
        user = os.environ.get('SUDO_USER', os.getlogin())
    except OSError:
        user = "unknown"

    os.system('clear') # Tambahkan ini untuk membersihkan layar sebelum pesan selamat datang
    print(f"{C.G}--- Selamat Datang di Anjay Root Shell ---{C.END}")
    print(f"Anda sekarang beroperasi sebagai {C.R}root{C.END}.")
    print(f"Ketik '{C.Y}exit{C.END}' atau '{C.Y}quit{C.END}' untuk keluar.")
    print("-" * 40)

    while True:
        try:
            # Membuat prompt yang terlihat seperti shell sungguhan
            # Contoh: [root@hostname ~]#
            prompt = f"{C.G}{user}@{hostname}{C.END}:{C.B}{os.getcwd()}{C.END}# {C.END}"
            
            # Membaca input dari pengguna
            # Diubah untuk mengatasi masalah terminal di mana prompt tidak muncul
            print(prompt, end='', flush=True)
            command = input()

            # Menghapus spasi di awal dan akhir
            stripped_command = command.strip()

            if not stripped_command:
                # Jika hanya menekan Enter, lanjutkan ke iterasi berikutnya
                continue

            if stripped_command.lower() in ['exit', 'quit']:
                # Jika perintah adalah 'exit' atau 'quit', keluar dari loop
                print(f"\n{C.Y}Keluar dari Anjay Root Shell...{C.END}")
                break
            
            # Menangani perintah 'cd' dengan aturan keamanan khusus
            if stripped_command.startswith('cd'):
                try:
                    # Mendapatkan argumen direktori, default ke '~' jika tidak ada
                    parts = stripped_command.split(None, 1)
                    target_arg = parts[1] if len(parts) > 1 else '~'

                    # Resolve argumen ke path absolut untuk pemeriksaan
                    abs_target_path = os.path.abspath(os.path.expanduser(target_arg))

                    # Pemeriksaan keamanan: hanya izinkan cd di dalam /home/santri
                    if abs_target_path.startswith('/home/santri/') or abs_target_path == '/home/santri':
                        os.chdir(abs_target_path)
                    else:
                        # Jika tidak diizinkan, blokir
                        print(f"{C.R}[!] Akses 'cd' dibatasi hanya untuk direktori di dalam /home/santri.{C.END}")
                
                except FileNotFoundError:
                    target_display = parts[1] if len(parts) > 1 else ''
                    print(f"bash: cd: {target_display}: No such file or directory")
                except Exception as e:
                    print(f"Error: {e}")
                
                continue # Selalu lanjutkan setelah loop 'cd' selesai

            # Aturan keamanan untuk perintah berbahaya lainnya
            if (stripped_command.startswith('chmod') or 
                ' /' in stripped_command or 
                stripped_command.startswith('passwd')):
                print(f"{C.R}[!] Perintah ini diblokir karena berpotensi berbahaya.{C.END}")
                continue

            # Jalankan perintah secara langsung (tanpa shell) untuk menghindari masalah
            # lingkungan shell yang aneh. Ini akan menonaktifkan fitur seperti pipe (|).
            try:
                command_parts = shlex.split(stripped_command)
                if command_parts:
                    subprocess.run(
                        command_parts, 
                        check=False, 
                        stdout=sys.stdout, 
                        stderr=sys.stdout
                    )
            except Exception as e:
                print(f"Anjay Shell Error: {e}")

        except KeyboardInterrupt:
            # Menangani Ctrl+C dengan baik
            print(f"\n{C.Y}Keyboard interrupt diterima. Ketik 'exit' untuk keluar.{C.END}")
            continue
        except EOFError:
            # Menangani Ctrl+D
            print(f"\n{C.Y}EOF diterima. Keluar dari shell.{C.END}")
            break

def main():
    """
    Pintu masuk utama skrip.
    """
    # Periksa apakah skrip dijalankan sebagai root
    if os.geteuid() != 0:
        print(f"{C.R}[!] Error: Hak akses root dibutuhkan.{C.END}")
        print(f"{C.Y}Skrip ini harus dijalankan sebagai root atau melalui aturan sudoers.{C.END}")
        print(f"Contoh: sudo python3 {sys.argv[0]}")
        sys.exit(1)
    
    # Jika sudah root, jalankan shell interaktif
    run_interactive_root_shell()

if __name__ == "__main__":
    main()
