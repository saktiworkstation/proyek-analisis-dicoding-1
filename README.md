# Proyek Analisis Data: E-Commerce Public Dataset

## Latar Belakang

Proyek ini bertujuan untuk melakukan analisis mendalam terhadap E-Commerce Public Dataset yang tersedia di Kaggle. Analisis ini mencakup eksplorasi data untuk menemukan wawasan bisnis, seperti kategori produk terlaris, demografi pelanggan, metode pembayaran yang paling sering digunakan, dan segmentasi pelanggan menggunakan RFM Analysis untuk mengidentifikasi perilaku pembelian pelanggan.

## Pertanyaan Bisnis (Business Questions)

1.  **Apa saja 10 kategori produk yang paling banyak dan paling sedikit diminati oleh pelanggan?**
    -   *Tujuan*: Mengidentifikasi kategori produk unggulan dan yang kurang performa untuk membantu dalam strategi manajemen inventaris dan pemasaran.
2.  **Bagaimana demografi pelanggan (berdasarkan negara bagian/state) dan metode pembayaran apa yang paling sering mereka gunakan?**
    -   *Tujuan*: Memahami basis pelanggan utama dan preferensi pembayaran mereka untuk menyesuaikan strategi pemasaran regional dan mengoptimalkan sistem pembayaran.
3.  **(Analisis Lanjutan) Bagaimana cara mengelompokkan pelanggan ke dalam segmen-segmen yang berarti berdasarkan perilaku pembelian mereka (Recency, Frequency, Monetary)?**
    -   *Tujuan*: Membuat segmentasi pelanggan untuk kampanye pemasaran yang lebih personal dan efektif, serta meningkatkan retensi pelanggan.

## Struktur Proyek

submission/
├───dashboard/
│   └───dashboard.py         # File utama aplikasi Streamlit
├───data/
│   └─── (semua file .csv)   # Kumpulan dataset mentah
├───notebook.ipynb             # Notebook Jupyter berisi proses analisis data
├───README.md                  # Berkas ini (penjelasan proyek)
└───requirements.txt           # Daftar library Python yang dibutuhkan


## Setup Lingkungan

1.  **Clone Repositori (jika ada)**
    ```bash
    git clone [URL_REPOSITORY_ANDA]
    cd submission
    ```

2.  **Buat dan Aktifkan Virtual Environment**
    Disarankan untuk menggunakan *virtual environment* untuk menjaga dependensi proyek tetap terisolasi.
    ```bash
    # Membuat environment
    python -m venv venv

    # Mengaktifkan environment
    # Windows (PowerShell)
    venv\Scripts\activate

    # macOS/Linux
    source venv/bin/activate
    ```
    *Catatan: Jika Anda mengalami masalah saat aktivasi di PowerShell, jalankan `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` pada PowerShell (Admin).*

3.  **Instal Dependensi**
    Instal semua *library* yang diperlukan menggunakan file `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

## Cara Menjalankan Dasbor

Pastikan Anda berada di direktori utama (`submission/`) dan *virtual environment* sudah aktif. Jalankan perintah berikut di terminal:

```bash
streamlit run dashboard/dashboard.py
```

Biasanya akan langsung mengarah ke browser, jika tidak bisa cek url di terminal atau berikut (biasanya http://localhost:8501).

## Hasil Analisis

    - Dasbor interaktif akan menampilkan visualisasi dari hasil analisis, antara lain:

    - Key Metrics: Total pendapatan, jumlah pesanan, dan jumlah pelanggan unik.

    - Performa Produk: Grafik batang untuk 10 kategori produk terlaris dan 10 kategori kurang laris.

    - Demografi & Pembayaran: Grafik distribusi pelanggan berdasarkan negara bagian dan diagram pai untuk metode pembayaran.

    - Segmentasi Pelanggan (RFM): Grafik distribusi pelanggan berdasarkan segmen seperti "Champions", "Loyal Customers", "At Risk", dan "Hibernating".