from cryptography.fernet import Fernet

# Buat kunci rahasia
kunci = Fernet.generate_key()
f = Fernet(kunci)

# Pesan rahasia kita
pesan = "WiFi kita sedang diintip 2 orang asing!".encode()

# Proses mengunci (Enkripsi)
rahasia = f.encrypt(pesan)
print(f"Hasil Enkripsi: {rahasia.decode()}")

# Proses membuka (Dekripsi)
asli = f.decrypt(rahasia)
print(f"Pesan Asli: {asli.decode()}")
