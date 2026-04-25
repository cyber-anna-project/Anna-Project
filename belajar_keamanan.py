# Anna akan ajari cara baca file "Brankas" kita
nama_file = "rahasia.text"

try:
    with open(nama_file, "r") as f:
        isi_sandi = f.read().strip()
        print("Anna berhasil membaca sandi Ayah!")
        print("Isinya adalah:", isi_sandi)
except PermissionError:
    print("Akses ditolak! Izin file terlalu ketat, Ayah.")
