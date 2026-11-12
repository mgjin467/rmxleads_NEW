\
import logging, requests, yaml
from bs4 import BeautifulSoup
from utils import clean_text

def load_sites(yaml_path: str):
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            y = yaml.safe_load(f)
        return y.get("sites",[])
    except Exception as e:
        logging.warning(f"NOTICE config 로드 실패: {e}")
        return []

def scrape_site(site: dict):
    url = site.get("list_url")
    item_sel = site.get("item_selector")
    title_sel = site.get("title_selector")
    date_sel = site.get("date_selector")
    href_attr = site.get("href_attr","href")
    absolute = site.get("absolute_href", True)
    include_kw = site.get("include_keywords", [])

    rows = []
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        for tr in soup.select(item_sel):
            a = tr.select_one(title_sel)
            if not a: 
                continue
            title = clean_text(a.get_text(" ", strip=True))
            if include_kw and not any(k in title for k in include_kw):
                continue
            link = a.get(href_attr,"")
            if link and not link.startswith("http") and absolute:
                from urllib.parse import urljoin
                link = urljoin(url, link)
            date = ""
            if date_sel:
                d = tr.select_one(date_sel)
                if d:
                    date = clean_text(d.get_text(" ", strip=True))
            rows.append({
                "id": clean_text(f"{url}_{title}_{date}"),
                "source": "NOTICE",
                "title": title,
                "org": site.get("name","지자체"),
                "stage": "고시공고",
                "date_key": date,
                "address": "",   # 상세페이지에서 주소 파싱을 추가 구현 가능
                "link": link
            })
    except Exception as e:
        logging.warning(f"NOTICE 스크랩 실패({url}): {e}")
    return rows

def get_notices(yaml_path: str):
    out = []
    for site in load_sites(yaml_path):
        out.extend(scrape_site(site))
    return out
