\
import os, logging
from datetime import datetime, timedelta
import pandas as pd

from config import CFG
from utils import setup_logging, haversine_km, now_dates
from geocode import kakao_geocode
from scoring import est_concrete_by_keywords, lead_score
from sheet import open_ws, upsert, HEADERS_AGG
from modules.narajangteo import get_bids

def main():
    setup_logging()
    today, yesterday = now_dates()
    start_date = (yesterday).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    bids = get_bids(start_date, end_date, CFG.REGION_KEYWORD)

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
        # dday 추정: 마감일이 있으면 계산
        try:
            dday = (datetime.strptime(b.get("date_key",""), "%Y-%m-%d").date() - today).days
        except:
            dday = 15

        score = lead_score(dist, est, dday, CFG.SEARCH_RADIUS_KM)
        rows.append([
            b["id"], b["source"], title, b["org"], b["stage"], b.get("date_key",""),
            addr, lat, lon, round(dist,2), round(est,1), score, b.get("link",""), today.isoformat()
        ])

    if not rows:
        logging.info("최소가동: 신규 리드 없음")
        return

    ws = open_ws(CFG.WS_AGG, HEADERS_AGG)
    new_count = upsert(ws, HEADERS_AGG, rows)
    logging.info(f"신규 {new_count}건 추가 완료")

if __name__ == "__main__":
    main()
