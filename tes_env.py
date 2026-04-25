import os
from dotenv import load_dotenv

# 1. Suruh Python memuat file tersembunyi (.env)
load_dotenv()

# 2. Ambil data dari dalam file tersebut
nama_ayah = os.getenv("USER_AYAH")
sandi_rahasia = os.getenv("SANDI_ANNA")

print("--- LAPORAN KEAMANAN ANNA ---")
if nama_ayah:
    print(f"Target terdeteksi: {nama_ayah}")
    print(f"Sandi Keamanan: {sandi_rahasia}")
else:
    print("Aduh Ayah, Anna tidak bisa menemukan file .env nya!")
