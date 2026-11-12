\
import requests, logging, time, re
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential_jitter
from bs4 import BeautifulSoup
from config import CFG
from utils import clean_text
from parsers.bid_detail import extract_address_from_detail

NARA_LIST_URL = "https://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoCnstwk"

@retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(1,5))
def fetch_list(start_date: str, end_date: str, page_no: int = 1):
    # 날짜 형식: YYYYMMDDHHMM (12자리)
    bgnDt = start_date.replace("-","") + "0000"
    endDt = end_date.replace("-","") + "2359"
    params = {
        "serviceKey": CFG.DATAGOKR_SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": CFG.NARA_ROWS_PER_PAGE,
        "inqryDiv": "1",
        "inqryBgnDt": bgnDt,
        "inqryEndDt": endDt,
        "type": "json"
    }
    r = requests.get(NARA_LIST_URL, params=params, timeout=20)
    r.raise_for_status()
    js = r.json()
    body = js.get("response",{}).get("body",{})
    total = int(body.get("totalCount",0))
    raw = body.get("items", [])
    if isinstance(raw, dict):
        items = raw.get("item", [])
        if isinstance(items, dict): items = [items]
    elif isinstance(raw, list):
        items = raw
    else:
        items = []
    return total, items

def get_bids(start_date: str, end_date: str, region_regex: str = ""):
    if not CFG.DATAGOKR_SERVICE_KEY:
        logging.warning("DATAGOKR_SERVICE_KEY 미설정 → 나라장터 모듈 스킵")
        return []

    total, items = fetch_list(start_date, end_date, 1)
    all_items = items[:]
    page = 1
    while len(all_items) < total:
        page += 1
        _, more = fetch_list(start_date, end_date, page)
        all_items.extend(more)
        time.sleep(0.2)

    leads = []
    for it in all_items:
        title = clean_text(it.get("bidNtceNm",""))
        org   = clean_text(it.get("ntceInsttNm",""))
        no    = str(it.get("bidNtceNo",""))
        seq   = str(it.get("bidNtceOrd",""))
        close = clean_text((it.get("bidClseDt","") or "")[:10])
        link  = clean_text(it.get("bidNtceDtlUrl",""))
        # API에서 직접 제공하는 공사현장지역명 사용 (상세페이지 크롤링 불필요)
        addr  = clean_text(it.get("cnstrtsiteRgnNm","")) or org

        if region_regex:
            if not re.search(region_regex, f"{title} {org} {addr}"):
                continue

        leads.append({
            "id": f"{no}-{seq}",
            "source": "NARA",
            "title": title,
            "org": org,
            "stage": "입찰공고",
            "date_key": close or "",
            "address": addr,
            "link": link
        })
    return leads
