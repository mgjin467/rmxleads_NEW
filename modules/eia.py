\
import logging, requests
from utils import clean_text

def get_eia_by_api(base_url: str, service_key: str, start_date: str, end_date: str):
    """
    환경영향평가 API 호출 예시(실제 엔드포인트/파라미터는 최신 문서 참고).
    """
    if not (base_url and service_key):
        return []
    try:
        # 예시 쿼리(필드명은 문서 확인 후 수정)
        params = {
            "serviceKey": service_key,
            "pageNo": 1,
            "numOfRows": 200,
            "startDt": start_date.replace("-",""),
            "endDt": end_date.replace("-",""),
            "_type": "json"
        }
        r = requests.get(f"{base_url}/getProjectList", params=params, timeout=30)
        r.raise_for_status()
        js = r.json()
        items = (js.get("response",{}).get("body",{}).get("items",{}) or {}).get("item",[])
        if isinstance(items, dict): items = [items]
        out = []
        for it in items:
            name = clean_text(it.get("prjctNm","") or it.get("bizNm",""))
            step = clean_text(it.get("prgrsStepNm","") or it.get("step",""))
            addr = clean_text(it.get("adres","") or it.get("loc",""))
            date = clean_text(it.get("rcptDt","") or it.get("updDt",""))
            link = ""  # 상세링크가 제공되면 사용
            out.append({
                "id": clean_text(it.get("bizNo","") or f"{name}_{date}_{addr}"),
                "source": "EIA",
                "title": name or "환경영향평가",
                "org": clean_text(it.get("cnstrctnEntrpsNm","") or it.get("instNm","")),
                "stage": step or "EIA",
                "date_key": date,
                "address": addr,
                "link": link
            })
        return out
    except Exception as e:
        logging.warning(f"EIA API 실패/스킵: {e}")
        return []

def get_eia_by_scrape(search_url: str):
    """
    검색 페이지 목록 스크랩(사이트 구조에 맞게 커스터마이즈 필요)
    """
    if not search_url: return []
    out = []
    try:
        r = requests.get(search_url, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        # TODO: 실제 선택자 맞춤 필요. 여기서는 placeholder.
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        for row in soup.select("table tbody tr"):
            t = clean_text(row.get_text(" ", strip=True))
            a = row.select_one("a")
            link = a.get("href") if a else ""
            out.append({
                "id": clean_text(f"{search_url}_{t}"),
                "source": "EIA",
                "title": t[:50],
                "org": "EIA",
                "stage": "EIA",
                "date_key": "",
                "address": "",
                "link": link
            })
    except Exception as e:
        logging.warning(f"EIA 스크랩 실패: {e}")
    return out

def get_eia(start_date: str, end_date: str, api_base: str, service_key: str, search_url: str):
    rows = []
    rows.extend(get_eia_by_api(api_base, service_key, start_date, end_date))
    if not rows:
        rows.extend(get_eia_by_scrape(search_url))
    return rows
