import json, random, uuid
from config import *
from modules import llm_provider as llm
from modules.question_validator import parse_json, validate_question
from modules.evidence_extraction import split_sentences, best_sentence
SYSTEM = """You are an expert Indonesian UTBK Literacy question writer.
Generate high-quality Indonesian reading literacy multiple-choice questions using ONLY the provided evidence as factual support.
The reference questions are provided only to guide style, structure, and difficulty. Never copy reference questions.
Rules: align with the requested topic and competency; natural Indonesian; exactly five options A-E; exactly one correct answer; plausible distractors; a hint that does not reveal the answer; a detailed explanation of why the answer is supported by evidence and why distractors are wrong; include exact evidence excerpts with their material IDs; never invent facts; do not fabricate evidence IDs; avoid ambiguity and duplicates; match difficulty; original questions only. If evidence is insufficient return {"generation_status":"insufficient_evidence","questions":[]}.
Return valid JSON only, format: {"generation_status":"success","questions":[{"kode_soal":"GEN-001","nama_subtes":"Literasi Bahasa Indonesia","topik":"","tipe_soal":"Pilihan Ganda","teks_soal":"","opsi":{"A":"","B":"","C":"","D":"","E":""},"kunci_jawaban":"","hint":"","pembahasan":"","tingkat_kesulitan":"","evidence":[{"materi_id":"","kutipan":""}]}]}"""
def demo_questions(ev, n, topik, diff, kompetensi):
    """Mode demo tanpa API: soal dibuat dari kalimat evidence (BUKAN hasil LLM)."""
    qs = []
    pool = [(r.materi_id, s) for r in ev.itertuples() for s in split_sentences(r.isi_materi)]
    for i in range(n):
        r = ev.iloc[i % len(ev)]; ss = split_sentences(r.isi_materi); ans = ss[i // len(ev) % len(ss)]
        dis = [s for m, s in pool if m != r.materi_id and s != ans]
        random.shuffle(dis); dis = (dis + ["Penulis tidak memberikan informasi apa pun tentang hal ini.", "Pernyataan tersebut bertentangan dengan isi bacaan.", "Hal itu hanya berlaku pada kasus tertentu saja.", "Bacaan menyatakan sebaliknya."])[:4]
        opts = dis + [ans]; random.shuffle(opts); key_ = "ABCDE"[opts.index(ans)]
        qs.append({"kode_soal": f"GEN-{i+1:03d}", "nama_subtes": SUBTES, "topik": topik, "tipe_soal": "Pilihan Ganda",
          "teks_soal": f"Perhatikan bacaan berikut!\n\n\"{r.isi_materi}\"\n\nPernyataan yang paling sesuai dengan isi bacaan ({topik.lower()}) adalah ....",
          "opsi": dict(zip("ABCDE", opts)), "kunci_jawaban": key_, "hint": f"Cocokkan setiap opsi dengan isi bacaan tentang \"{r.judul_materi}\".",
          "pembahasan": f"[MODE DEMO] Jawaban {key_} sesuai dengan kalimat pada materi {r.materi_id}. Opsi lain tidak didukung oleh bacaan.",
          "tingkat_kesulitan": diff, "evidence": [{"materi_id": r.materi_id, "kutipan": ans}]})
    return qs
def generate(ev, refs, n, topik, kategori, diff, kompetensi, provider, model, use_demo, retries=2):
    """Return (status, questions, message, mode)."""
    if ev.empty or ev.skor.max() < MIN_SCORE: return "insufficient_evidence", [], "Evidence tidak cukup relevan. Pilih materi/topik lain.", "-"
    ids = set(ev.materi_id)
    if use_demo or not llm.available(provider):
        return "success", demo_questions(ev, n, topik, diff, kompetensi), "Mode demo (tanpa LLM).", "demo"
    evtxt = "\n".join(f"[{r.materi_id}] {r.judul_materi}: {r.isi_materi}" for r in ev.itertuples())
    reftxt = "\n".join(f"- {r['Teks Soal'][:300]}" for _, r in refs.head(2).iterrows()) if refs is not None and len(refs) else "(tanpa contoh)"
    user = f"Topik: {topik}\nKategori literasi: {kategori}\nKompetensi: {kompetensi}\nTingkat: {diff}\nJumlah soal: {n}\n\nEVIDENCE:\n{evtxt}\n\nREFERENCE STYLE (jangan disalin):\n{reftxt}"
    err = ""
    for _ in range(retries + 1):
        try:
            data = parse_json(llm.call_llm(provider, model, SYSTEM, user + (f"\nPerbaiki kesalahan sebelumnya: {err}" if err else "")))
            if data.get("generation_status") == "insufficient_evidence": return "insufficient_evidence", [], "LLM menyatakan evidence tidak cukup.", "llm"
            qs = data.get("questions", [])
            probs = [p for q in qs for p in validate_question(q, ids)]
            if len(qs) != n: probs.append(f"Jumlah soal {len(qs)} != {n}")
            if not probs: return "success", qs, "OK", "llm"
            err = "; ".join(probs[:5])
        except Exception as ex: err = str(ex)[:200]
    return "failed", [], f"Gagal menghasilkan soal valid: {err}", "llm"
def to_22(q):
    r = {c: "" for c in Q_COLS}
    r.update({"Kode Soal": q["kode_soal"], "Nama Subtes": q["nama_subtes"], "Topik": q["topik"], "Tipe Soal": q["tipe_soal"], "Teks Soal": q["teks_soal"],
              "Kunci Jawaban": q["kunci_jawaban"], "Hint": q["hint"], "Pembahasan": q["pembahasan"], "Tingkat Kesulitan": q["tingkat_kesulitan"]})
    for x in "ABCDE": r[f"Opsi {x} - Teks"] = q["opsi"][x]
    return r

def generate_soal(topik, n=3, tingkat="Sedang", metode="TF-IDF", top_k=3, provider="OpenAI", model=None, kategori=None, mats=None, refs=None, demo=None):
    """Fungsi utama generate soal: retrieval evidence -> LLM -> validasi. Return dict {status, message, mode, evidence, questions}.
    demo=None: otomatis mode demo bila API key tidak ada."""
    from modules import database as db, evidence_extraction as ee
    mats = db.read("materials") if mats is None else mats
    kategori = kategori or TOPIC_CATEGORY[topik][0]
    ev = ee.retrieve(mats, f"{topik} {kategori}", topik, metode, top_k)
    model = model or ("gpt-4o-mini" if provider == "OpenAI" else "gemini-1.5-flash")
    st, qs, msg, mode = generate(ev, refs, n, topik, kategori, tingkat, f"{kategori} - {topik}", provider, model, bool(demo) if demo is not None else not llm.available(provider))
    return {"status": st, "message": msg, "mode": mode, "evidence": ev[["evidence_id", "judul_materi", "skor", "metode"]].to_dict("records") if len(ev) else [], "questions": qs}
