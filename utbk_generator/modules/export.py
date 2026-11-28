import io, json, pandas as pd
from config import Q_COLS
def to_csv(df): return df.to_csv(index=False).encode("utf-8-sig")
def to_json(df): return df.to_json(orient="records", force_ascii=False, indent=2).encode()
def to_xlsx(df):
    b = io.BytesIO(); df.to_excel(b, index=False, engine="openpyxl"); return b.getvalue()
