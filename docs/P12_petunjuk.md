# P12 — Baseline Abstraktif T5

## Tujuan
Membangun baseline abstraktif untuk dibandingkan dengan baseline ekstraktif TF-IDF pada P11.

## Model
`cahya/t5-base-indonesian-summarization-cased`

Model merupakan T5-base untuk summarization Bahasa Indonesia dan model card menyebutkan fine-tuning menggunakan dataset `id_liputan6`. Domain sumber model adalah berita, bukan khusus materi UTBK; hasil pada materi pembelajaran harus diperiksa secara manual dan dievaluasi.

## Input dan output
- Input: satu file `*_token_chunks.json` dari P09.
- Output: `outputs/baseline_summaries_p12/<nama_materi>_p12_abstraktif.json`.
- Tingkat ringkasan: pendek (target 80 kata), sedang (150 kata), panjang (250 kata).
- Target kata bukan batas mutlak; jumlah kata aktual dicatat pada output.

## Cara menjalankan
1. Salin `P12_baseline_abstraktif_T5.ipynb` ke folder `notebooks/` repository.
2. Buka notebook di Google Colab.
3. Jalankan cell berurutan.
4. Unggah satu JSON hasil P09 ketika diminta.
5. Tunggu model diunduh dan proses selesai.
6. Periksa hasil ringkasan dan file JSON di folder output.

## Komputasi
T5-base memiliki ukuran relatif besar. GPU Colab disarankan; CPU dapat berjalan tetapi lebih lambat. Notebook memproses satu dokumen per eksekusi dan menggunakan batch satu per inferensi.

## Batasan metodologis
- P12 adalah baseline inferensi, bukan fine-tuning model pada dataset proyek.
- Model card menyebutkan dataset fine-tuning `id_liputan6`; domain ini berbeda dari materi UTBK.
- Ringkasan generatif dapat menghilangkan atau menambahkan informasi. Audit fakta tetap diperlukan.
- `source_context` mencatat chunk dan halaman yang menjadi konteks, bukan alignment bukti per kalimat ringkasan.
- Gunakan split development untuk debugging dan tuning. Jangan menggunakan split test untuk memilih konfigurasi.
