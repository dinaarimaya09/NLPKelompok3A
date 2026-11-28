import json, pandas as pd
from config import *
def _r(rows, kode, kol, msg, lvl="Error"): rows.append({"Kode/ID": kode, "Kolom": kol, "Masalah": msg, "Status": lvl})
def summary(df, issues):
    err = {i["Kode/ID"] for i in issues if i["Status"] == "Error"}
    n = len(df); bad = len(err); pct = round(100 * (n - bad) / n, 1) if n else 0
    status = "Valid" if not err else ("Perlu Perbaikan" if pct >= 50 else "Tidak Valid")
    return {"total": n, "valid": n - bad, "tidak_valid": bad, "error": sum(i["Status"]=="Error" for i in issues),
            "warning": sum(i["Status"]=="Warning" for i in issues), "persen": pct, "status": status}
def validate_materials(df):
    rows = []
    miss = [c for c in M_COLS if c not in df.columns]
    if miss: _r(rows, "-", ",".join(miss), "Kolom wajib tidak ada"); return summary(df, rows), pd.DataFrame(rows)
    for i, r in df.iterrows():
        k = r["materi_id"]
        if not str(k).strip(): _r(rows, f"baris {i+2}", "materi_id", "Kosong")
        if not str(r["isi_materi"]).strip() or str(r["isi_materi"])=="nan": _r(rows, k, "isi_materi", "Kosong")
        if r["topik"] not in TOPICS: _r(rows, k, "topik", f"Topik tidak terdaftar: {r['topik']}")
        if not str(r["kata_kunci"]).strip() or str(r["kata_kunci"])=="nan": _r(rows, k, "kata_kunci", "Kosong", "Warning")
    for k in df[df.materi_id.duplicated(keep=False)].materi_id.unique(): _r(rows, k, "materi_id", "Duplikat")
    for k in df[df.isi_materi.duplicated(keep=False)].materi_id: _r(rows, k, "isi_materi", "Isi materi duplikat", "Warning")
    return summary(df, rows), pd.DataFrame(rows)
def validate_questions(df):
    rows = []
    miss = [c for c in Q_COLS if c not in df.columns]
    if miss: _r(rows, "-", ",".join(miss), "Kolom wajib (22 kolom) tidak lengkap"); return summary(df, rows), pd.DataFrame(rows)
    for k in df[df["Kode Soal"].duplicated(keep=False)]["Kode Soal"].unique(): _r(rows, k, "Kode Soal", "Duplikat")
    for _, r in df.fillna("").iterrows():
        k = r["Kode Soal"] or "(kosong)"
        if not r["Kode Soal"]: _r(rows, k, "Kode Soal", "Kosong")
        if r["Nama Subtes"] != SUBTES: _r(rows, k, "Nama Subtes", f"Harus '{SUBTES}'")
        if r["Topik"] not in TOPICS: _r(rows, k, "Topik", "Topik tidak terdaftar")
        if r["Tipe Soal"] not in ["Pilihan Ganda","PG Kompleks","Isian Singkat"]: _r(rows, k, "Tipe Soal", "Tidak valid")
        if len(str(r["Teks Soal"]).strip()) < 10: _r(rows, k, "Teks Soal", "Kosong/placeholder")
        if r["Tipe Soal"] == "Pilihan Ganda":
            opts = [str(r[f"Opsi {x} - Teks"]).strip() for x in "ABCDE"]
            for x, o in zip("ABCDE", opts):
                if not o: _r(rows, k, f"Opsi {x}", "Kosong")
            ne = [o for o in opts if o]
            if len(set(ne)) < len(ne): _r(rows, k, "Opsi", "Ada opsi duplikat")
            key = r["Kunci Jawaban"]
            if key not in list("ABCDE"): _r(rows, k, "Kunci Jawaban", "Nilai harus A-E kapital")
            elif not opts["ABCDE".index(key)]: _r(rows, k, "Kunci Jawaban", "Menunjuk opsi kosong")
            elif r["Hint"] and opts["ABCDE".index(key)].lower() in str(r["Hint"]).lower(): _r(rows, k, "Hint", "Terlalu mengarah ke jawaban", "Warning")
        if not str(r["Pembahasan"]).strip(): _r(rows, k, "Pembahasan", "Kosong")
        if r["Tingkat Kesulitan"] not in DIFFICULTY: _r(rows, k, "Tingkat Kesulitan", "Tidak valid")
        kt = str(r["Kolom Tabel"]).strip()
        if kt.startswith(("{", "[")):
            try: json.loads(kt)
            except Exception: _r(rows, k, "Kolom Tabel", "JSON tidak terbaca")
        for g in ["Gambar Soal"] + [f"Opsi {x} - Gambar" for x in "ABCDE"]:
            if r[g] and not str(r[g]).lower().endswith((".png",".jpg",".jpeg")): _r(rows, k, g, "Format gambar harus PNG/JPG/JPEG")
    return summary(df, rows), pd.DataFrame(rows)
def validate_mapping(df, mats, qs):
    rows = []
    miss = [c for c in MAP_COLS if c not in df.columns]
    if miss: _r(rows, "-", ",".join(miss), "Kolom wajib tidak ada"); return summary(df, rows), pd.DataFrame(rows)
    for i, r in df.iterrows():
        k = f"{r['kode_soal']}→{r['materi_id']}"
        if r["kode_soal"] not in set(qs): _r(rows, k, "kode_soal", "Tidak ada di dataset soal")
        if r["materi_id"] not in set(mats): _r(rows, k, "materi_id", "Tidak ada di dataset materi")
        if r["topik"] not in CATEGORIES: _r(rows, k, "topik", "Harus salah satu kategori literasi resmi (bukan subtopik soal)")
    for _, r in df[df.duplicated(["kode_soal","materi_id"], keep=False)].iterrows(): _r(rows, f"{r.kode_soal}→{r.materi_id}", "pasangan", "Duplikat")
    return summary(df, rows), pd.DataFrame(rows)
