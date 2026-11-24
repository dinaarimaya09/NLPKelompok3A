# Patch P11 — Baseline Ekstraktif TF-IDF

## Isi
- `notebooks/P11_baseline_ekstraktif.ipynb`: notebook eksperimen Colab.
- `src/baseline_extractive.py`: modul implementasi TF-IDF.
- `docs/P11_petunjuk.md`: petunjuk pemasangan dan penggunaan.

## Cara memasukkan ke repository
Salin folder `notebooks/`, `src/`, dan `docs/` dari patch ini ke repository `NLPKelompok3A-main` di Google Drive/GitHub. Pertahankan file lain yang sudah ada.

## Prasyarat
1. P08 menghasilkan `*_extracted_pages.json`.
2. P09 memproses file tersebut dan menghasilkan `*_token_chunks.json`.
3. File JSON P09 diunggah saat menjalankan P11.
4. Modul `src/baseline_extractive.py` harus sudah berada di repository Drive pada lokasi yang ditetapkan notebook.

## Catatan
Notebook menggunakan tiga batas kata awal (80, 150, 250) sebagai konfigurasi eksperimen. Angka tersebut dapat disesuaikan setelah melihat distribusi panjang ringkasan, tetapi perubahan parameter harus dilakukan pada data development, bukan berdasarkan hasil test.
