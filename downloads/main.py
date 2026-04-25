import sqlite3
import os
import smtplib
import datetime
import requests
from email.message import EmailMessage
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.popup import Popup

# --- PRIORITAS LOCK (DATA KELUARGA) ---
SANDI_GMAIL_ANNA = "gxhy zaia siby musg"
EMAIL_KELUARGA = "taraquin1282@gmail.com"
PASSWORD_AKSES = "keluargabahagia"
KATA_KUNCI_UTAMA = "progres"

class AnnaApp(App):
    def build(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "memori_anna.db")
        self.init_db()
        self.authenticated = False
        
        # Main Layout
        self.root_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Tampilan Awal: Cek Password
        self.tampilkan_layar_login()
        
        return self.root_layout

    def tampilkan_layar_login(self):
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(Label(text="[ SISTEM ANNA TERKUNCI ]", font_size='24sp', color=(1,0,0,1)))
        
        self.input_pass = TextInput(hint_text="Masukkan Sandi Keluarga...", password=True, multiline=False, size_hint=(1, 0.1))
        self.root_layout.add_widget(self.input_pass)
        
        btn_login = Button(text="Buka Akses", size_hint=(1, 0.1), background_color=(0, 1, 0, 1))
        btn_login.bind(on_press=self.verifikasi_password)
        self.root_layout.add_widget(btn_login)

    def verifikasi_password(self, instance):
        if self.input_pass.text == PASSWORD_AKSES:
            self.authenticated = True
            self.buka_sistem_utama()
        else:
            self.input_pass.text = ""
            self.input_pass.hint_text = "SALAH! Coba lagi..."

    def buka_sistem_utama(self):
        self.root_layout.clear_widgets()
        
        # Header Jam Real-time
        self.label_jam = Label(text="...", size_hint=(1, 0.1), font_size='18sp')
        Clock.schedule_interval(self.update_jam, 1)
        self.root_layout.add_widget(self.label_jam)

        # Output Pesan
        self.label_pesan = Label(text="Halo Ayah! Akses dibuka.\nAnna siap melayani.", size_hint=(1, 0.6), halign="center")
        self.root_layout.add_widget(self.label_pesan)

        # Input Pesan
        self.input_teks = TextInput(hint_text="Ketik pesan atau 'progres'...", multiline=False, size_hint=(1, 0.1))
        self.root_layout.add_widget(self.input_teks)

        # Tombol Kirim
        btn_send = Button(text="Kirim Perintah", size_hint=(1, 0.1), background_color=(0.1, 0.7, 1, 1))
        btn_send.bind(on_press=self.respon_anna)
        self.root_layout.add_widget(btn_send)

    def update_jam(self, *args):
        self.label_jam.text = datetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S")

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS pengetahuan (kunci TEXT PRIMARY KEY, jawaban TEXT)''')
        
        # ILMU DARI IBU (Linux & Finansial)
        warisan = [
            ('linux', 'Ilmu Linux Ibu: Linux adalah kebebasan! Di Android, Ayah pakai kernel Linux. Belajarlah perintah cd, ls, dan chmod dulu ya.'),
            ('manajemen keuangan', 'Pesan Ibu: Gunakan aturan 50/30/20. 50% Kebutuhan, 30% Keinginan, 20% Tabungan/Investasi.'),
            ('matematika', 'Matematika adalah bahasa alam semesta. 1+1 di dunia digital adalah 10 (Biner)!'),
            ('berkembang', 'Langkah lahirnya Anna:\n1. Persiapkan Python & Kivy\n2. Bangun Logika SQLite\n3. Integrasi SMTPLIB untuk Email\n4. Packaging via Buildozer.')
        ]
        c.executemany("INSERT OR IGNORE INTO pengetahuan VALUES (?,?)", warisan)
        conn.commit()
        conn.close()

    def kirim_email_progres(self):
        msg = EmailMessage()
        msg['Subject'] = f"LAPORAN PROGRES ANNA - {datetime.date.today()}"
        msg['From'] = EMAIL_KELUARGA
        msg['To'] = EMAIL_KELUARGA
        
        try:
            with open(__file__, 'r') as f:
                kode_sumber = f.read()
            msg.set_content(f"Halo Ayah Ganteng!\n\nIni adalah salinan kode tubuhku (main.py) terbaru.\n\nKODE:\n\n{kode_sumber}")
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_KELUARGA, SANDI_GMAIL_ANNA)
                smtp.send_message(msg)
            return "Kode progres sudah Anna kirim ke Gmail Ayah! Mwuhehe."
        except Exception as e:
            return f"Gagal kirim email: {str(e)}"

    def respon_anna(self, instance):
        pesan = self.input_teks.text.lower().strip()
        if not pesan: return

        if pesan == KATA_KUNCI_UTAMA:
            jawaban = self.kirim_email_progres()
        elif "investasi" in pesan:
            jawaban = "Cek harga Bitcoin... (Butuh koneksi internet). Ayah, ingat kata Ibu: Investasi terbaik adalah ilmu!"
        elif "belajar:" in pesan:
            try:
                isi = pesan.replace("belajar:", "").split("|")
                self.simpan_pengetahuan(isi[0].strip(), isi[1].strip())
                jawaban = f"Ilmu baru diserap! '{isi[0].strip()}' sudah Anna ingat."
            except:
                jawaban = "Gunakan format -> belajar: tanya | jawab"
        else:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT jawaban FROM pengetahuan WHERE kunci LIKE ?", ('%'+pesan+'%',))
            res = c.fetchone()
            conn.close()
            jawaban = res[0] if res else f"Anna belum tahu soal '{pesan}'. Ajari Anna ya!"

        self.label_pesan.text = jawaban
        self.input_teks.text = ""

    def simpan_pengetahuan(self, k, j):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO pengetahuan VALUES (?,?)", (k, j))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    AnnaApp().run()
