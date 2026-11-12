import os, json, logging
from datetime import datetime, timedelta

from config import CFG
from utils import haversine_km, now_dates
from geocode import kakao_geocode
from scoring import est_concrete_by_keywords, lead_score
from modules.narajangteo import get_bids
from sheet import HEADERS_AGG

CACHE_PATH = os.path.join(os.path.dirname(__file__), "data", "leads_cache.json")

_status = {"running": False, "msg": "대기 중", "last": None}


def get_status():
    return dict(_status)


def _matches(text, keywords, mode):
    if not keywords:
        return True
    t = text.lower()
    if mode == "AND":
        return all(k.lower() in t for k in keywords)
    return any(k.lower() in t for k in keywords)


def run(settings):
    global _status
    if _status["running"]:
        return False, "이미 실행 중입니다"
    _status = {"running": True, "msg": "시작 중...", "last": None}
    try:
        _execute(settings)
        _status = {"running": False, "msg": "완료", "last": datetime.now().isoformat()}
        return True, "완료"
    except Exception as e:
        logging.exception("파이프라인 오류")
        _status = {"running": False, "msg": f"오류: {e}", "last": datetime.now().isoformat()}
        return False, str(e)


def _execute(settings):
    today, _ = now_dates()
    days_back = int(settings.get("days_back", 30))
    start = (today - timedelta(days=days_back)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")

    plant_lat     = float(settings.get("plant_lat", CFG.PLANT_LAT))
    plant_lon     = float(settings.get("plant_lon", CFG.PLANT_LON))
    radius_km     = float(settings.get("search_radius_km", CFG.SEARCH_RADIUS_KM))
    region_kws    = settings.get("region_keywords", [])
    region_mode   = settings.get("region_mode", "OR")
    content_kws   = settings.get("content_keywords", [])
    content_mode  = settings.get("content_mode", "OR")

    region_regex = "|".join(region_kws) if region_kws else ""

    _status["msg"] = f"나라장터 수집 중... ({start} ~ {end})"
    logging.info(_status["msg"])
    bids = get_bids(start, end, region_regex)
    logging.info(f"수집 완료: {len(bids)}건")

    rows = []
    for i, b in enumerate(bids):
        _status["msg"] = f"지오코딩 중... ({i+1}/{len(bids)})"
        title   = b["title"]
        combined = f"{title} {b.get('org', '')}"

        if content_kws and not _matches(title, content_kws, content_mode):
            continue
        if region_kws and not _matches(combined, region_kws, region_mode):
            continue

        addr = b.get("address") or b.get("org") or title
        lat, lon = kakao_geocode(addr)
        if not lat:
            continue
        dist = haversine_km(plant_lat, plant_lon, lat, lon)
        if dist > radius_km:
            continue

        est = est_concrete_by_keywords(title)
        try:
            dday = (datetime.strptime(b.get("date_key", ""), "%Y-%m-%d").date() - today).days
        except Exception:
            dday = 15

        score = lead_score(dist, est, dday, radius_km)
        rows.append(dict(zip(HEADERS_AGG, [
            b["id"], b["source"], title, b["org"], b["stage"],
            b.get("date_key", ""), addr, lat, lon,
            round(dist, 2), round(est, 1), score, b.get("link", ""), today.isoformat()
        ])))

    logging.info(f"반경 내 리드: {len(rows)}건")
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    logging.info(f"{len(rows)}건 저장 완료")
