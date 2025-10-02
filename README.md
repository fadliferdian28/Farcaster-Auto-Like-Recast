# multi_account_bot

Sebuah skrip Python sederhana untuk melakukan **like** dan **recast** (repost) secara bergantian menggunakan beberapa akun (multi-account) pada platform yang memakai *Bearer tokens* (contoh: Farcaster).
Skrip ini dibuat untuk tujuan **otomasi pribadi / eksperimen** — **jangan** gunakan untuk menyalahgunakan akun orang lain atau melanggar kebijakan layanan.

---

## Struktur repository

```
multi_account_bot/
├── multi_account_bot.py     # skrip utama (Python)
├── hashes.txt               # daftar cast hashes (satu per baris)
├── tokens.example.txt       # contoh format token (DUMMY) — commit file ini
└── README.md                # (file ini)
```

> **PENTING:** Jangan pernah commit `tokens.txt` (file asli yang berisi token nyata). Gunakan `tokens.example.txt` sebagai panduan.

---

## tokens.example.txt (contoh)

Buat file `tokens.example.txt` agar kontributor tahu formatnya. Contoh isi:

```
# Format: satu token per baris
# Gunakan format "Bearer <TOKEN>" atau cukup "<TOKEN>" (skrip otomatis menambahkan "Bearer ")
Bearer YOUR_TOKEN_1_EXAMPLE
Bearer YOUR_TOKEN_2_EXAMPLE
```

Instruksi penggunaan:

1. Salin `tokens.example.txt` menjadi `tokens.txt`:

   ```bash
   cp tokens.example.txt tokens.txt
   ```
2. Isi `tokens.txt` dengan token asli (satu per baris).
3. Pastikan **tidak** meng-commit `tokens.txt` ke GitHub.

---

## Cara menjalankan (quickstart)

1. Pastikan Python 3.8+ terpasang.
2. (Opsional) Buat virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux / macOS
   venv\Scripts\activate       # Windows
   pip install -r requirements.txt   # jika ada requirements
   ```
3. Siapkan `tokens.txt` dan `hashes.txt`.
4. Jalankan:

   ```bash
   python multi_account_bot.py
   ```

Skrip akan membuat `results.csv` berisi ringkasan hasil (status HTTP untuk like & recast per token-per-hash).

---

## Konfigurasi (di dalam file skrip)

Beberapa variabel yang bisa kamu ubah di bagian atas `multi_account_bot.py`:

* `TOKENS_FILE` — nama file token (default `tokens.txt`)
* `HASHES_FILE` — nama file hash cast (default `hashes.txt`)
* `OUTPUT_CSV` — nama file hasil log (default `results.csv`)
* `DELAY_MIN`, `DELAY_MAX` — jeda acak antar request (dalam detik)
* `MAX_RETRIES`, `BACKOFF_BASE` — pengaturan retry & exponential backoff

Jangan set jeda terlalu kecil kalau target API punya rate-limit — biarkan jeda acak untuk mengurangi kemungkinan diblokir.

---

## Keamanan & privasi

* **Tokens = kredensial**: Perlakukan `tokens.txt` seperti password.
* Simpan `tokens.txt` hanya di mesin lokal yang aman dan berikan permission terbatas:

  ```bash
  chmod 600 tokens.txt
  ```
* Jika token pernah ter-publish / ter-push, anggap token tersebut **bocor**. Revoke / rotate token segera melalui dashboard layanan.
* Jangan pakai token orang lain tanpa izin.

---

## Etika & Kepatuhan

* Gunakan skrip ini hanya untuk akun yang **kamu miliki** atau akun yang secara eksplisit memberikan izin.
* Hormati Terms of Service dari platform target (mis. Farcaster). Otomasi yang melanggar peraturan dapat menyebabkan suspend/banned akun.

---

## Troubleshooting

* **401 Unauthorized** → token salah atau kadaluarsa. Periksa `tokens.txt`.
* **429 Too Many Requests** → kena rate-limit. Tingkatkan `DELAY_MIN/DELAY_MAX` atau tunggu beberapa saat.
* **No response / network errors** → cek koneksi Internet; skrip sudah memakai retry + backoff.

---

## Contoh penggunaan advanced

* Jalankan di background (Linux):

  ```bash
  nohup python multi_account_bot.py &> bot.log &
  ```
* Integrasi CI: Jika ingin menjalankan otomatis di CI/GitHub Actions, gunakan **secrets** untuk menyimpan token (JANGAN commit `tokens.txt`).

---

## Contribution

* Fork repo ini, buat perubahan pada branch baru, lalu submit Pull Request.
* Jika berkontribusi: sertakan `tokens.example.txt` (dummy) dan jangan sertakan file berisi secrets.

---
