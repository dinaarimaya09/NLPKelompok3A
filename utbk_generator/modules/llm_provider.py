import os, requests
def key(name):
    v = os.getenv(name)
    if not v:
        try:
            import streamlit as st; v = st.secrets.get(name)
        except Exception: v = None
    return v
def available(provider): return bool(key("OPENAI_API_KEY" if provider == "OpenAI" else "GEMINI_API_KEY"))
def mask(k): return (k[:4] + "…" + k[-2:]) if k and len(k) > 8 else "(belum diatur)"
def call_llm(provider, model, system, user):
    if provider == "OpenAI":
        r = requests.post("https://api.openai.com/v1/chat/completions", timeout=90, headers={"Authorization": f"Bearer {key('OPENAI_API_KEY')}"},
            json={"model": model, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
        r.raise_for_status(); return r.json()["choices"][0]["message"]["content"]
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key('GEMINI_API_KEY')}", timeout=90,
        json={"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"parts": [{"text": user}]}], "generationConfig": {"responseMimeType": "application/json"}})
    r.raise_for_status(); return r.json()["candidates"][0]["content"]["parts"][0]["text"]
