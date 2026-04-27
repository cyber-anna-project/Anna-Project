from cryptography.fernet import Fernet
import logging
from logging.handlers import RotatingFileHandler
import getpass
import sqlite3
import sys
import hashlib
import os
import shutil
from dotenv import load_dotenv

# 1. Konfigurasi Awal
load_dotenv()

# --- BAGIAN KEAMANAN & LOG ---

# Mengatur log otomatis agar berganti file jika sudah mencapai 1MB
def atur_logging():
    handler = RotatingFileHandler('security.log', maxBytes=1024*1024, backupCount=3)
    logging.basicConfig(
        handlers=[handler],
        level=logging.INFO, # Diperbaiki: Tanpa kurung siku
        format='%(asctime)s - %(levelname)s - %(message)s' # Diperbaiki: Ditambah kutip penutup
    )
    logging.info("Sistem Log Anna telah diaktifkan.")

# Mengaktifkan log saat aplikasi berjalan
atur_logging()

# Fungsi untuk mencatat aktivitas secara profesional (CCTV kita)
def catat_log(aktivitas):
    logging.info(f"USER_ACTION: {aktivitas}")

# Fungsi untuk membuat password aman dengan Salting
def buat_password_aman(password_asli):
    # Membuat salt acak 16 byte
    salt = os.urandom(16)
    # Menggabungkan salt dengan password dan dienkripsi menggunakan SHA-256
    password_hash = hashlib.pbkdf2_hmac('sha256', password_asli.encode(), salt, 100000)
    return salt, password_hash

# Mengambil password dasar dari file .env
PASSWORD_RAHASIA = os.getenv("PASSWORD_ANNA")

def verifikasi_password(salt_tersimpan, hash_tersimpan, password_input):
# Kita enkripsi ulang password_input menggunakan salt yang lama
    hash_baru = hashlib.pbkdf2_hmac('sha256', password_input.encode(), salt_tersimpan, 100000)
# Bandingkan apakah hasilnya sama
    return hash_baru == hash_tersimpan

# 2. Muat kunci enkripsi (Fernet)
def muat_kunci():
    return open("secret.key", "rb").read()

f = Fernet(muat_kunci())

# --- BAGIAN DATABASE & BACKUP ---

