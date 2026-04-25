import sqlite3, os, smtplib, ssl, threading, requests, signal
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv

# --- Modul Suara & UI Kivy ---
from gtts import gTTS
from kivy.core.audio import SoundLoader
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.core.window import Window

# === JALUR RAHASIA (SISTEM KEAMANAN) ===
load_dotenv()
SANDI_GMAIL_ANNA = os.getenv("SANDI_GMAIL")
EMAIL_KELUARGA = os.getenv("EMAIL_USER")
PASSWORD_AKSES = os.getenv("SANDI_ANNA")

KATA_KUNCI_PROGRES = "progres"
KATA_KUNCI_UPDATE = "update"
NAMA_FILE_DB = "anna_v5_final.db"
API_BTC = "https://api.coindesk.com/v1/bpi/currentprice.json"

def bersihkan_input(teks):
    teks = teks.strip()
    aman = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(c for c in teks if c in aman)

class AnnaApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        self.init_db()
        self.is_logged_in = False
        return self.layout_utama()

    def layout_utama(self):
        self.main_layout = BoxLayout(orientation='vertical', padding=15, spacing=20)
        from kivy.uix.floatlayout import FloatLayout
        self.header_area = FloatLayout(size_hint=(1, 0.45))

        # JAM SUDAH DIPERBAIKI: Mengikuti waktu sistem langsung
        self.lbl_jam = Label(text="... : ...", font_size='22sp', color=(0, 0.9, 1, 1),
                             pos_hint={'x': 0.05, 'top': 0.98}, size_hint=(None, None), size=(150, 40))
        Clock.schedule_interval(self.update_sistem, 1)
        self.header_area.add_widget(self.lbl_jam)

        # CEK WAJAH: Pastikan file 'wajah_anna.png' ada di folder yang sama
        img_src = "wajah_anna.png" if os.path.exists("wajah_anna.png") else "icon_anna.png"
        if os.path.exists(img_src):
            self.wajah_img = Image(source=img_src, pos_hint={'center_x': 0.5, 'center_y': 0.4}, size_hint=(0.95, 0.95))
            self.header_area.add_widget(self.wajah_img)
            Clock.schedule_once(lambda dt: self.animate_anna_float(self.wajah_img))
        else:
            self.header_area.add_widget(Label(text="[ Menunggu Wajah... ]", color=(0.5, 0.5, 0.5, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5}))

        self.main_layout.add_widget(self.header_area)

        self.input_area = BoxLayout(orientation='horizontal', size_hint=(1, 0.06), spacing=10)
        self.inp_input = TextInput(password=True, multiline=False, hint_text="Otorisasi...", background_color=(0.1, 0.1, 0.1, 1), foreground_color=(0, 1, 1, 1))
        self.input_area.add_widget(self.inp_input)

        self.btn_aksi = Button(text="AKSES", size_hint=(0.25, 1), background_color=(0, 0.6, 0.8, 1), bold=True)
        self.btn_aksi.bind(on_press=self.proses_utama)
        self.input_area.add_widget(self.btn_aksi)
        self.main_layout.add_widget(self.input_area)

        self.dashboard = GridLayout(cols=4, spacing=10, size_hint=(1, 0.18))
        self.dashboard.add_widget(self.create_game_btn("ASET", "icon_wallet.png", self.cek_saldo_wallet))
        self.dashboard.add_widget(self.create_game_btn("ANALISIS", "icon_invest.png", self.cek_investasi_realtime))
        self.dashboard.add_widget(self.create_game_btn("DATA", "icon_news.png", self.show_news))
        self.dashboard.add_widget(self.create_game_btn("KOM", "icon_chat.png", self.start_chat))
        self.main_layout.add_widget(self.dashboard)

        self.footer = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))
        self.scroll_msg = ScrollView()
        self.lbl_msg = Label(text=">> Masukkan Sandi Otorisasi...", halign='left', valign='top', size_hint_y=None, color=(0, 1, 0, 1), font_size='13sp')
        self.lbl_msg.bind(texture_size=self.lbl_msg.setter('size'))
        self.scroll_msg.add_widget(self.lbl_msg)
        self.footer.add_widget(self.scroll_msg)
        self.main_layout.add_widget(self.footer)

        return self.main_layout

    def animate_anna_float(self, widget):
        anim = Animation(pos_hint={'center_y': 0.42}, duration=2.5, t='in_out_quad') + Animation(pos_hint={'center_y': 0.40}, duration=2.5, t='in_out_quad')
        anim.repeat = True
        anim.start(widget)

    def create_game_btn(self, text, icon_src, func):
        btn = Button(background_color=(0.1, 0.1, 0.1, 0))
        layout = BoxLayout(orientation='vertical', padding=5)
        icon = Image(source=icon_src) if os.path.exists(icon_src) else Label(text="◈", color=(0, 0.8, 1, 1))
        layout.add_widget(icon)
        layout.add_widget(Label(text=text, font_size='10sp', size_hint_y=0.3, bold=True))
        btn.add_widget(layout)
        btn.bind(on_press=func)
        return btn

    def init_db(self):
        conn = sqlite3.connect(NAMA_FILE_DB)
        conn.execute("CREATE TABLE IF NOT EXISTS memori (id INTEGER PRIMARY KEY, kunci TEXT, isi TEXT)")
        conn.close()

    def update_sistem(self, *args):
        # JAM DISESUAIKAN: Mengambil waktu lokal perangkat langsung
        sekarang = datetime.now()
        self.lbl_jam.text = sekarang.strftime('%H:%M:%S WIB')

    def bicara(self, teks):
        def proses():
            try:
                tts = gTTS(text=teks, lang='id')
                tts.save("v.mp3")
                Clock.schedule_once(lambda dt: self._putar_suara("v.mp3"))
            except Exception as e:
                print(f"Gagal bicara: {e}")
        threading.Thread(target=proses, daemon=True).start()

    def _putar_suara(self, file):
        s = SoundLoader.load(file)
        if s: s.play()

    def proses_utama(self, instance):
        sandi_bersih = bersihkan_input(self.inp_input.text)
        if not self.is_logged_in:
            if sandi_bersih == PASSWORD_AKSES:
                self.is_logged_in = True
                self.lbl_msg.text = ">> OTORISASI DITERIMA. mwuhehe."
                self.bicara("Akses diterima, Komandan!")
                self.inp_input.password = False
                self.inp_input.text = ""
                self.btn_aksi.text = "KIRIM"
                self.btn_aksi.background_color = (0, 0.8, 0, 1)
            else:
                self.lbl_msg.text = ">> GAGAL. Akses Ditolak!"
                self.bicara("Akses ditolak!")
        else:
            self.logika_anna(sandi_bersih)

    def logika_anna(self, pesan):
        p = pesan.lower()
        if p == KATA_KUNCI_UPDATE or p == KATA_KUNCI_PROGRES:
            self.lbl_msg.text = f">> Menjalankan {p}... Cek Gmail."
            self.kirim_email(f"REPORT {p.upper()}", f"Laporan {p} Anna terbaru.", "anna.py")
        else:
            self.lbl_msg.text = f">> Log: {pesan}"
        self.inp_input.text = ""

    def kirim_email(self, sub, kont, lamp=None):
        def prs():
            try:
                m = EmailMessage()
                m['Subject'] = f"{sub} - {datetime.now().strftime('%d/%m/%Y')}"
                m['From'] = EMAIL_KELUARGA
                m['To'] = EMAIL_KELUARGA
                m.set_content(kont)
                if lamp and os.path.exists(lamp):
                    with open(lamp, "rb") as f: m.add_attachment(f.read(), maintype="text", subtype="plain", filename=lamp)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
                    s.login(EMAIL_KELUARGA, SANDI_GMAIL_ANNA)
                    s.send_message(m)
            except: pass
        threading.Thread(target=prs, daemon=True).start()

    def cek_saldo_wallet(self, instance): self.lbl_msg.text = ">> Dompet aman, Komandan."
    def cek_investasi_realtime(self, instance):
        self.lbl_msg.text = ">> Cek BTC..."
        threading.Thread(target=self._fetch_btc, daemon=True).start()

    def _fetch_btc(self):
        try:
            res = requests.get(API_BTC, timeout=5).json()
            price = res['bpi']['USD']['rate']
            Clock.schedule_once(lambda dt: setattr(self.lbl_msg, 'text', f">> BTC: {price} USD"))
        except: pass

    def show_news(self, instance): self.lbl_msg.text = ">> Belum ada data baru."
    def start_chat(self, instance): self.inp_input.focus = True

    # PENGHANCUR MANDIRI: Menghapus audio saat aplikasi berhenti
    def on_stop(self):
        if os.path.exists("v.mp3"):
            try:
                os.remove("v.mp3")
            except:
                pass

if __name__ == '__main__':
    def signal_handler(sig, frame):
        print('\n[SYSTEM] Mematikan Anna... Menghancurkan jejak.')
        try:
            App.get_running_app().stop()
        except:
            pass
        os._exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    os.environ['DISPLAY'] = ':0'
    
    try:
        AnnaApp().run()
    except Exception as e:
        print(f"Fatal Error: {e}")
        os._exit(1)
