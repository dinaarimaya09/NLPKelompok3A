import json, re
def parse_json(txt):
    txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
    try: return json.loads(txt)
    except Exception:
        m = re.search(r"\{.*\}", txt, re.S)
        if m: return json.loads(m.group(0))
        raise
def validate_question(q, valid_ids):
    e = []
    for f in ["teks_soal","kunci_jawaban","hint","pembahasan","topik","tingkat_kesulitan"]:
        if not str(q.get(f, "")).strip(): e.append(f"{f} kosong")
    o = q.get("opsi", {})
    if sorted(o.keys()) != list("ABCDE") or any(not str(v).strip() for v in o.values()): e.append("Opsi harus A-E dan tidak kosong")
    elif len(set(map(str, o.values()))) < 5: e.append("Opsi duplikat")
    if q.get("kunci_jawaban") not in list("ABCDE"): e.append("Kunci tidak valid")
    ev = q.get("evidence", [])
    if not ev: e.append("Evidence kosong")
    for x in ev:
        if x.get("materi_id") not in valid_ids: e.append(f"Evidence ID tidak valid: {x.get('materi_id')}")
    return e
