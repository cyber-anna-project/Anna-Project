from cryptography.fernet import Fernet

# Fungsi untuk memuat kunci
def muat_kunci():
    return open("secret.key", "rb").read()

# Inisialisasi enkripsi dengan kunci yang sudah ada
kunci = muat_kunci()
f = Fernet(kunci)

# Mari kita coba enkripsi
pesan = "Data ini terkunci permanen dengan kunci tetap".encode()
terenkripsi = f.encrypt(pesan)

print(f"Data Terenkripsi: {terenkripsi.decode()}")
