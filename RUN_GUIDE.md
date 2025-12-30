# 🚀 Panduan Menjalankan Crypto Insight

## Prasyarat (Requirements)

Sebelum menjalankan aplikasi, pastikan Anda sudah install:

### 1. **Python 3.8+**
   - Download: https://www.python.org/downloads/
   - Verifikasi: `python --version`

### 2. **Required Libraries**

```bash
# Install semua dependencies sekaligus
pip install -r requirements.txt
```

Atau install satu per satu:

```bash
pip install PyQt5
pip install psycopg2-binary
```

---

## 📦 Setup Database

Aplikasi menggunakan **Railway PostgreSQL**. Koneksi sudah dikonfigurasi di `app_db_fixed.py`.

**Pastikan:**
- ✅ Internet connection aktif
- ✅ DATABASE_URL di `app_db_fixed.py` valid
- ✅ Server Railway dapat diakses

---

## ▶️ Cara Menjalankan

### **Opsi 1: Menjalankan langsung (Recommended)**

```bash
python main.py
```

**Output yang diharapkan:**
```
✅ Connected to Railway PostgreSQL
✅ Splash screen muncul
✅ Login window terbuka
```

### **Opsi 2: Menjalankan dengan verbose output**

```bash
python -u main.py
```

### **Opsi 3: Menjalankan module spesifik**

```bash
# Test database connection saja
python app_db_fixed.py

# Test auth window saja
python auth_ui_cyberpunk.py
```

---

## 🔑 Akun Test

Anda bisa register akun baru atau gunakan yang sudah ada:

**Test Credentials:**
- Username: `testuser`
- Password: `test1234`
- Role: `user` atau `penerbit`

---

## ❌ Troubleshooting

### Error 1: `ModuleNotFoundError: No module named 'PyQt5'`

**Solusi:**
```bash
pip install PyQt5
```

### Error 2: `ModuleNotFoundError: No module named 'psycopg2'`

**Solusi:**
```bash
pip install psycopg2-binary
```

### Error 3: `❌ Connection failed: Could not connect to server`

**Solusi:**
1. Cek internet connection
2. Verifikasi DATABASE_URL di `app_db_fixed.py`
3. Pastikan Railway server aktif
4. Try di environment lain atau test dengan:
   ```bash
   python app_db_fixed.py
   ```

### Error 4: `ImportError: cannot import name 'dashboard_ui'`

**Solusi:**
- Pastikan semua file `.py` ada di root directory
- Jalankan dari folder yang benar:
  ```bash
  cd /path/to/barubaru
  python main.py
  ```

### Error 5: Window tidak muncul / Freeze

**Solusi:**
1. Tunggu 3-5 detik (splash screen loading)
2. Cek console untuk error messages
3. Kill process dan restart:
   ```bash
   Ctrl+C  # di terminal
   python main.py
   ```

---

## 📁 Struktur File Penting

```
barubaru/
├── main.py                      # Entry point aplikasi
├── auth_ui_cyberpunk.py         # Login & Register UI
├── app_db_fixed.py              # Database connection & auth
├── dashboard_ui.py              # Main dashboard
├── user_dashboard.py            # User dashboard
├── admin_dashboard.py           # Admin dashboard
├── modern_notification.py       # Notification system
├── requirements.txt             # Dependencies
└── RUN_GUIDE.md                # Ini file!
```

---

## 🔧 Advanced Options

### Menjalankan di Background (Linux/Mac)

```bash
nohup python main.py &
```

### Menjalankan dengan Custom Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Debug Mode

```bash
python -c "import sys; sys.path.insert(0, '.'); from main import *; main()"
```

---

## 📝 Logs & Output

Aplikasi akan print output seperti:

```
✅ Connected to Railway PostgreSQL
✅ Database connection successful!
📊 Total users in database: 5
🔐 Active sessions: 2
```

**Jika ada error, cek:**
- Console output untuk error message
- File `.log` (jika ada)
- Database connection di `app_db_fixed.py`

---

## 🎯 Fitur Aplikasi

Setelah berhasil login, Anda bisa:

✅ **User Dashboard:**
- View profile
- Browse content
- Manage settings

✅ **Penerbit Dashboard:**
- Upload content
- Manage publications
- View analytics

✅ **Admin Dashboard:**
- Manage users
- Monitor system
- Admin controls

---

## 💡 Tips

1. **Internet Connection**: Pastikan connection stabil (database remote)
2. **Screen Resolution**: Optimal di layar dengan minimal 1024x768
3. **Performance**: Jika loading lambat, cek internet speed
4. **Database**: Backup database secara berkala

---

## 📞 Support

Jika ada masalah:

1. Check error messages di console
2. Lihat troubleshooting section di atas
3. Verify file structure
4. Test database connection dengan `python app_db_fixed.py`

---

**Status**: ✅ Ready to Run!

Happy Coding! 🚀
