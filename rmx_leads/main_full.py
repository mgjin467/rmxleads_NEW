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
from modules.hub import get_permits
from modules.notices import get_notices
from modules.eia import get_eia

def normalize_to_rows(items, today_str: str):
    rows = []
    for r in items:
        title = r.get("title","")
        addr  = r.get("address") or r.get("org") or title
        lat, lon = kakao_geocode(addr)
        if not lat:
            continue
        dist = haversine_km(CFG.PLANT_LAT, CFG.PLANT_LON, lat, lon)
        if dist > CFG.SEARCH_RADIUS_KM:
            continue

        est = est_concrete_by_keywords(title)
        # D-day: date_key가 있으면 계산
        try:
            dday = (datetime.strptime(r.get("date_key",""), "%Y-%m-%d").date() - datetime.now().date()).days
        except:
            dday = 15

        score = lead_score(dist, est, dday, CFG.SEARCH_RADIUS_KM)
        rows.append([
            r.get("id",""), r.get("source",""), title, r.get("org",""), r.get("stage",""),
            r.get("date_key",""), addr, lat, lon, round(dist,2), round(est,1), score, r.get("link",""), today_str
        ])
    return rows

def main():
    setup_logging()
    today, yesterday = now_dates()
    start_date = (yesterday).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    today_str = today.isoformat()

    # === 수집 ===
    nara = get_bids(start_date, end_date, CFG.REGION_KEYWORD)
    hub  = get_permits(start_date, end_date, sigungu_cd="")
    notice = get_notices(CFG.NOTICE_SITES_CONFIG)
    eia = get_eia(start_date, end_date, CFG.EIA_API_BASE, CFG.EIA_SERVICE_KEY, CFG.EIA_SEARCH_URL)

    logging.info(f"수집 결과: NARA {len(nara)}, HUB {len(hub)}, NOTICE {len(notice)}, EIA {len(eia)}")

    # === 시트별 저장(원천) ===
    ws_nara = open_ws(CFG.WS_NARA, HEADERS_AGG)
    ws_hub  = open_ws(CFG.WS_HUB, HEADERS_AGG)
    ws_no   = open_ws(CFG.WS_NOTICE, HEADERS_AGG)
    ws_eia  = open_ws(CFG.WS_EIA, HEADERS_AGG)
    ws_agg  = open_ws(CFG.WS_AGG, HEADERS_AGG)

    rows_nara = normalize_to_rows(nara, today_str)
    rows_hub  = normalize_to_rows(hub,  today_str)
    rows_no   = normalize_to_rows(notice, today_str)
    rows_eia  = normalize_to_rows(eia, today_str)

    new_nara = upsert(ws_nara, HEADERS_AGG, rows_nara)
    new_hub  = upsert(ws_hub,  HEADERS_AGG, rows_hub)
    new_no   = upsert(ws_no,   HEADERS_AGG, rows_no)
    new_eia  = upsert(ws_eia,  HEADERS_AGG, rows_eia)

    # === 종합시트에도 추가 ===
    new_agg = upsert(ws_agg, HEADERS_AGG, rows_nara + rows_hub + rows_no + rows_eia)

    logging.info(f"업서트 완료: NARA {new_nara}, HUB {new_hub}, NOTICE {new_no}, EIA {new_eia}, AGG {new_agg}")

if __name__ == "__main__":
    main()
