# P10 — Pembagian Data Development dan Test

## Tujuan
Menetapkan 10 dokumen untuk development dan 10 dokumen untuk test. Split dibuat tetap sebelum eksperimen P11–P21. Data development boleh dipakai untuk memperbaiki prompt, parameter, dan kode. Data test hanya digunakan setelah metode/configuration dibekukan.

## Pembagian sementara

| Split | Materi | Jumlah |
|---|---|---:|
| development | M001–M010 | 10 |
| test | M011–M020 | 10 |

Semua tujuh bab dari satu buku, M013–M019, ditempatkan pada split test yang sama agar bab dari sumber yang sama tidak tersebar ke development dan test. Materi M001–M004 yang tercatat berasal dari tautan Scribd yang sama ditempatkan bersama pada development.

Materi M006–M012 berasal dari penerbit/penyedia yang sama (Ruangguru), tetapi merupakan dokumen dengan topik berbeda menurut metadata. Pembagian sementara memisahkan M006–M010 ke development dan M011–M012 ke test. Sebelum split dibekukan, periksa isi PDF untuk memastikan tidak ada halaman, soal, atau bagian teks yang tumpang tindih. Jika ada tumpang tindih, pindahkan seluruh materi yang saling tumpang tindih ke split yang sama lalu evaluasi kembali komposisi 10/10.

## Batas unit dan halaman
Unit yang direncanakan adalah satu PDF utuh per materi. Rentang halaman awal diisi dari jumlah halaman pada metadata; untuk PDF yang tersedia, jumlah halaman diverifikasi langsung dari file. Untuk PDF yang belum ada, rentang masih sementara dan wajib diperiksa setelah file diterima. Jika evaluasi nanti hanya memakai sebagian halaman, rentang tersebut harus ditetapkan dan dibekukan sebelum melihat hasil model.

## Audit file yang ditemukan di ZIP repository

Dari 20 baris pada `data/materi_index.csv`, hanya 5 PDF yang ditemukan pada ZIP repository yang diperiksa: M001, M002, M003, M004, dan M013. Lima PDF ini memiliki jumlah halaman aktual yang cocok dengan metadata (2, 4, 2, 3, dan 72). Lima belas PDF lainnya belum ada di ZIP, sehingga status ketersediaan dan jumlah halamannya belum dapat diverifikasi.

**Artinya: pembagian 10/10 ini adalah rancangan split berdasarkan 20 entri metadata, belum boleh disebut final/terverifikasi penuh.** Lengkapi 15 PDF yang belum tersedia, cocokkan nama file, jumlah halaman, topik, dan potensi duplikasi sebelum menetapkan split final. Jangan mengarang status kelayakan dokumen.

## Aturan penggunaan
1. Development: boleh dipakai untuk debugging, tuning prompt, parameter, dan perbaikan kode.
2. Test: jangan dipakai untuk memilih prompt, mengubah parameter, atau memperbaiki kode.
3. Jika ada perubahan split, catat alasan dan tanggal perubahan sebelum eksperimen. Jangan mengubah split karena hasil test terlihat buruk.
4. Simpan salinan final `materi_index.csv` pada commit Git yang digunakan untuk eksperimen.
5. Laporkan keterbatasan distribusi topik/panjang dokumen. Jumlah dokumen 10/10 tidak otomatis berarti jumlah halaman atau kompleksitasnya seimbang.

## Kriteria selesai P10
- [ ] Semua 20 PDF tersedia dan nama file cocok dengan metadata.
- [ ] Jumlah halaman aktual diperiksa.
- [ ] Topik dan panjang dokumen diperiksa untuk variasi.
- [ ] Duplikasi/tumpang tindih antardokumen diperiksa, terutama materi dengan sumber yang sama.
- [ ] Split 10 development dan 10 test dikunci.
- [ ] Rentang halaman/unit evaluasi ditetapkan dan tidak berubah setelah hasil diketahui.
