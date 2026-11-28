import re
from config import TOPICS, DIFFICULTY
W = {"Evidence Relevance": .30, "Answer Consistency": .25, "Question Clarity": .15, "Option Quality": .15, "Topic Alignment": .10, "Difficulty Alignment": .05}
def _n(t): return re.sub(r"\s+", " ", str(t).lower()).strip()
def evaluate(q, mats, ref_texts=()):
    notes, A = [], {}
    m = mats.set_index("materi_id").isin_text if False else dict(zip(mats.materi_id, mats.isi_materi)); tp = dict(zip(mats.materi_id, mats.topik))
    ev = q.get("evidence", []); ok = [e for e in ev if e.get("materi_id") in m and _n(e.get("kutipan", "")) and _n(e["kutipan"]) in _n(m[e["materi_id"]])]
    A["Evidence Relevance"] = 100 * len(ok) / len(ev) if ev else 0
    if len(ok) < len(ev): notes.append("Ada kutipan evidence yang tidak ditemukan persis di materi.")
    o = q.get("opsi", {}); k = q.get("kunci_jawaban"); c = 0
    if k in o: c += 50
    if k in o and (f" {k}" in " " + q.get("pembahasan", "") or _n(o[k])[:25] in _n(q.get("pembahasan", ""))): c += 50
    else: notes.append("Pembahasan tidak menyebut kunci/opsi benar secara jelas.")
    A["Answer Consistency"] = c
    t = q.get("teks_soal", ""); cl = 100
    if len(t) < 25: cl -= 50; notes.append("Teks soal terlalu pendek.")
    if _n(t) in {_n(x) for x in ref_texts}: cl -= 60; notes.append("Soal identik dengan soal referensi.")
    if not re.search(r"(\?|\.{3,}|:)\s*$", t.strip()): cl -= 25; notes.append("Soal tidak diakhiri tanda tanya/titik-titik.")
    A["Question Clarity"] = max(cl, 0)
    vals = [_n(v) for v in o.values()]; oq = 100
    if len(o) != 5 or any(not v for v in vals): oq = 0; notes.append("Opsi tidak lengkap.")
    elif len(set(vals)) < 5: oq -= 60; notes.append("Ada opsi duplikat.")
    elif max(map(len, vals)) > 4 * max(min(map(len, vals)), 1): oq -= 25; notes.append("Panjang opsi sangat timpang (petunjuk tersembunyi).")
    A["Option Quality"] = max(oq, 0)
    ta = 0 if q.get("topik") not in TOPICS else 50
    if ok and all(tp.get(e["materi_id"]) == q.get("topik") for e in ok): ta += 50
    else: notes.append("Topik evidence berbeda dari topik soal.")
    A["Topic Alignment"] = ta
    A["Difficulty Alignment"] = 100 if q.get("tingkat_kesulitan") in DIFFICULTY else 0
    overall = round(sum(A[a] * w for a, w in W.items()), 1)
    return {"overall": overall, "aspects": A, "notes": notes, "saran": "Lolos pemeriksaan otomatis; tetap verifikasi manual." if overall >= 80 else "Revisi sebelum dipakai."}
