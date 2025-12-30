# 📋 STEP BY STEP - CARA MENJALANKAN APLIKASI

**Panduan ini untuk PEMULA - sangat detail dan mudah diikuti!**

---

## 🎯 OVERVIEW

Untuk menjalankan aplikasi, kamu perlu:

1. ✅ Install Python
2. ✅ Download/Clone project dari GitHub
3. ✅ Install dependencies (library)
4. ✅ Jalankan aplikasi

**Total waktu: ~10-15 menit**

---

## STEP 1️⃣: Install Python

### Windows:

**1. Buka browser, pergi ke:** https://www.python.org/downloads/

**2. Download yang "Latest"** (contoh: Python 3.12.x)

**3. Double-click file yang di-download**

**4. ⚠️ PENTING! Centang "Add Python to PATH"**

```
☑ Add Python 3.x to PATH  <-- HARUS DICENTANG!
```

**5. Klik "Install Now"**

**6. Tunggu sampai selesai**

### Mac:

```bash
# Install menggunakan Homebrew:
brew install python3
```

Atau download dari https://www.python.org/downloads/

### Linux:

```bash
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install python3 python3-pip

# Fedora:
sudo dnf install python3 python3-pip
```

---

## STEP 2️⃣: Verifikasi Python Terinstall

### Buka Command Prompt / Terminal

**Windows:**
- Tekan `Win + R`
- Ketik: `cmd`
- Tekan Enter

**Mac/Linux:**
- Buka aplikasi "Terminal"

### Cek versi Python:

Ketik di terminal:

```bash
python --version
```

**Expected output:**

```
Python 3.8.0  (atau versi lebih tinggi)
```

✅ Jika keluar versi = Python sudah install dengan benar!

❌ Jika error "python not found" = Restart computer atau ulangi Step 1

---

## STEP 3️⃣: Download Project dari GitHub

### Opsi A: Menggunakan Git (Recommended)

**1. Install Git** (jika belum ada)
- Download: https://git-scm.com/
- Install dengan default settings

**2. Buka terminal/cmd**

**3. Pergi ke folder tempat kamu mau save project:**

```bash
# Contoh: folder Documents
cd Documents
```

**4. Clone project:**

```bash
git clone https://github.com/Muhreza12/barubaru.git
```

**5. Masuk ke folder project:**

```bash
cd barubaru
```

### Opsi B: Download ZIP (Jika tidak punya Git)

**1. Buka:** https://github.com/Muhreza12/barubaru

**2. Klik tombol hijau "Code"** (kanan atas)

**3. Pilih "Download ZIP"**

**4. Extract/Unzip file yang di-download**

**5. Buka folder yang sudah di-extract**

**6. Buka Command Prompt/Terminal di folder tersebut:**

**Windows:**
- Tekan `Shift + Right Click` di folder kosong
- Pilih "Open PowerShell window here"

**Mac/Linux:**
- Buka Terminal
- Ketik: `cd /path/to/barubaru`

---

## STEP 4️⃣: Install Dependencies (Library)

Sekarang kamu harus di folder `barubaru`.

Cek dengan:

```bash
dir          # Windows
ls           # Mac/Linux
```

Kamu seharusnya lihat:
```
main.py
auth_ui_cyberpunk.py
requirements.txt
... (file-file lainnya)
```

### Install semua library:

```bash
pip install -r requirements.txt
```

⏳ **Tunggu 2-5 menit**, akan install:
- PyQt5 (UI framework)
- psycopg2 (database driver)
- dan dependencies lainnya

**Expected output di akhir:**

```
Successfully installed ...
```

✅ Jika muncul "Successfully installed" = Berhasil!

---

## STEP 5️⃣: Jalankan Aplikasi!

Di terminal yang sama, ketik:

```bash
python main.py
```

### Apa yang akan terjadi:

**Detik 0-3:**
```
✅ Connected to Railway PostgreSQL
(Splash screen muncul dengan loading bar)
```

**Detik 3-5:**
```
(Splash screen hilang)
(Login window muncul dengan UI cyberpunk)
```

### ✅ BERHASIL!

Sekarang kamu bisa:
- **Register** akun baru
- **Login** dengan test account:
  - Username: `testuser`
  - Password: `test1234`

---

## 🆘 TROUBLESHOOTING

