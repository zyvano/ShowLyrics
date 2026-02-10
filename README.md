# ✝️ Worship Engine (Checkpoint 6)

**Professional Multimedia Solution for Church.** *Lightweight, Web-Based, and Zero-Lag replacement for ProPresenter/EasyWorship.*

![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![Status](https://img.shields.io/badge/Release-Stable-green)

## 📖 Overview

**Worship Engine** adalah aplikasi presentasi lirik modern yang dirancang khusus untuk ibadah. Aplikasi ini menghilangkan kompleksitas software berat dengan menggunakan teknologi web yang ringan namun *powerful*.

Cukup install, jalankan, dan kontrol seluruh ibadah (Projector, Live Stream, Stage Display) dari Laptop, Tablet, atau HP manapun dalam jaringan WiFi yang sama.

---

## 📥 Download & Install

Tidak perlu coding atau install Python. Cukup download installer siap pakai:

1.  Masuk ke menu **[Releases](https://github.com/username/worship-engine/releases)** di sebelah kanan halaman ini.
2.  Download file installer terbaru (`.msi` atau `.exe`).
3.  Install seperti biasa.
4.  Buka shortcut **"Worship Engine"** di Desktop.
5.  Dashboard akan otomatis terbuka di browser Anda.

---

## ✨ Fitur Utama

### 🖥️ 3 Output Terpisah (Independent)
* **Main Display:** Tampilan untuk Proyektor/LED Wall dengan efek *Cinematic Motion*, *Blur*, dan *Glow*.
* **Lower Third (OBS):** Output khusus background transparan (Alpha Channel) untuk overlay Live Streaming.
* **Stage Foldback:** Monitor panggung pintar untuk Singer/WL. Teks otomatis membesar/mengecil (Auto-fit) agar selalu terbaca jelas dari jauh.

### 🎛️ Controller Canggih
* **Deep Search:** Cari lagu berdasarkan *potongan lirik*, bukan cuma judul. (Contoh: ketik "bapa engkau" ketemu "Bapa Engkau Sungguh Baik").
* **Mass Import:** Masukkan ratusan lagu format `.txt` sekaligus dalam hitungan detik.
* **Preset System:** Simpan gaya tampilan (Tema, Font, Warna) dan load otomatis saat aplikasi dinyalakan.

### ⚡ Integrasi & Workflow
* **Resolume Arena (OSC):** Trigger video/lighting di Resolume Arena langsung dari Controller (Port 7000).
* **Smart Shortcuts:** Navigasi super cepat menggunakan keyboard tanpa perlu mouse.

---

## 🔗 Quick Link

Setelah aplikasi berjalan, buka URL berikut di browser (Chrome/Edge):

| Menu | URL | Fungsi |
| :--- | :--- | :--- |
| **Dashboard** | `http://localhost:8000/` | Halaman Utama & Panduan. |
| **Controller** | `http://localhost:8000/control` | Panel Operator (Lirik & Setting). |
| **Main Display** | `http://localhost:8000/display` | Output ke Layar Besar. |
| **Lower Third** | `http://localhost:8000/lowerthird` | Output ke OBS/vMix. |
| **Foldback** | `http://localhost:8000/foldback` | Output ke Monitor Panggung. |

> **Tips:** Jika ingin mengontrol dari HP/Tablet, ganti `localhost` dengan **IP Address Laptop** (misal: `192.168.1.10:8000/control`).

---

## ⌨️ Shortcut Keyboard
### Navigasi
* `⬅` / `➡` : Next dan Previous Slide
* `Ctrl + C` : Clear Screen

### Lompat Bagian (Jump)
* `V` : Lompat ke Verse 1.
* `C` : Lompat ke Chorus 1.
* `B` : Lompat ke Bridge.

### Quick Tagging (Shift + Key)
*Klik slide lalu tekan kombinasi ini untuk mewarnai slide:*
* `Shift + V` : Tag Verse (Biru)
* `Shift + C` : Tag Chorus (Merah)
* `Shift + P` : Tag Pre-Chorus (Kuning)
* `Shift + B` : Tag Bridge (Hijau)

---

## 📂 Lokasi Data

Semua data lagu dan preset Anda tersimpan aman di folder:
`Documents/WorshipEngineData/`

* `songs.json` : Database lagu.
* `*_presets.json` : Settingan tampilan.
* Anda bisa mem-backup folder ini jika ingin pindah laptop.

---

**Developed with ❤️ by JMultimedia.**
