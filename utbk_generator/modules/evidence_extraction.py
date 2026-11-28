import re, numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
STOP = set("yang dan di ke dari untuk pada dengan adalah itu ini atau juga dalam sebagai oleh akan dapat karena tidak ada para agar bahwa serta lebih sebuah suatu satu saat telah sudah mereka kita kami saya".split())
def preprocess(t):
    return " ".join(w for w in re.findall(r"[a-z0-9]+", str(t).lower()) if w not in STOP)
def split_sentences(t): return [s.strip() for s in re.split(r"(?<=[.!?])\s+", str(t)) if s.strip()]
def retrieve(mats, query, topik=None, method="TF-IDF", k=3, ids=None):
    d = mats.copy()
    if ids is not None: d = d[d.materi_id.isin(ids)]
    elif topik: d = d[d.topik == topik]
    if d.empty or not query.strip(): return pd.DataFrame()
    docs = (d.judul_materi + " " + d.kata_kunci.fillna("") + " " + d.isi_materi).map(preprocess).tolist()
    q = preprocess(query)
    if method == "Keyword Matching":
        qs = set(q.split()); sc = np.array([len(qs & set(x.split())) / max(len(qs), 1) for x in docs])
    else:
        v = TfidfVectorizer(); X = v.fit_transform(docs + [q]); sc = cosine_similarity(X[-1], X[:-1])[0]
    d = d.assign(skor=sc, metode=method).sort_values("skor", ascending=False).head(k)
    d["evidence_id"] = "EV-" + d.materi_id
    return d.reset_index(drop=True)
def best_sentence(text, query):
    ss = split_sentences(text); qs = set(preprocess(query).split())
    return max(ss, key=lambda s: len(qs & set(preprocess(s).split()))) if ss else text
def highlight(text, query):
    for w in set(preprocess(query).split()):
        text = re.sub(f"(?i)\\b({re.escape(w)})\\b", r"**\1**", text)
    return text