### ❌ Error 1: `'python' is not recognized`

**Penyebab:** Python belum di-add ke PATH

**Solusi:**

1. Uninstall Python
2. Install ulang
3. **PASTIKAN centang "Add Python to PATH"**
4. Restart computer
5. Coba `python --version` lagi

---

### ❌ Error 2: `No module named 'PyQt5'`

**Penyebab:** Library belum install

**Solusi:**

```bash
pip install PyQt5
```

Tunggu sampai selesai, coba lagi `python main.py`

---

### ❌ Error 3: `No module named 'psycopg2'`

**Penyebab:** Database driver belum install

**Solusi:**

```bash
pip install psycopg2-binary
```

Tunggu sampai selesai, coba lagi `python main.py`

---

### ❌ Error 4: `Could not connect to server`

**Penyebab:** Database (Railway) tidak bisa diakses

**Solusi:**

1. Cek internet connection (harus aktif!)
2. Tunggu 5-10 detik, coba lagi
3. Cek apakah Railway server aktif
4. Jika masih error, test database:
   ```bash
   python app_db_fixed.py
   ```

---

### ❌ Error 5: Window tidak muncul / Freeze

**Penyebab:** Loading lama atau error di background

**Solusi:**

1. **Tunggu 5-10 detik** (loading database)
2. Jika masih tidak muncul:
   ```bash
   Ctrl + C  # di terminal (stop program)
   python -u main.py  # run dengan verbose
   ```
3. Lihat error message yang muncul
4. Follow troubleshooting sesuai errornya

---

### ❌ Error 6: `ModuleNotFoundError: No module named 'dashboard_ui'`

**Penyebab:** Path/folder tidak benar

**Solusi:**

1. Pastikan kamu di folder `barubaru`
2. Cek dengan `dir` atau `ls`
3. Seharusnya ada file:
   - main.py
   - dashboard_ui.py
   - auth_ui_cyberpunk.py
   - dll

4. Jika ada file yang missing, download ulang dari GitHub

---

## 📊 QUICK COMMAND REFERENCE

### Windows:

```batch
REM 1. Cek Python
python --version

REM 2. Masuk ke folder project
cd Documents\barubaru

REM 3. Install dependencies
pip install -r requirements.txt

REM 4. Run aplikasi
python main.py
```

### Mac/Linux:

```bash
# 1. Cek Python
python3 --version

# 2. Masuk ke folder project
cd ~/Documents/barubaru

# 3. Install dependencies
pip3 install -r requirements.txt

# 4. Run aplikasi
python3 main.py
```

---

## 🎯 CHECKLIST SEBELUM RUN

Sebelum jalankan `python main.py`, pastikan:

- [ ] Python sudah install (cek dengan `python --version`)
- [ ] Kamu di folder `barubaru` (cek dengan `dir` atau `ls`)
- [ ] File `main.py` ada di folder tersebut
- [ ] File `requirements.txt` ada
- [ ] Sudah jalankan `pip install -r requirements.txt`
- [ ] Internet connection aktif (untuk database)
- [ ] Tidak ada terminal/cmd error sebelumnya

✅ Semua checked? Siap jalankan `python main.py`!

---

## 💡 TIPS PENTING

1. **Internet Connection Required**: Aplikasi butuh koneksi internet karena database di Railway (cloud)

2. **First Run Agak Lambat**: Jangan khawatir, loading database pertama kali memang bisa 5-10 detik

3. **Jangan Close Terminal**: Jangan tutup terminal sambil aplikasi jalan. Klik X di aplikasi untuk close

4. **Screen Resolution**: Optimal dengan resolusi minimal 1024x768

5. **Test Account**: Kamu bisa login dengan akun test atau register yang baru

---

## 🎉 DONE!

Jika semua langkah di atas berhasil:

1. ✅ Aplikasi Crypto Insight sudah jalan
2. ✅ Kamu bisa login/register
3. ✅ Bisa akses dashboard

**Selamat! Aplikasi siap digunakan!** 🚀

---

## 📞 BUTUH BANTUAN LEBIH?

Jika masih stuck:

1. Baca section "TROUBLESHOOTING" di atas
2. Copy-paste error message dan cari di Google
3. Check di GitHub Issues
4. Hubungi developer

---

**Happy Coding!** 💻✨
