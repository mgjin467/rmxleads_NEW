\
import re, math, logging, time, unicodedata
from datetime import datetime, timedelta
from typing import Optional, Iterable

def setup_logging():
    import sys, io
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl   = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

def clean_text(s: str) -> str:
    if s is None: return ""
    s = unicodedata.normalize("NFKC", str(s))
    s = re.sub(r"\s+", " ", s).strip()
    return s

def slug_id(*parts: Iterable[str]) -> str:
    raw = "_".join([clean_text(p) for p in parts if p])
    raw = raw.lower()
    raw = re.sub(r"[^a-z0-9]+","-", raw).strip("-")
    return raw

def parse_yyyymmdd(s: str):
    s = clean_text(s)
    for fmt in ("%Y-%m-%d", "%Y%m%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except:
            continue
    return None

def now_dates():
    today = datetime.now().date()
    return today, today - timedelta(days=1)
