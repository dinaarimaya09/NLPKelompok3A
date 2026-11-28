# UTBK Literasi Bahasa Indonesia Question Generator
Jalankan: `python3 -m pip install -r requirements.txt && python3 -m streamlit run app.py`
API key: salin `.env.example` ke `.env` (OPENAI_API_KEY / GEMINI_API_KEY). Tanpa key, aplikasi berjalan di **mode demo**.
Data di `data/` adalah DATA DEMO, bukan dataset resmi UTBK. Pada run pertama, data demo otomatis dimuat ke database.
Materi = sumber evidence; soal referensi = gaya; mapping = penghubung. Ekspor soal mengikuti 22 kolom.