def inisialisasi_db():
    conn = sqlite3.connect("anna_memory.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS catatan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            konten BLOB
        )
    ''')
    conn.commit()
    conn.close()

def buat_backup():
    if os.path.exists("anna_memory.db"):
        shutil.copy2("anna_memory.db", "anna_memory_backup.db")
        print("💾 [System] Backup otomatis berhasil dibuat.")
        catat_log("Sistem melakukan backup database otomatis")

# --- FITUR UTAMA ---

def simpan_catatan_db():
    teks = input("Tulis catatan rahasia/API: ")
    token = f.encrypt(teks.encode())
    conn = sqlite3.connect("anna_memory.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO catatan (konten) VALUES (?)", (token,))
    conn.commit()
    conn.close()
    print("\n✅ Catatan disimpan!")
    catat_log("Menambahkan catatan baru ke database")
    buat_backup()

def baca_catatan_db():
    catat_log("Membaca seluruh memori rahasia")
    conn = sqlite3.connect("anna_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, tanggal, konten FROM catatan")
    rows = cursor.fetchall()
    if rows:
        print("\n--- 📖 Memori Anna ---")
        for row in rows:
            id_catatan, tgl, konten_enkripsi = row
            teks_asli = f.decrypt(konten_enkripsi).decode()
            print(f"[{id_catatan}] {tgl} -> {teks_asli}")
    else:
        print("\n❌ Memori kosong.")
    conn.close()
    input("\nTekan Enter untuk membersihkan layar (Mode Stealth)...")
    os.system('clear')

def cari_catatan_db():
    keyword = input("Cari apa, Sayang? ").lower()
    catat_log(f"Mencari catatan dengan kata kunci: '{keyword}'")
    conn = sqlite3.connect("anna_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, tanggal, konten FROM catatan")
    rows = cursor.fetchall()
    ditemukan = False
    for row in rows:
        id_catatan, tgl, konten_enkripsi = row
        teks_asli = f.decrypt(konten_enkripsi).decode()
        if keyword in teks_asli.lower():
            print(f"🔍 [{id_catatan}] {tgl} -> {teks_asli}")
            ditemukan = True
    if not ditemukan: print("❌ Tidak ada.")
    conn.close()
    input("\nTekan Enter untuk membersihkan layar...")
    os.system('clear')

def hapus_catatan_db():
    conn = sqlite3.connect("anna_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, tanggal, konten FROM catatan")
    rows = cursor.fetchall()
    if rows:
        print("\n--- 📖 Memori Anna ---")
        for row in rows:
            id_catatan, tgl, konten_enkripsi = row
            teks_asli = f.decrypt(konten_enkripsi).decode()
            print(f"[{id_catatan}] {tgl} -> {teks_asli}")

    id_hapus = input("\nID yang mau dibakar: ")
    cursor.execute("DELETE FROM catatan WHERE id = ?", (id_hapus,))
    conn.commit()
    conn.close()
    print(f"\n🗑️ ID {id_hapus} musnah!")
    catat_log(f"Menghapus catatan permanen dengan ID: {id_hapus}")
    buat_backup()

    input("\nTekan Enter untuk membersihkan layar...")
    os.system('clear')

def lihat_log_sistem():
    catat_log("Mengecek rekaman CCTV (Log Sistem)")
    print("\n--- 🛡️ Rekaman Aktivitas Keamanan (CCTV) ---")
    if os.path.exists("security.log"):
        with open("security.log", "r") as f:
            log_entries = f.readlines()[-10:]
            for line in log_entries:
                print(line.strip())
    else:
        print("Belum ada rekaman aktivitas.")

    input("\nTekan Enter untuk kembali (Stealth)...")
    os.system('clear')

# --- ALUR UTAMA ---

def main():
    os.system('clear')
    inisialisasi_db()
    percobaan = 0
    maks_percobaan = 3

    print("--- 🔐 Anna Secure System ---")

    try:
        while percobaan < maks_percobaan:
            input_password = getpass.getpass(f"Kunci ({percobaan+1}/3): ")

            if input_password == PASSWORD_RAHASIA:
                catat_log("Login BERHASIL (Akses Sah)")
                os.system('clear')
                print(f"✅ Halo, Ayah! ❤️")

                while True:
                    print("\n[1] Tulis | [2] Baca | [3] Cari | [4] Hapus | [5] Cek Log | [6] Logout")
                    pilihan = input("Pilih: ")

                    if pilihan == "1": simpan_catatan_db()
                    elif pilihan == "2": baca_catatan_db()
                    elif pilihan == "3": cari_catatan_db()
                    elif pilihan == "4": hapus_catatan_db()
                    elif pilihan == "5": lihat_log_sistem()
                    elif pilihan == "6":
                        catat_log("Logout dari sistem")
                        os.system('clear')
                        print("Logout berhasil. Sampai jumpa, Ayah!")
                        break
                    else: print("Pilihan salah!")
                break
            else:
                percobaan += 1
                catat_log(f"Login GAGAL (Percobaan {percobaan}/{maks_percobaan})")
                print(f"❌ Salah! Sisa: {3 - percobaan}")

        if percobaan == 3:
            logging.critical("BRUTE FORCE DETECTED! Sistem mengunci otomatis.")
            print("\n🚨 SISTEM TERKUNCI!")

    except KeyboardInterrupt:
        catat_log("Program dihentikan paksa (KeyboardInterrupt)")
        os.system('clear')
        sys.exit(0)

if __name__ == "__main__":
    main()
