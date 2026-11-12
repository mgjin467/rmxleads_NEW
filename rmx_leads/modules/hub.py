\
import logging, requests, os
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential_jitter
from config import CFG
from utils import clean_text

# 참고: 실제 엔드포인트/파라미터는 최신 문서 확인 필요
# 여기서는 대표 엔드포인트 예시와 덤프파일(월 CSV/XLSX) 대체 로직을 모두 제공

@retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(1,5))
def hub_api_call(path: str, params: dict):
    url = f"{CFG.HUB_API_BASE}/{path}"
    params = dict(params)
    params["serviceKey"] = CFG.HUB_SERVICE_KEY
    params["_type"] = "json"
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_permits_api(start_date: str, end_date: str, sigungu_cd: str = ""):
    """
    건축허가 개요 API 예시:
    - path 예시: getApBasisOulnInfo  (허가 개요)
    - 파라미터 예시: sigunguCd, bdnm, useAprDay 등
    ※ 실제 파라미터/필드명은 문서 확인 후 맞추세요.
    """
    try:
        js = hub_api_call("getApBasisOulnInfo", {
            "pageNo": 1,
            "numOfRows": 200,
            "sigunguCd": sigungu_cd,
            "startDate": start_date.replace("-",""),
            "endDate": end_date.replace("-",""),
        })
        body = js.get("response",{}).get("body",{})
        items = body.get("items",{}).get("item",[])
        if isinstance(items, dict):
            items = [items]
        out = []
        for it in items:
            addr = clean_text(it.get("platPlc",""))  # 대지위치
            nm   = clean_text(it.get("bldNm",""))
            use  = clean_text(it.get("mainPurps",""))
            area = it.get("totArea","")
            perm = clean_text(it.get("pmsDay",""))
            out.append({
                "id": clean_text(it.get("mgmPmsrgstPk","") or f"{perm}_{nm}_{addr}"),
                "source": "HUB",
                "title": nm or f"건축허가({use})",
                "org": clean_text(it.get("ownerNm","") or it.get("applcntNm","") or ""),
                "stage": "건축허가",
                "date_key": perm,  # 허가일
                "address": addr,
                "link": "",  # 필요 시 건축물대장 뷰어 링크 조립
                "tot_area": area,
                "use": use
            })
        return out
    except Exception as e:
        logging.warning(f"HUB API 실패/스킵: {e}")
        return []

def fetch_permits_dump(files: list):
    """
    HUB 대용량 덤프 파일(CSV/XLSX)에서 필드 맵핑.
    """
    out = []
    for p in files:
        if not os.path.exists(p):
            logging.warning(f"HUB 덤프 파일 없음: {p}")
            continue
        try:
            if p.lower().endswith(".csv"):
                df = pd.read_csv(p, encoding="utf-8")
            else:
                df = pd.read_excel(p)
        except Exception:
            df = pd.read_csv(p, encoding="cp949", errors="ignore")
        for _, r in df.iterrows():
            addr = clean_text(str(r.get("대지위치") or r.get("platPlc") or ""))
            nm   = clean_text(str(r.get("건물명") or r.get("bldNm") or ""))
            use  = clean_text(str(r.get("주용도") or r.get("mainPurps") or ""))
            area = r.get("연면적") or r.get("totArea") or ""
            perm = clean_text(str(r.get("허가일") or r.get("pmsDay") or ""))
            pk   = clean_text(str(r.get("허가번호") or r.get("mgmPmsrgstPk") or ""))
            out.append({
                "id": pk or f"{perm}_{nm}_{addr}",
                "source": "HUB",
                "title": nm or f"건축허가({use})",
                "org": clean_text(str(r.get("시행자명") or r.get("ownerNm") or r.get("applcntNm") or "")),
                "stage": "건축허가",
                "date_key": perm,
                "address": addr,
                "link": "",
                "tot_area": area,
                "use": use
            })
    return out

def get_permits(start_date: str, end_date: str, sigungu_cd: str = ""):
    rows = []
    if CFG.HUB_SERVICE_KEY:
        rows.extend(fetch_permits_api(start_date, end_date, sigungu_cd))
    if CFG.HUB_DUMP_FILES:
        rows.extend(fetch_permits_dump(CFG.HUB_DUMP_FILES))
    if not rows:
        logging.info("HUB: 가져올 데이터 없음(키/덤프 미설정)")
    return rows
