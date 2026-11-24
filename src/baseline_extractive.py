"""Baseline ekstraktif berbasis TF-IDF untuk AI Smart Learning Assistant.

Input utama mengikuti struktur JSON keluaran notebooks/09_chunking.ipynb.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Daftar awal kata umum Bahasa Indonesia. Daftar ini dapat diperluas setelah evaluasi.
INDONESIAN_STOPWORDS = {
    "yang", "dan", "di", "ke", "dari", "pada", "dengan", "untuk", "dalam",
    "adalah", "ialah", "yaitu", "atau", "serta", "karena", "sehingga",
    "agar", "maka", "jika", "apabila", "ketika", "saat", "oleh", "sebagai",
    "terhadap", "antara", "dapat", "akan", "telah", "sudah", "belum",
    "tidak", "bukan", "juga", "lebih", "paling", "sangat", "hanya",
    "secara", "merupakan", "menjadi", "yakni", "ini", "itu", "tersebut",
    "ada", "y ang", "para", "suatu", "setiap", "beberapa", "seluruh",
    "berbagai", "sebuah", "d yaitu", "pun", "nya", "ia", "mereka",
    "kita", "kami", "anda", "saya", "aku", "dia", "d an"
}

def load_p09_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Ambil kalimat unik dari chunks P09, menghilangkan duplikasi overlap."""
    if not isinstance(payload, dict) or not isinstance(payload.get("chunks"), list):
        raise ValueError("Format input tidak sesuai. JSON harus memiliki key 'chunks'.")

    records = []
    seen = set()
    for chunk in payload["chunks"]:
        details = chunk.get("sentences_detail", [])
        if not isinstance(details, list):
            continue
        for item in details:
            text = re.sub(r"\s+", " ", str(item.get("text", ""))).strip()
            fragment_id = str(item.get("fragment_id") or item.get("sentence_id") or "")
            if not text or not fragment_id or fragment_id in seen:
                continue
            seen.add(fragment_id)
            records.append({
                "fragment_id": fragment_id,
                "sentence_id": str(item.get("sentence_id") or item.get("source_sentence_id") or ""),
                "page": item.get("page"),
                "paragraph_id": item.get("paragraph_id"),
                "text": text,
            })

    if not records:
        raise ValueError(
            "Tidak ditemukan sentences_detail pada file P09. "
            "Pastikan file berasal dari notebook 09_chunking.ipynb versi repository ini."
        )
    return records

def rank_sentences(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Skor relevansi kalimat terhadap centroid TF-IDF dokumen."""
    texts = [r["text"] for r in records]
    if len(texts) == 1:
        return [{**records[0], "tfidf_score": 1.0}]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True,
        stop_words=list(INDONESIAN_STOPWORDS),
        token_pattern=r"(?u)\b[a-zA-ZÀ-ÿ][a-zA-ZÀ-ÿ]+\b",
    )
    try:
        matrix = vectorizer.fit_transform(texts)
    except ValueError:
        # Fallback jika seluruh teks tersaring atau tidak memiliki token valid.
        return [{**r, "tfidf_score": 0.0} for r in records]

    centroid = __import__("numpy").asarray(matrix.mean(axis=0))
    scores = cosine_similarity(matrix, centroid).ravel()
    ranked = [{**r, "tfidf_score": float(score)} for r, score in zip(records, scores)]
    return ranked

def build_extractive_summary(
    records: list[dict[str, Any]],
    max_words: int = 150,
) -> dict[str, Any]:
    """Pilih kalimat dengan skor tertinggi hingga batas kata, lalu urutkan kembali."""
    if max_words < 1:
        raise ValueError("max_words harus lebih besar dari 0.")

    ranked = rank_sentences(records)
    selected = []
    used_words = 0

    # Ranking skor tertinggi; tie-break mempertahankan urutan sumber.
    candidates = sorted(
        enumerate(ranked),
        key=lambda pair: (-pair[1]["tfidf_score"], pair[0])
    )

    for original_index, item in candidates:
        word_count = len(item["text"].split())
        if not selected and word_count > max_words:
            # Jangan menghasilkan ringkasan kosong hanya karena satu kalimat panjang.
            selected.append((original_index, item))
            used_words += word_count
            break
        if used_words + word_count <= max_words:
            selected.append((original_index, item))
            used_words += word_count

    selected.sort(key=lambda pair: pair[0])
    selected_records = [item for _, item in selected]
    summary_text = " ".join(item["text"] for item in selected_records)

    return {
        "summary": summary_text,
        "max_words": max_words,
        "actual_words": len(summary_text.split()),
        "selected_sentence_count": len(selected_records),
        "source_sentences": selected_records,
        "all_sentence_scores": [
            {
                "fragment_id": item["fragment_id"],
                "page": item.get("page"),
                "tfidf_score": item["tfidf_score"],
                "selected": item in selected_records,
                "text": item["text"],
            }
            for item in ranked
        ],
    }

def run_baseline(input_json: str | Path, output_json: str | Path, max_words: int = 150):
    """Jalankan baseline dari satu file JSON P09 dan simpan hasil JSON."""
    input_json = Path(input_json)
    output_json = Path(output_json)
    payload = json.loads(input_json.read_text(encoding="utf-8"))
    records = load_p09_records(payload)
    result = build_extractive_summary(records, max_words=max_words)

    metadata = payload.get("pipeline_metadata", {})
    output = {
        "method": "TF-IDF extractive baseline",
        "source_file": metadata.get("source_file", input_json.name),
        "tokenizer_model_from_p09": metadata.get("tokenizer_model"),
        "input_chunk_count": len(payload.get("chunks", [])),
        "unique_source_units": len(records),
        **result,
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return output
