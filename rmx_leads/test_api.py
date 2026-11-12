import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from config import CFG
from modules.narajangteo import get_bids
from utils import now_dates
from datetime import timedelta

today, yesterday = now_dates()
start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
end = today.strftime("%Y-%m-%d")
print("기간:", start, "~", end)
print("키워드:", CFG.REGION_KEYWORD)
bids = get_bids(start, end, CFG.REGION_KEYWORD)
print("수집 결과:", len(bids), "건")
for b in bids[:10]:
    print(" -", b["title"], "/", b["org"])
