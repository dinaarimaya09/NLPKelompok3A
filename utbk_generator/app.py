import json, pandas as pd, streamlit as st, plotly.express as px
from dotenv import load_dotenv
load_dotenv()
from config import *
from modules import database as db, dataset_validator as dv, evidence_extraction as ee, question_generator as qg, llm_provider as llm, export as ex
from modules.seed import write_all
st.set_page_config(page_title="UTBK Literasi Generator", page_icon="📘", layout="wide")
db.init_db()
if not (BASE/"data/materials.csv").exists(): write_all()
if db.read("materials").empty and db.read("reference_questions").empty:  # seed data demo pada run pertama
    db.save_materials(pd.read_csv(BASE/"data/materials.csv", dtype=str).fillna("")); db.save_refs(pd.read_csv(BASE/"data/reference_questions.csv", dtype=str).fillna(""))
    db.save_mapping(pd.read_csv(BASE/"data/mapping_soal_materi.csv", dtype=str).fillna(""))
st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html,body,[class*="css"]{font-family:Inter,sans-serif;color:#1E293B}.stApp{background:#F5F7FB}
[data-testid=stSidebar]{background:#14213D}[data-testid=stSidebar] *{color:#fff!important}
.hero{background:linear-gradient(135deg,#14213D,#2563EB);color:#fff;padding:32px;border-radius:18px;margin-bottom:18px}
.hero h1{color:#fff;margin:0}.hero p{color:#E0F2FE}
div[data-testid=stMetric]{background:#fff;padding:14px;border-radius:14px;box-shadow:0 2px 10px rgba(20,33,61,.08)}
.badge{padding:2px 10px;border-radius:99px;font-size:12px;color:#fff}.card{background:#fff;padding:18px;border-radius:14px;box-shadow:0 2px 10px rgba(20,33,61,.08);margin-bottom:12px}
.block-container{padding-top:1.5rem;max-width:1250px}h1,h2,h3{color:#14213D;font-weight:800}
.stButton>button,.stDownloadButton>button{border-radius:10px;border:1px solid #2563EB;font-weight:600;transition:.15s}
.stButton>button:hover{background:#2563EB;color:#fff;transform:translateY(-1px);box-shadow:0 4px 12px rgba(37,99,235,.3)}
button[kind=primary]{background:linear-gradient(135deg,#2563EB,#38BDF8)!important;color:#fff!important;border:0!important}
div[data-testid=stMetric]{border-left:5px solid #38BDF8}div[data-testid=stMetricValue]{color:#2563EB;font-weight:800}
.stTabs [data-baseweb=tab]{font-weight:600}[data-testid=stExpander]{background:#fff;border-radius:12px;border:1px solid #E2E8F0}
.opt{background:#fff;border:1px solid #E2E8F0;border-radius:10px;padding:8px 14px;margin:4px 0}
</style>""", unsafe_allow_html=True)
px.defaults.template = "plotly_white"; px.defaults.color_discrete_sequence = ["#2563EB", "#38BDF8", "#14213D", "#60A5FA", "#93C5FD"]
st.markdown("""<style>
[data-testid=stSidebar]{background:linear-gradient(180deg,#0B1B3A,#14213D 60%,#1E3A8A)}
[data-testid=stSidebarNav] a{border-radius:12px;margin:2px 6px;padding:6px 10px}[data-testid=stSidebarNav] a:hover{background:rgba(56,189,248,.18)}
[data-testid=stSidebarNav] a[aria-current=page]{background:linear-gradient(135deg,#2563EB,#38BDF8);box-shadow:0 4px 14px rgba(37,99,235,.45)}
.hero{background:radial-gradient(circle at 85% 20%,#38BDF8 0,transparent 35%),linear-gradient(135deg,#0B1B3A,#2563EB);box-shadow:0 12px 30px rgba(37,99,235,.25)}
div[data-testid=stMetric]{border:1px solid #E0E7FF;border-radius:18px;padding:16px 18px}
div[data-testid=stMetricLabel]{color:#64748B;font-weight:600}
.card{border:1px solid #E0E7FF;border-radius:18px}
.opt{display:flex;align-items:center;gap:14px;background:#fff;border:1px solid #DBEAFE;border-radius:14px;padding:10px 16px;margin:8px 0;transition:.15s}
.opt:hover{border-color:#2563EB;background:#EFF6FF;transform:translateX(3px)}
.ltr{background:#2563EB;color:#fff;font-weight:800;border-radius:10px;min-width:34px;height:34px;display:flex;align-items:center;justify-content:center}
.qchip{display:inline-block;background:#DBEAFE;color:#1D4ED8;border-radius:99px;padding:3px 14px;font-size:12px;font-weight:700;margin-right:6px}
.flow{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.flow b{background:#fff;border:1px solid #BFDBFE;color:#1D4ED8;border-radius:12px;padding:8px 14px;font-size:13px}.flow span{color:#38BDF8;font-weight:800}
.stTabs [aria-selected=true]{color:#2563EB!important}
</style>""", unsafe_allow_html=True)
def badge(t, c): return f"<span class='badge' style='background:{c}'>{t}</span>"
def load_up(f):
    return pd.read_excel(f, dtype=str).fillna("") if f.name.endswith("xlsx") else pd.read_csv(f, dtype=str).fillna("")
def stat(m): return {"Valid": "#16A34A", "Perlu Perbaikan": "#F59E0B", "Tidak Valid": "#EF4444"}[m["status"]]
def go(p): st.switch_page(p)

def dashboard():
    mats, refs, mp, gq = db.read("materials"), db.load_refs(), db.read("question_material_mapping"), db.read("generated_questions")
    ev = db.read("generated_question_evidence")
    st.markdown("<div class='hero'><h1>UTBK Literacy Question Generator</h1><p><b>Platform AI untuk menghasilkan soal latihan UTBK Literasi Bahasa Indonesia berdasarkan evidence dari materi pembelajaran.</b><br>Temukan materi relevan, hasilkan soal berkualitas, dan verifikasi setiap pertanyaan melalui evidence yang transparan.</p></div>", unsafe_allow_html=True)
    b = st.columns(3)
    b[0].button("🚀 Mulai Generate Soal", on_click=go, args=(gen_p,), use_container_width=True)
    b[1].button("🗂️ Kelola Dataset", on_click=go, args=(data_p,), use_container_width=True)
    b[2].button("🔎 Lihat Evidence Explorer", on_click=go, args=(expl_p,), use_container_width=True)
    sc = gq.evaluation_score.dropna().mean() if len(gq) else None
    c = st.columns(6)
    for col, (l, v) in zip(c, [("Dataset Materi", len(mats)), ("Soal Referensi", len(refs)), ("Mapping", len(mp)), ("Soal Generated", len(gq)), ("Evidence", len(ev)), ("Rata-rata Evaluasi", "-" if sc is None or pd.isna(sc) else f"{sc:.1f}")]): col.metric(l, v)
    if mats.empty: st.info("Dataset belum tersedia. Unggah dataset di menu Dataset & Validasi.")
    g = st.columns(2)
    if len(mats): g[0].plotly_chart(px.bar(mats.topik.value_counts().reset_index(), x="topik", y="count", title="Materi per Topik", color_discrete_sequence=["#2563EB"]), use_container_width=True)
    if len(refs): g[1].plotly_chart(px.pie(refs, names="Tingkat Kesulitan", title="Soal Referensi per Kesulitan"), use_container_width=True)
    if len(gq):
        gq["topik"] = gq.data_json.map(lambda x: json.loads(x)["topik"]); gq["tgl"] = gq.created_at.str[:10]
        h = st.columns(2)
        h[0].plotly_chart(px.bar(gq.topik.value_counts().reset_index(), x="topik", y="count", title="Soal Generate per Topik", color_discrete_sequence=["#38BDF8"]), use_container_width=True)
        h[1].plotly_chart(px.line(gq.groupby("tgl").size().reset_index(name="n"), x="tgl", y="n", title="Aktivitas Generate", markers=True), use_container_width=True)
    if len(gq) and gq.evaluation_score.notna().any():
        bins = pd.cut(gq.evaluation_score.dropna(), [-1, 59.9, 79.9, 100], labels=["Tidak Valid", "Perlu Revisi", "Valid"]).value_counts().reset_index()
        st.plotly_chart(px.pie(bins, names="evaluation_score", values="count", hole=.6, title="Distribusi Hasil Evaluasi Kualitas"), use_container_width=True)
    st.subheader("Quick Actions"); qa = st.columns(5)
    for col, (lb, pg) in zip(qa, [("✨ Generate soal", gen_p), ("⬆️ Upload dataset", data_p), ("✔️ Validasi dataset", data_p), ("🔗 Lihat mapping", data_p), ("🏦 Bank soal", bank_p)]): col.button(lb, on_click=go, args=(pg,), use_container_width=True, key="qa" + lb)
    st.subheader("Alur Kerja")
    st.markdown("<div class='flow'>" + "<span>➜</span>".join(f"<b>{x}</b>" for x in ["Dataset Materi", "Soal Referensi", "Mapping", "Evidence (TF-IDF)", "LLM Generation", "Validasi", "Soal Generate", "Evaluasi & Export"]) + "</div>", unsafe_allow_html=True)

def data_page():
    st.title("🗂️ Dataset & Validasi")
    st.caption("Data contoh adalah DATA DEMO, bukan dataset resmi UTBK. Dataset tidak valid tidak boleh dipakai sebelum diperbaiki.")
    tabs = st.tabs(["Materi", "Soal Referensi (22 kolom)", "Mapping Soal–Materi"])
    mats, refs, mp = db.read("materials"), db.load_refs(), db.read("question_material_mapping")
    with tabs[0]:
        f = st.file_uploader("Upload CSV/Excel materi", ["csv", "xlsx"], key="um")
        if f:
            df = load_up(f); st.write("Column mapping ke skema internal:")
            mp_ = {c: st.selectbox(c, df.columns, index=list(df.columns).index(c) if c in df.columns else 0, key="cm"+c) for c in M_COLS}
            df = df[[mp_[c] for c in M_COLS]]; df.columns = M_COLS; s, i = dv.validate_materials(df)
            st.write(f"{s['status']} — {s['persen']}% valid"); st.dataframe(i)
            if st.button("Simpan Materi ke Database", disabled=s["error"] > 0): db.save_materials(df); st.rerun()
        q = st.text_input("Cari materi"); v = mats[mats.apply(lambda r: q.lower() in " ".join(r.astype(str)).lower(), axis=1)] if q else mats
        ed = st.data_editor(v, num_rows="dynamic", use_container_width=True, key="edm")
        if st.button("Simpan perubahan tabel materi"): db.save_materials(ed); st.success("Tersimpan"); st.rerun()
        st.download_button("Template materi", ex.to_csv(pd.read_csv(BASE/"data/template_dataset_materi.csv")), "template_dataset_materi.csv")
    with tabs[1]:
        f = st.file_uploader("Upload CSV/Excel soal referensi", ["csv", "xlsx"], key="uq")
        if f:
            df = load_up(f); s, i = dv.validate_questions(df); st.write(f"{s['status']} — {s['persen']}% valid"); st.dataframe(i)
            if st.button("Simpan Soal Referensi", disabled=s["error"] > 0): db.save_refs(df); st.rerun()
        st.dataframe(refs, use_container_width=True); st.download_button("Template soal (22 kolom)", ex.to_csv(pd.read_csv(BASE/"data/template_dataset_soal.csv")), "template_dataset_soal.csv")
    with tabs[2]:
        f = st.file_uploader("Upload CSV/Excel mapping", ["csv", "xlsx"], key="ump")
        if f:
            df = load_up(f); s, i = dv.validate_mapping(df, mats.materi_id, refs["Kode Soal"] if len(refs) else []); st.write(f"{s['status']} — {s['persen']}% valid"); st.dataframe(i)
            if st.button("Simpan Mapping", disabled=s["error"] > 0): db.save_mapping(df); st.rerun()
        st.markdown("#### Mapping Manager")
        with st.form("addmap", clear_on_submit=True):
            a, b_, c_ = st.columns(3); ks = a.selectbox("Kode soal", refs["Kode Soal"].tolist() if len(refs) else []); ms = b_.multiselect("Materi", mats.materi_id.tolist()); kt = c_.selectbox("Kategori literasi", CATEGORIES)
            if st.form_submit_button("Tambah mapping") and ks and ms: db.save_mapping(pd.concat([mp[MAP_COLS], pd.DataFrame([[ks, m, kt] for m in ms], columns=MAP_COLS)])); st.rerun()
        ed = st.data_editor(mp[MAP_COLS] if len(mp) else pd.DataFrame(columns=MAP_COLS), num_rows="dynamic", use_container_width=True, key="edmap")
        s, i = dv.validate_mapping(ed, mats.materi_id, refs["Kode Soal"] if len(refs) else []); st.write(f"Status: **{s['status']}** · {s['persen']}% valid")
        if len(i): st.dataframe(i)
        if st.button("Simpan perubahan mapping", disabled=s["error"] > 0): db.save_mapping(ed); st.rerun()
        for k_, grp in mp.groupby("kode_soal"): st.code(k_ + "\n" + "\n".join(("└── " if j == len(grp) - 1 else "├── ") + f"{r.materi_id} ({r.topik})" for j, r in enumerate(grp.itertuples())))
        st.download_button("Template mapping", ex.to_csv(pd.read_csv(BASE/"data/template_mapping_soal_materi.csv")), "template_mapping_soal_materi.csv")
    st.divider(); st.subheader("Validasi Terpadu")
    if st.button("Jalankan validasi 3 dataset"):
        allr = []
        for nm, (s, i) in {"Materi": dv.validate_materials(mats), "Soal": dv.validate_questions(refs) if len(refs) else ({"status": "Tidak Valid", "total": 0, "valid": 0, "tidak_valid": 0, "error": 0, "warning": 0, "persen": 0}, pd.DataFrame()),
                           "Mapping": dv.validate_mapping(mp, mats.materi_id, refs["Kode Soal"] if len(refs) else [])}.items():
            st.markdown(f"**{nm}** {badge(s['status'], stat(s))} baris {s['total']}, valid {s['valid']}, error {s['error']}, warning {s['warning']}, {s['persen']}%", unsafe_allow_html=True)
            st.progress(s["persen"] / 100)
            if len(i): i.insert(0, "Dataset", nm); st.dataframe(i); allr.append(i)
        if allr:
            rep = pd.concat(allr); st.download_button("Laporan validasi CSV", ex.to_csv(rep), "laporan_validasi.csv"); st.download_button("Laporan validasi Excel", ex.to_xlsx(rep), "laporan_validasi.xlsx")

def show_evidence(ev, q):
    for r in ev.itertuples():
        with st.expander(f"{r.evidence_id} — {r.judul_materi} (skor {r.skor:.3f}, {r.metode})"):
            st.caption(f"{r.topik} / {r.subtopik} · {r.sumber}"); st.markdown(ee.highlight(r.isi_materi, q))
    st.caption("Skor retrieval = kemiripan teks, bukan ukuran kebenaran evidence.")

def generate_page():
    st.title("✨ Generate Soal")
    mats, refs, mp = db.read("materials"), db.load_refs(), db.read("question_material_mapping")
    if mats.empty: st.warning("Unggah dataset materi dahulu."); return
    L, R = st.columns([1, 2])
    with L:
        topik = st.selectbox("Topik", TOPICS); sub = st.selectbox("Subtopik", ["(semua)"] + sorted(mats[mats.topik == topik].subtopik.unique()))
        kat = st.selectbox("Kategori literasi", TOPIC_CATEGORY[topik]); n = st.slider("Jumlah soal", 1, 10, 3); diff = st.selectbox("Tingkat kesulitan", DIFFICULTY, 1)
        meth = st.radio("Metode retrieval", ["TF-IDF", "Keyword Matching"]); k = st.slider("Jumlah evidence", 1, 5, 3)
        src = st.selectbox("Sumber materi", ["Semua materi (per topik)", "Materi hasil mapping referensi"]); kom = st.text_input("Kompetensi yang diuji", f"{kat} — {topik}")
        use_ref = st.checkbox("Gunakan soal referensi sebagai gaya", True)
        prov = st.selectbox("Provider", ["OpenAI", "Gemini"]); model = st.text_input("Model", "gpt-4o-mini" if prov == "OpenAI" else "gemini-1.5-flash")
        demo = st.checkbox("Mode demo (tanpa API)", not llm.available(prov)); go_ = st.button("Generate Soal", type="primary")
    with R:
        if go_:
            ids = None; rq = refs[refs.Topik == topik] if len(refs) else refs
            if src.startswith("Materi hasil") and len(rq): ids = mp[mp.kode_soal.isin(rq["Kode Soal"])].materi_id.unique().tolist()
            query = f"{topik} {kat} {kom} " + (sub if sub != "(semua)" else "")
            if sub != "(semua)": mats_f = mats[mats.subtopik == sub]
            else: mats_f = mats
            ev = ee.retrieve(mats_f, query, topik, meth, k, ids)
            gid = f"G-{pd.Timestamp.now():%Y%m%d%H%M%S}"
            if len(ev): st.subheader("Evidence"); show_evidence(ev, query)
            status, qs, msg, mode = qg.generate(ev, rq if use_ref else None, n, topik, kat, diff, kom, prov, model, demo)
            db.execute("INSERT INTO generation_history(generation_id,params_json,status,message,n_questions) VALUES(?,?,?,?,?)", (gid, json.dumps({"topik": topik, "kat": kat, "n": n, "diff": diff, "metode": meth, "mode": mode}), status, msg, len(qs)))
            if status != "success": st.error(msg)
            else:
                for q in qs:
                    qid = db.execute("INSERT INTO generated_questions(generation_id,kode_soal,data_json,retrieval_method,reference_question_ids,mode) VALUES(?,?,?,?,?,?)",
                                     (gid, f"{gid}-{q['kode_soal']}", json.dumps({**q, "kategori": kat}, ensure_ascii=False), meth, ",".join(rq["Kode Soal"]) if use_ref and len(rq) else "", mode))
                    sc = ev.set_index("materi_id").skor.to_dict()
                    for e in q["evidence"]: db.execute("INSERT INTO generated_question_evidence(question_id,evidence_id,evidence_text,evidence_score) VALUES(?,?,?,?)", (qid, e["materi_id"], e["kutipan"], float(sc.get(e["materi_id"], 0))))
                st.success(f"{len(qs)} soal dibuat ({msg}) dan disimpan. Status: Belum Diverifikasi."); st.session_state["last"] = gid
        gid = st.session_state.get("last")
        if gid:
            for _, r in db.read("generated_questions").query("generation_id==@gid").iterrows(): render_q(r)

def render_q(r):
    q = json.loads(r.data_json)
    st.markdown(f"<div class='card'><b>{r.kode_soal}</b> {badge(r.validation_status,'#F59E0B')} {badge('DEMO','#64748B') if r['mode']=='demo' else ''}<br><span class='qchip'>{q['topik']}</span><span class='qchip'>{q.get('kategori','-')}</span><span class='qchip'>{q['tingkat_kesulitan']}</span></div>", unsafe_allow_html=True)
    st.write(q["teks_soal"])
    for x in "ABCDE": st.markdown(f"<div class='opt'><span class='ltr'>{x}</span><span>{q['opsi'][x]}</span></div>", unsafe_allow_html=True)
    c = st.columns(3)
    if c[0].toggle("Hint", key=f"h{r.id}"): st.info(q["hint"])
    if c[1].toggle("Kunci & Pembahasan", key=f"k{r.id}"): st.success(f"Kunci: {q['kunci_jawaban']}"); st.write(q["pembahasan"])
    if c[2].toggle("Evidence", key=f"e{r.id}"):
        for e in db.read("generated_question_evidence").query("question_id==@r.id").itertuples(): st.caption(f"{e.evidence_id} (skor {e.evidence_score:.3f}): {e.evidence_text}")

def explorer_page():
    st.title("🔎 Evidence Explorer")
    mats = db.read("materials"); q = st.text_input("Query"); t = st.selectbox("Topik", ["(semua)"] + TOPICS); k = st.slider("Top-K", 1, 10, 5)
    if q and len(mats):
        c = st.columns(2)
        for col, m in zip(c, ["TF-IDF", "Keyword Matching"]):
            with col:
                st.subheader(m); ev = ee.retrieve(mats, q, None if t == "(semua)" else t, m, k)
                if len(ev): show_evidence(ev, q)
                else: st.info("Tidak ada hasil")

def bank_page():
    st.title("🏦 Bank Soal Hasil Generate")
    g = db.read("generated_questions")
    if g.empty: st.info("Belum ada soal."); return
    g["topik"] = g.data_json.map(lambda x: json.loads(x)["topik"]); f = st.selectbox("Filter topik", ["(semua)"] + TOPICS)
    if f != "(semua)": g = g[g.topik == f]
    rows = [qg.to_22({**json.loads(r.data_json), "kode_soal": r.kode_soal}) for r in g.itertuples()]; df = pd.DataFrame(rows, columns=Q_COLS)
    st.dataframe(df, use_container_width=True); st.caption("Format export mengikuti 22 kolom data dictionary.")
    c = st.columns(4); nk = df.drop(columns=["Kunci Jawaban", "Pembahasan", "Hint"])
    c[0].download_button("CSV", ex.to_csv(df), "soal_generate.csv"); c[1].download_button("JSON", ex.to_json(df), "soal_generate.json")
    c[2].download_button("Excel", ex.to_xlsx(df), "soal_generate.xlsx"); c[3].download_button("CSV tanpa kunci", ex.to_csv(nk), "soal_tanpa_kunci.csv")
    st.divider()
    for r in g.itertuples():
        with st.expander(r.kode_soal):
            row = db.read("generated_questions").query("id==@r.id").iloc[0]; render_q(row); q = json.loads(row.data_json)
            with st.form(f"ed{r.id}"):
                tq = st.text_area("Teks soal", q["teks_soal"]); ops = {x: st.text_input(f"Opsi {x}", q["opsi"][x]) for x in "ABCDE"}
                kj = st.selectbox("Kunci", list("ABCDE"), "ABCDE".index(q["kunci_jawaban"])); hn = st.text_input("Hint", q["hint"]); pb = st.text_area("Pembahasan", q["pembahasan"])
                if st.form_submit_button("Simpan Edit"):
                    q.update(teks_soal=tq, opsi=ops, kunci_jawaban=kj, hint=hn, pembahasan=pb)
                    db.execute("UPDATE generated_questions SET data_json=?, validation_status='Belum Diverifikasi', evaluation_score=NULL WHERE id=?", (json.dumps(q, ensure_ascii=False), int(r.id))); st.rerun()
    d = st.selectbox("Hapus soal", [""] + g.id.tolist())
    if d and st.button("Hapus"): db.execute("DELETE FROM generated_questions WHERE id=?", (int(d),)); st.rerun()

def history_page():
    st.title("🕑 Riwayat Generate"); st.dataframe(db.read("generation_history"), use_container_width=True)
def settings_page():
    st.title("⚙️ Pengaturan")
    for p, k in [("OpenAI", "OPENAI_API_KEY"), ("Gemini", "GEMINI_API_KEY")]: st.write(f"{p}: {llm.mask(llm.key(k))} — {'✅ tersedia' if llm.available(p) else '❌ belum diatur'}")
    st.caption("Atur API key lewat .env atau st.secrets.")
    if st.checkbox("Saya yakin ingin reset database") and st.button("Reset database"): DB_PATH.unlink(missing_ok=True); db.init_db(); st.success("Database direset")


from modules import evaluation as evl
def eval_page():
    st.title("✅ Evaluasi & Review Soal"); g = db.read("generated_questions"); mats = db.read("materials"); refs = db.load_refs()
    if g.empty: st.info("Belum ada soal untuk dievaluasi."); return
    rt = refs["Teks Soal"].tolist() if len(refs) else []
    if st.button("Evaluasi otomatis semua soal", type="primary"):
        for r in g.itertuples():
            res = evl.evaluate(json.loads(r.data_json), mats, rt); db.execute("UPDATE generated_questions SET evaluation_score=? WHERE id=?", (res["overall"], r.id))
            db.execute("DELETE FROM evaluation_results WHERE question_id=?", (r.id,)); db.execute("INSERT INTO evaluation_results(question_id,overall,detail_json) VALUES(?,?,?)", (r.id, res["overall"], json.dumps(res, ensure_ascii=False)))
        st.rerun()
    st.caption("Skor otomatis bukan jaminan kunci jawaban benar. Status final ditentukan reviewer manual di bawah.")
    ev = db.read("evaluation_results").set_index("question_id")
    for r in g.itertuples():
        q = json.loads(r.data_json); sc = r.evaluation_score
        with st.expander(f"{r.kode_soal} · skor {'-' if pd.isna(sc) else sc} · {r.validation_status}"):
            st.write(q["teks_soal"][:300])
            if r.id in ev.index:
                d = json.loads(ev.loc[r.id, "detail_json"]); st.plotly_chart(px.bar(x=list(d["aspects"].values()), y=list(d["aspects"]), orientation="h", range_x=[0, 100], color_discrete_sequence=["#2563EB"]), use_container_width=True)
                for n in d["notes"]: st.warning(n)
                st.caption(d["saran"])
            ns = st.selectbox("Status manual", ["Belum Diverifikasi", "Valid", "Perlu Revisi", "Tidak Valid"], ["Belum Diverifikasi", "Valid", "Perlu Revisi", "Tidak Valid"].index(r.validation_status), key=f"vs{r.id}")
            if st.button("Simpan status", key=f"sv{r.id}"): db.execute("UPDATE generated_questions SET validation_status=? WHERE id=?", (ns, r.id)); st.rerun()

def practice_page():
    st.title("🎯 Latihan Mandiri"); g = db.read("generated_questions")
    if g.empty: st.info("Generate soal dulu agar bisa dipakai latihan."); return
    g["topik"] = g.data_json.map(lambda x: json.loads(x)["topik"]); c = st.columns(3)
    t = c[0].selectbox("Topik", ["(semua)"] + TOPICS); pool = g if t == "(semua)" else g[g.topik == t]; n = c[1].slider("Jumlah soal", 1, max(len(pool), 1), min(5, max(len(pool), 1)))
    if c[2].button("Mulai Latihan", type="primary", disabled=pool.empty): st.session_state.ps = pool.sample(n).id.tolist(); st.session_state.pdone = False
    ids = st.session_state.get("ps")
    if not ids: return
    qs = {r.id: (r, json.loads(r.data_json)) for r in g.itertuples() if r.id in ids}; done = st.session_state.get("pdone")
    with st.form("latihan"):
        ans = {}
        for i, qid in enumerate(ids, 1):
            r, q = qs[qid]; st.markdown(f"**Soal {i}** · {q['topik']}"); st.write(q["teks_soal"])
            ans[qid] = st.radio("Jawaban", list("ABCDE"), index=None, format_func=lambda x, q=q: f"{x}. {q['opsi'][x]}", key=f"pa{qid}", disabled=done, label_visibility="collapsed")
        sub = st.form_submit_button("Kumpulkan Jawaban", disabled=done)
    st.progress(sum(v is not None for v in ans.values()) / len(ids), text="Progress pengerjaan")
    if sub:
        st.session_state.pdone = True; res = [(qs[i][1]["topik"], ans[i] == qs[i][1]["kunci_jawaban"]) for i in ids]
        sid = db.execute("INSERT INTO practice_sessions(topik,score) VALUES(?,?)", (t, 100 * sum(c for _, c in res) / len(ids)))
        for i in ids: db.execute("INSERT INTO practice_answers(session_id,question_id,answer,correct) VALUES(?,?,?,?)", (sid, i, ans[i], int(ans[i] == qs[i][1]["kunci_jawaban"])))
        st.session_state.pres = res; st.session_state.pans = ans; st.rerun()
    if done and "pres" in st.session_state:
        res = st.session_state.pres; b = sum(c for _, c in res); m = st.columns(3)
        m[0].metric("Skor", f"{100*b/len(res):.0f}"); m[1].metric("Benar", b); m[2].metric("Salah", len(res) - b)
        df = pd.DataFrame(res, columns=["Topik", "Benar"]).groupby("Topik").Benar.mean().mul(100).reset_index(); st.plotly_chart(px.bar(df, x="Topik", y="Benar", title="Performa per Topik (%)", range_y=[0, 100]), use_container_width=True)
        for i in ids:
            r, q = qs[i]; ok = st.session_state.pans[i] == q["kunci_jawaban"]; st.markdown(f"{'✅' if ok else '❌'} **{r.kode_soal}** · kunci {q['kunci_jawaban']}")
            st.caption(q["pembahasan"])
            for e in db.read("generated_question_evidence").query("question_id==@i").itertuples(): st.caption(f"Evidence {e.evidence_id}: {e.evidence_text}")

TIPS = {
 "Dashboard": ("Ringkasan seluruh aplikasi: kondisi data dan aktivitas generate.", [
  ("Hero & 3 tombol", "Pintu masuk cepat: mulai generate, kelola dataset, atau lihat evidence."),
  ("6 kartu angka", "Jumlah materi, soal referensi, mapping, soal hasil generate, evidence, dan rata-rata skor evaluasi. Semua dihitung dari database, bukan angka palsu."),
  ("Grafik materi per topik", "Mengecek apakah materi tiap topik cukup merata. Topik yang materinya sedikit akan menghasilkan soal yang kurang bervariasi."),
  ("Grafik kesulitan soal referensi", "Menunjukkan sebaran Mudah/Sedang/Sulit pada contoh gaya soal."),
  ("Grafik soal generate & aktivitas", "Memantau topik apa saja yang sudah digenerate dan kapan."),
  ("Alur kerja", "Urutan proses sistem dari data sampai ekspor.")]),
 "Generate Soal": ("Tempat membuat soal baru berbasis evidence.", [
  ("Topik / Subtopik / Kategori", "Menentukan materi apa yang dicari dan kompetensi literasi yang diuji. Kategori literasi berbeda dari topik soal."),
  ("Jumlah soal & Kesulitan", "Berapa soal (1-10) dan tingkat kesulitannya."),
  ("Metode retrieval", "TF-IDF mencari materi paling mirip secara bobot kata. Keyword Matching hanya menghitung kata yang sama."),
  ("Jumlah evidence", "Berapa potongan materi teratas yang dipakai sebagai dasar fakta soal."),
  ("Sumber materi", "'Semua materi' = cari di seluruh topik. 'Hasil mapping' = hanya materi yang terhubung ke soal referensi."),
  ("Soal referensi sebagai gaya", "Contoh soal dipakai untuk meniru format, bukan disalin dan bukan sumber fakta."),
  ("Mode demo", "Dipakai jika API key belum ada. Soal disusun dari kalimat evidence, bukan oleh LLM."),
  ("Kartu soal", "Hint, kunci, pembahasan, dan evidence disembunyikan dulu. Status 'Belum Diverifikasi' berarti belum dicek guru.")]),
 "Dataset & Validasi": ("Mengelola tiga dataset dan memeriksa kualitasnya.", [
  ("Tab Materi", "Sumber evidence. Bisa upload, memetakan kolom yang namanya berbeda, mencari, dan mengedit."),
  ("Tab Soal Referensi", "Contoh soal 22 kolom sebagai acuan gaya. Bukan sumber fakta."),
  ("Tab Mapping", "Penghubung kode_soal, materi_id, dan kategori literasi."),
  ("Tombol Simpan", "Nonaktif selama masih ada error validasi, supaya data rusak tidak dipakai."),
  ("Validasi Terpadu", "Memeriksa ketiga dataset sekaligus. Hasilnya bisa diunduh sebagai laporan CSV/Excel.")]),
 "Evidence Explorer": ("Melihat cara sistem memilih materi, tanpa membuat soal.", [
  ("Query & Topik", "Kata yang dicari dan batas topiknya."),
  ("Top-K", "Jumlah hasil teratas yang ditampilkan."),
  ("Dua kolom", "TF-IDF dan Keyword Matching dibandingkan berdampingan."),
  ("Skor & teks tebal", "Skor adalah kemiripan teks, bukan bukti kebenaran. Kata yang cocok ditebalkan.")]),
 "Bank Soal Generate": ("Semua soal hasil generate yang tersimpan.", [
  ("Tabel 22 kolom", "Formatnya sama dengan dataset referensi, tetapi disimpan terpisah darinya."),
  ("Tombol unduh", "CSV, JSON, Excel, atau CSV tanpa kunci jawaban untuk dibagikan ke siswa."),
  ("Hapus soal", "Menghapus soal beserta evidence-nya.")]),
 "Riwayat Generate": ("Catatan setiap percobaan generate.", [
  ("Status & pesan", "success, insufficient_evidence, atau failed beserta alasannya, termasuk mode demo atau LLM.")]),
 "Evaluasi & Review": ("Menilai kualitas soal dan menetapkan status akhir.", [
  ("Evaluasi otomatis", "Menghitung skor 6 aspek: Evidence 30%, Konsistensi Jawaban 25%, Kejelasan 15%, Kualitas Opsi 15%, Topik 10%, Kesulitan 5%."),
  ("Grafik & catatan", "Menunjukkan aspek yang lemah dan alasan pengurangan skor."),
  ("Status manual", "Guru menentukan Valid/Perlu Revisi/Tidak Valid. Skor otomatis tidak menggantikan pemeriksaan manusia.")]),
 "Latihan Mandiri": ("Siswa mengerjakan soal yang sudah digenerate.", [
  ("Mulai Latihan", "Memilih topik dan jumlah soal secara acak dari bank soal."),
  ("Kumpulkan", "Kunci baru terbuka setelah jawaban dikumpulkan."),
  ("Hasil", "Skor, benar/salah, performa per topik, pembahasan, dan evidence.")]),
 "Pengaturan": ("Status API dan reset data.", [
  ("Status API", "Key hanya tampil sebagian. Atur lewat .env atau st.secrets."),
  ("Reset database", "Menghapus semua data. Perlu dicentang dulu sebagai konfirmasi.")])}
def tip(key):
    if st.session_state.get("tutor_on", True):
        d, items = TIPS[key]
        with st.expander(f"💡 Live Tutor: fungsi halaman {key}", expanded=False):
            st.write(d)
            for a, b in items: st.markdown(f"- **{a}**: {b}")
def wrap(fn, key):
    def f(): tip(key); fn()
    f.__name__ = fn.__name__; return f
def tutor_page():
    st.title("🎓 Live Tutor")
    st.write("Panduan langkah demi langkah. Pilih halaman, lalu baca fungsi tiap bagiannya.")
    k = st.selectbox("Halaman", list(TIPS)); d, items = TIPS[k]; st.info(d)
    n = st.session_state.setdefault("tstep", 0) % len(items); c = st.columns(3)
    if c[0].button("⬅ Sebelumnya"): st.session_state.tstep = n - 1; st.rerun()
    if c[2].button("Berikutnya ➡"): st.session_state.tstep = n + 1; st.rerun()
    a, b = items[n]; c[1].caption(f"Langkah {n+1}/{len(items)}")
    st.markdown(f"<div class='card'><h4>{a}</h4>{b}</div>", unsafe_allow_html=True)
    st.subheader("Alur pemakaian pertama kali")
    st.markdown("1. **Dataset & Validasi**: cek data, jalankan validasi.\n2. **Evidence Explorer**: coba cari materi.\n3. **Generate Soal**: pilih topik, klik Generate.\n4. **Bank Soal Generate**: tinjau dan unduh.\n5. Guru memeriksa kunci jawaban secara manual.")
    st.checkbox("Tampilkan kotak Live Tutor di setiap halaman", True, key="tutor_on")

dash_p = st.Page(wrap(dashboard, "Dashboard"), title="Dashboard", icon="📊", default=True, url_path="dashboard"); gen_p = st.Page(wrap(generate_page, "Generate Soal"), title="Generate Soal", icon="✨", url_path="generate")
data_p = st.Page(wrap(data_page, "Dataset & Validasi"), title="Dataset & Validasi", icon="🗂️", url_path="dataset"); expl_p = st.Page(wrap(explorer_page, "Evidence Explorer"), title="Evidence Explorer", icon="🔎", url_path="evidence")
bank_p = st.Page(wrap(bank_page, "Bank Soal Generate"), title="Bank Soal Generate", icon="🏦", url_path="bank")
nav = st.navigation([dash_p, gen_p, data_p, expl_p, bank_p,
  st.Page(wrap(history_page, "Riwayat Generate"), title="Riwayat Generate", icon="🕑", url_path="riwayat"), st.Page(wrap(settings_page, "Pengaturan"), title="Pengaturan", icon="⚙️", url_path="settings"),
  st.Page(wrap(eval_page, "Evaluasi & Review"), title="Evaluasi & Review", icon="✅", url_path="evaluasi"), st.Page(wrap(practice_page, "Latihan Mandiri"), title="Latihan Mandiri", icon="🎯", url_path="latihan"),
  st.Page(tutor_page, title="Live Tutor", icon="🎓", url_path="tutor")])
with st.sidebar:
    st.markdown("### 📘 UTBK Literasi Generator\n*Generate Smarter Questions. Learn with Evidence.*"); st.caption("v1.1 · DB: ✅ SQLite"); st.caption(f"API LLM: {'✅' if llm.available('OpenAI') or llm.available('Gemini') else '⚠️ mode demo'}")
nav.run()
