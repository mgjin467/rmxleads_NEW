import os, json, logging
from datetime import datetime, timedelta

from config import CFG
from utils import setup_logging, haversine_km, now_dates
from geocode import kakao_geocode
from scoring import est_concrete_by_keywords, lead_score
from modules.narajangteo import get_bids
from sheet import HEADERS_AGG

CACHE_PATH = os.path.join(os.path.dirname(__file__), "data", "leads_cache.json")

def main():
    setup_logging()
    today, yesterday = now_dates()
    start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    logging.info(f"수집 기간: {start} ~ {end}")

    bids = get_bids(start, end, CFG.REGION_KEYWORD)
    logging.info(f"나라장터 수집: {len(bids)}건")

    rows = []
    for b in bids:
        title = b["title"]
        addr  = b.get("address") or b["org"] or title
        lat, lon = kakao_geocode(addr)
        if not lat:
            continue
        dist = haversine_km(CFG.PLANT_LAT, CFG.PLANT_LON, lat, lon)
        if dist > CFG.SEARCH_RADIUS_KM:
            continue

        est = est_concrete_by_keywords(title)
        try:
            dday = (datetime.strptime(b.get("date_key",""), "%Y-%m-%d").date() - today).days
        except:
            dday = 15

        score = lead_score(dist, est, dday, CFG.SEARCH_RADIUS_KM)
        row = dict(zip(HEADERS_AGG, [
            b["id"], b["source"], title, b["org"], b["stage"], b.get("date_key",""),
            addr, lat, lon, round(dist,2), round(est,1), score, b.get("link",""), today.isoformat()
        ]))
        rows.append(row)

    logging.info(f"반경 {CFG.SEARCH_RADIUS_KM}km 이내 리드: {len(rows)}건")

    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

    # 기존 캐시와 병합 (id 중복 제거)
    existing = []
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    existing_ids = {r.get("id") for r in existing}
    new_rows = [r for r in rows if r.get("id") not in existing_ids]
    merged = new_rows + existing

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    logging.info(f"신규 {len(new_rows)}건 저장 완료 → {CACHE_PATH}")

if __name__ == "__main__":
    main()
