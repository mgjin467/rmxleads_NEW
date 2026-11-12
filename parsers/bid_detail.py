\
import re
from bs4 import BeautifulSoup

ADDRESS_HINTS = [
    "현장주소","공사현장","공사장소","위치","대지위치","사업장소","사업위치","건설위치"
]

ADDR_REGEX = re.compile(r"([가-힣A-Za-z0-9\-\s]+(시|군|구)\s*[가-힣A-Za-z0-9\-\s]*(읍|면|동)?\s*[가-힣A-Za-z0-9\-\s]*(로|길)\s*\d+[^\s<]*)")

def extract_address_from_detail(html: str):
    """
    1) 라벨 기반(현장주소/공사장소 등) td/strong 텍스트 이웃 추출
    2) 전체 텍스트에서 주소 패턴 정규식 후보 추출
    """
    soup = BeautifulSoup(html, "lxml")

    # 1) 표 형태 라벨 탐색
    text = soup.get_text(" ", strip=True)
    # 우선 라벨-값 패턴 파악
    for hint in ADDRESS_HINTS:
        # hint 주변 50~150자 크롭
        idx = text.find(hint)
        if idx != -1:
            segment = text[max(0, idx-50): idx+150]
            m = ADDR_REGEX.search(segment)
            if m:
                return m.group(0)

    # 2) 전체 텍스트에서 주소 패턴
    m2 = ADDR_REGEX.search(text)
    if m2:
        return m2.group(0)

    # 3) a 태그 title/href에 포함된 경우
    for a in soup.select("a"):
        t = (a.get_text(" ", strip=True) or "") + " " + (a.get("title") or "") + " " + (a.get("href") or "")
        m3 = ADDR_REGEX.search(t)
        if m3:
            return m3.group(0)

    return None
