import sqlite3, pandas as pd
from config import DB_PATH
DDL = """
CREATE TABLE IF NOT EXISTS materials(materi_id TEXT PRIMARY KEY, topik TEXT, subtopik TEXT, judul_materi TEXT, isi_materi TEXT NOT NULL, kata_kunci TEXT, sumber TEXT);
CREATE TABLE IF NOT EXISTS reference_questions(kode_soal TEXT PRIMARY KEY, data_json TEXT);
CREATE TABLE IF NOT EXISTS question_material_mapping(kode_soal TEXT, materi_id TEXT, topik TEXT, UNIQUE(kode_soal,materi_id));
CREATE TABLE IF NOT EXISTS generated_questions(id INTEGER PRIMARY KEY AUTOINCREMENT, generation_id TEXT, kode_soal TEXT, data_json TEXT,
  retrieval_method TEXT, reference_question_ids TEXT, validation_status TEXT DEFAULT 'Belum Diverifikasi', evaluation_score REAL, mode TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS generated_question_evidence(id INTEGER PRIMARY KEY AUTOINCREMENT, question_id INTEGER REFERENCES generated_questions(id) ON DELETE CASCADE,
  evidence_id TEXT, evidence_text TEXT, evidence_score REAL);
CREATE TABLE IF NOT EXISTS generation_history(generation_id TEXT PRIMARY KEY, params_json TEXT, status TEXT, message TEXT, n_questions INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS evaluation_results(id INTEGER PRIMARY KEY AUTOINCREMENT, question_id INTEGER, overall REAL, detail_json TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS practice_sessions(id INTEGER PRIMARY KEY AUTOINCREMENT, topik TEXT, score REAL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS practice_answers(id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, question_id INTEGER, answer TEXT, correct INTEGER);
CREATE INDEX IF NOT EXISTS idx_mat_topik ON materials(topik);
CREATE INDEX IF NOT EXISTS idx_map_kode ON question_material_mapping(kode_soal);
"""
def conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    c = sqlite3.connect(DB_PATH); c.execute("PRAGMA foreign_keys=ON"); return c
def init_db():
    with conn() as c: c.executescript(DDL)
def read(table):
    with conn() as c: return pd.read_sql(f"SELECT * FROM {table}", c)
def execute(sql, args=()):
    with conn() as c: return c.execute(sql, args).lastrowid
def save_materials(df):
    with conn() as c:
        c.execute("DELETE FROM materials")
        df[["materi_id","topik","subtopik","judul_materi","isi_materi","kata_kunci","sumber"]].astype(str).to_sql("materials", c, if_exists="append", index=False)
def save_refs(df):
    import json
    with conn() as c:
        c.execute("DELETE FROM reference_questions")
        c.executemany("INSERT INTO reference_questions VALUES(?,?)", [(r["Kode Soal"], json.dumps(r, ensure_ascii=False)) for r in df.fillna("").to_dict("records")])
def load_refs():
    import json
    d = read("reference_questions")
    return pd.DataFrame([json.loads(x) for x in d.data_json]) if len(d) else pd.DataFrame()
def save_mapping(df):
    with conn() as c:
        c.execute("DELETE FROM question_material_mapping")
        df[["kode_soal","materi_id","topik"]].drop_duplicates(["kode_soal","materi_id"]).to_sql("question_material_mapping", c, if_exists="append", index=False)
