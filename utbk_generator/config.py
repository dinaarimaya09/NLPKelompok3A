from pathlib import Path
BASE = Path(__file__).parent
DB_PATH = BASE / "database" / "app.db"
TOPICS = ["Ide Pokok", "Makna Kata", "Inferensi", "Tujuan Teks", "Fakta dan Opini"]
CATEGORIES = ["Menemukan Informasi", "Memahami Informasi", "Mengevaluasi dan Merefleksi Informasi"]
TOPIC_CATEGORY = {"Ide Pokok": ["Memahami Informasi"], "Makna Kata": ["Memahami Informasi"],
    "Inferensi": ["Memahami Informasi", "Menemukan Informasi"], "Tujuan Teks": ["Mengevaluasi dan Merefleksi Informasi"],
    "Fakta dan Opini": ["Mengevaluasi dan Merefleksi Informasi", "Menemukan Informasi"]}
DIFFICULTY = ["Mudah", "Sedang", "Sulit"]
Q_COLS = ["Kode Soal","Nama Subtes","Topik","Tipe Soal","Teks Soal","Gambar Soal",
 "Opsi A - Teks","Opsi A - Gambar","Opsi B - Teks","Opsi B - Gambar","Opsi C - Teks","Opsi C - Gambar",
 "Opsi D - Teks","Opsi D - Gambar","Opsi E - Teks","Opsi E - Gambar","Kolom Tabel","Kunci Jawaban",
 "Hint","Pembahasan","Gambar Pembahasan","Tingkat Kesulitan"]
M_COLS = ["materi_id","topik","subtopik","judul_materi","isi_materi","kata_kunci","sumber"]
MAP_COLS = ["kode_soal","materi_id","topik"]
SUBTES = "Literasi Bahasa Indonesia"
MIN_SCORE = 0.05
