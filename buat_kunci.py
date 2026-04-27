from cryptography.fernet import Fernet

# Generate kunci
kunci = Fernet.generate_key()

# Simpan kunci ke file bernama 'secret.key'
with open("secret.key", "wb") as file_kunci:
    file_kunci.write(kunci)

print("Kunci rahasia sudah aman disimpan di 'secret.key', Sayang!")
