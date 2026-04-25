# Sel buildozer.spec - Versi Estetik & Ringan
spec_content = """
[app]
title = Anna AI
package.name = anna_ai
package.domain = org.keluargabahagia
source.dir = .
source.include_exts = py,png,jpg,kv,db,txt,atlas,env

# Versi aplikasi
version = 0.2

# Requirements (DITAMBAHKAN python-dotenv)
requirements = python3,kivy,gtts,requests,urllib3,charset-normalizer,idna,certifi,python-dotenv

icon.filename = icon_anna.png
orientation = portrait

# Izin Dasar
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.archs = arm64-v8a
android.accept_sdk_license = True
"""

with open("buildozer.spec", "w") as f:
    f.write(spec_content.strip())

print("✅ buildozer.spec sudah dioptimasi dengan sistem keamanan .env, Ayah! mwuhehe.")

