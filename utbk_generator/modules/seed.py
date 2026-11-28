import pandas as pd
from config import *
T = {"Ide Pokok": [("Paragraf dan gagasan utama","Ide pokok adalah gagasan utama yang menjadi inti sebuah paragraf. Kalimat utama biasanya memuat ide pokok dan didukung oleh kalimat penjelas.","paragraf,gagasan utama"),
 ("Letak ide pokok","Ide pokok dapat terletak di awal, akhir, atau awal dan akhir paragraf. Paragraf deduktif menempatkan ide pokok di awal paragraf.","deduktif,induktif"),
 ("Kalimat penjelas","Kalimat penjelas berfungsi menguraikan, memberi contoh, atau memperkuat kalimat utama. Kalimat penjelas tidak berdiri sebagai gagasan utama.","penjelas,contoh")],
"Makna Kata": [("Makna denotasi dan konotasi","Makna denotasi adalah makna sebenarnya sesuai kamus. Makna konotasi adalah makna tambahan yang muncul dari nilai rasa atau asosiasi pembaca.","denotasi,konotasi"),
 ("Makna kata dalam konteks","Makna kata dalam teks ditentukan oleh konteks kalimat di sekitarnya. Satu kata dapat bermakna berbeda ketika berada pada konteks yang berbeda.","konteks,polisemi"),
 ("Sinonim dan antonim","Sinonim adalah kata yang bermakna sama atau mirip. Antonim adalah kata yang bermakna berlawanan.","sinonim,antonim")],
"Inferensi": [("Menarik simpulan","Inferensi adalah simpulan yang ditarik pembaca berdasarkan informasi tersurat dan pengetahuan pendukung. Simpulan yang baik harus tetap dapat ditelusuri ke isi teks.","simpulan,tersirat"),
 ("Informasi tersirat","Informasi tersirat tidak dinyatakan langsung oleh penulis. Pembaca menemukannya dengan menghubungkan petunjuk-petunjuk dalam teks.","tersirat,petunjuk"),
 ("Hubungan sebab akibat","Hubungan sebab akibat menjelaskan peristiwa yang terjadi dan penyebabnya. Pembaca dapat menyimpulkan akibat apabila penyebab dalam teks sudah jelas.","sebab,akibat")],
"Tujuan Teks": [("Teks persuasi","Teks persuasi bertujuan membujuk pembaca agar melakukan sesuatu atau menerima gagasan penulis. Teks persuasi sering memakai ajakan dan alasan yang meyakinkan.","persuasi,ajakan"),
 ("Teks eksposisi","Teks eksposisi bertujuan menjelaskan atau memberi informasi secara objektif. Penulis menyajikan fakta dan penjelasan tanpa memaksa pembaca.","eksposisi,informasi"),
 ("Teks narasi","Teks narasi bertujuan menceritakan rangkaian peristiwa. Teks narasi memiliki tokoh, latar, dan alur.","narasi,tokoh")],
"Fakta dan Opini": [("Ciri fakta","Fakta adalah pernyataan yang dapat dibuktikan kebenarannya melalui data atau pengamatan. Fakta bersifat objektif.","fakta,objektif"),
 ("Ciri opini","Opini adalah pendapat atau penilaian penulis yang bersifat subjektif. Opini sering ditandai kata seperti seharusnya, sebaiknya, dan menurut saya.","opini,subjektif"),
 ("Membedakan fakta dan opini","Untuk membedakan fakta dan opini, pembaca perlu memeriksa apakah pernyataan dapat diverifikasi. Pernyataan yang tidak dapat diverifikasi dan berisi penilaian termasuk opini.","verifikasi,penilaian")]}
def materials():
    rows, i = [], 1
    for t, items in T.items():
        for j, (jd, isi, kk) in enumerate(items):
            rows.append([f"MAT-{i:03d}", t, jd, jd, isi, kk, "DATA DEMO (bukan dataset resmi UTBK)"]); i += 1
    return pd.DataFrame(rows, columns=M_COLS)
def questions():
    spec = [("Ide Pokok","Ide pokok sebuah paragraf merupakan ....",["Kalimat penjelas","Gagasan utama","Kalimat penutup","Kata kunci","Pendapat penulis"],"B","Mudah"),
     ("Makna Kata","Makna denotasi adalah makna ....",["tambahan karena nilai rasa","yang berlawanan","sebenarnya sesuai kamus","yang berubah-ubah","kiasan"],"C","Mudah"),
     ("Inferensi","Simpulan yang baik dalam inferensi harus ....",["tidak terkait teks","berdasarkan perasaan pembaca","bertentangan dengan teks","dapat ditelusuri ke isi teks","menambah fakta baru"],"D","Sedang"),
     ("Tujuan Teks","Teks yang bertujuan membujuk pembaca disebut teks ....",["narasi","eksposisi","deskripsi","persuasi","laporan"],"D","Sedang"),
     ("Fakta dan Opini","Pernyataan yang dapat dibuktikan kebenarannya melalui data disebut ....",["opini","fakta","harapan","saran","kesan"],"B","Sedang")]
    rows = []
    for n, (t, q, o, k, d) in enumerate(spec, 1):
        r = {c: "" for c in Q_COLS}
        r.update({"Kode Soal": f"LBI-{n:03d}", "Nama Subtes": SUBTES, "Topik": t, "Tipe Soal": "Pilihan Ganda", "Teks Soal": q, "Kunci Jawaban": k,
          "Hint": "Ingat kembali definisi konsep pada materi.", "Pembahasan": f"Jawaban {k} benar sesuai definisi materi; opsi lain tidak sesuai definisi.", "Tingkat Kesulitan": d})
        for x, v in zip("ABCDE", o): r[f"Opsi {x} - Teks"] = v
        rows.append(r)
    return pd.DataFrame(rows, columns=Q_COLS)
def mapping():
    return pd.DataFrame([["LBI-001","MAT-001","Memahami Informasi"],["LBI-001","MAT-002","Memahami Informasi"],["LBI-002","MAT-004","Memahami Informasi"],
      ["LBI-003","MAT-007","Memahami Informasi"],["LBI-004","MAT-010","Mengevaluasi dan Merefleksi Informasi"],["LBI-005","MAT-013","Mengevaluasi dan Merefleksi Informasi"]], columns=MAP_COLS)
def write_all():
    materials().to_csv(BASE/"data/materials.csv", index=False); questions().to_csv(BASE/"data/reference_questions.csv", index=False); mapping().to_csv(BASE/"data/mapping_soal_materi.csv", index=False)
    materials().to_csv(BASE/"data/template_dataset_materi.csv", index=False); questions().to_csv(BASE/"data/template_dataset_soal.csv", index=False); mapping().to_csv(BASE/"data/template_mapping_soal_materi.csv", index=False)
