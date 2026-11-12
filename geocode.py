\
import requests, logging
from tenacity import retry, stop_after_attempt, wait_exponential_jitter
from config import CFG

@retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(1,5))
def kakao_geocode(addr: str):
    if not CFG.KAKAO_REST_API_KEY:
        return None, None
    headers = {"Authorization": f"KakaoAK {CFG.KAKAO_REST_API_KEY}"}
    r = requests.get("https://dapi.kakao.com/v2/local/search/address.json",
                     headers=headers, params={"query": addr}, timeout=10)
    r.raise_for_status()
    docs = r.json().get("documents", [])
    if not docs: 
        return None, None
    x, y = float(docs[0]["x"]), float(docs[0]["y"])
    return y, x
